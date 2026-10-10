"""POST/GET/DELETE /api/assessments: the only mutating surface, gated by human verification and the limits."""

from __future__ import annotations

import json
import re
import time
from datetime import timedelta
from typing import Any, Literal

from cloud_assessor_core.assess import assess
from cloud_assessor_core.ingestion import IngestionError, normalize, parse_arg_csv, parse_arg_json
from cloud_assessor_core.ingestion.arg_json import TooManyRows, parse_arg_document
from cloud_assessor_core.report import BUNDLE_FILES, make_bundle, zip_bytes
from fastapi import APIRouter, Request, Response
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from cloud_assessment_lab.errors import ApiError
from cloud_assessment_lab.security.limits import client_address, read_body
from cloud_assessment_lab.security.logging import log_event
from cloud_assessment_lab.security.turnstile import verify

router = APIRouter()

FILE_NAME = re.compile(r"^[\w .()-]{1,120}\.(json|csv)$")
CONTENT_TYPES = {"md": "text/markdown; charset=utf-8", "json": "application/json", "csv": "text/csv; charset=utf-8"}


class Options(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weights: dict[str, dict[str, float]] | None = None


class CreateAssessmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    format: Literal["arg-json", "arg-csv"]
    content: str = Field(min_length=1)
    fileName: str | None = Field(default=None, pattern=FILE_NAME.pattern)
    options: Options | None = None


def _owner_token(request: Request) -> str | None:
    token = request.headers.get("x-owner-token", "").strip()
    return token if 0 < len(token) <= 128 else None


def _expires_at(state, assessment) -> str:
    return (assessment.created_at + timedelta(minutes=state.settings.ttl_minutes)).isoformat().replace("+00:00", "Z")


def _scorecards(assessment) -> list[dict[str, Any]]:
    return [c.model_dump(by_alias=True) for c in assessment.scorecards]


def _parse_upload(body: bytes, content_type: str, max_rows: int) -> tuple[str, Any, str | None, dict | None]:
    """Returns (format, parsed_rows, file_name, weights)."""
    if content_type.startswith("text/csv"):
        text = body.decode("utf-8", errors="replace")
        return "arg-csv", parse_arg_csv(text, max_rows=max_rows), None, None
    try:
        document = json.loads(body.decode("utf-8"))
    except UnicodeDecodeError, json.JSONDecodeError:
        raise ApiError(400, "invalid_json", "The body is not valid JSON.") from None
    if isinstance(document, dict) and "format" in document and "data" not in document:
        try:
            wrapper = CreateAssessmentRequest.model_validate(document)
        except ValidationError as exc:
            fields = sorted({".".join(str(p) for p in e["loc"]) for e in exc.errors()})
            raise ApiError(400, "invalid_request", "The request shape is not valid.", {"fields": fields}) from None
        weights = wrapper.options.weights if wrapper.options else None
        if wrapper.format == "arg-csv":
            return "arg-csv", parse_arg_csv(wrapper.content, max_rows=max_rows), wrapper.fileName, weights
        return "arg-json", parse_arg_json(wrapper.content, max_rows=max_rows), wrapper.fileName, weights
    return "arg-json", parse_arg_document(document, max_rows=max_rows), None, None


@router.post("/api/assessments", status_code=201)
async def create_assessment(request: Request) -> Response:
    state = request.app.state
    settings = state.settings
    started = time.monotonic()

    allowed, retry_after = state.limiter.acquire(client_address(request, settings.trust_proxy))
    if not allowed:
        log_event("rate_limited", retryAfter=retry_after)
        raise ApiError(
            429,
            "rate_limited",
            "Too many uploads from this client; try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    content_type = request.headers.get("content-type", "").split(";")[0].strip().lower()
    if content_type not in ("application/json", "text/csv"):
        raise ApiError(415, "unsupported_media_type", "Send application/json or text/csv.")

    if settings.turnstile_required:
        verdict = verify(
            settings.turnstile_secret or "",
            request.headers.get("x-turnstile-token"),
            client_address(request, settings.trust_proxy),
            opener=state.verifier,
        )
        if not verdict.ok:
            log_event("turnstile_rejected", codes=len(verdict.codes))
            raise ApiError(403, "turnstile_failed", "Human verification did not succeed.", {"codes": verdict.codes})
        log_event("turnstile_verified")
    elif settings.turnstile_enforced:
        raise ApiError(
            503, "turnstile_not_configured", "Uploads are not available until human verification is configured."
        )

    body = await read_body(request, settings.max_upload_bytes)
    try:
        fmt, parsed, file_name, weights = _parse_upload(body, content_type, settings.max_rows)
        resources, warnings = normalize(parsed, fmt)
    except TooManyRows as exc:
        log_event("assessment_rejected", code="too_many_rows", rows=exc.count)
        raise ApiError(
            422,
            "too_many_rows",
            "The export has more rows than the limit.",
            {"rows": exc.count, "maxRows": exc.max_rows},
        ) from None
    except IngestionError as exc:
        log_event("assessment_rejected", code="ingestion_failed", warnings=len(exc.warnings))
        raise ApiError(
            422,
            "ingestion_failed",
            "The export could not be read.",
            {"reason": str(exc), "warnings": exc.warnings[:50]},
        ) from None

    if not await state.bound.acquire():
        log_event("busy")
        raise ApiError(503, "busy", "The service is busy; try again shortly.", headers={"Retry-After": "2"})
    try:
        assessment = assess(
            resources,
            state.catalog,
            state.scoring,
            source_format=fmt,
            file_name=file_name,
            ingestion_warnings=warnings,
            weights=weights,
        )
        files = make_bundle(assessment, state.catalog)
        files["bundle.zip"] = zip_bytes(files)
    finally:
        state.bound.release()

    stored = state.store.put(assessment, files)
    log_event(
        "assessment_created",
        format=fmt,
        resources=len(resources),
        findings=len(assessment.findings),
        warnings=len(warnings),
        durationMs=int((time.monotonic() - started) * 1000),
        stored=state.store.size,
    )
    payload = {
        "assessmentId": stored.id,
        "ownerToken": stored.owner_token,
        "expiresAt": _expires_at(state, assessment),
        "summary": assessment.summary.model_dump(by_alias=True),
        "scorecards": _scorecards(assessment),
        "ingestionWarnings": warnings,
    }
    return Response(json.dumps(payload), status_code=201, media_type="application/json")


def _load(request: Request, assessment_id: str):
    entry = request.app.state.store.get(assessment_id, _owner_token(request))
    if entry is None:
        raise ApiError(404, "not_found", "Not found.")
    return entry


@router.get("/api/assessments/{assessment_id}")
async def get_assessment(request: Request, assessment_id: str) -> Response:
    assessment, files = _load(request, assessment_id)
    log_event("assessment_read")
    body = {
        "assessment": assessment.model_dump(mode="json", by_alias=True),
        "files": sorted(files),
        "expiresAt": _expires_at(request.app.state, assessment),
    }
    return Response(json.dumps(body), media_type="application/json")


@router.get("/api/assessments/{assessment_id}/report.md")
async def get_report_md(request: Request, assessment_id: str) -> Response:
    _, files = _load(request, assessment_id)
    return Response(
        files["report.md"],
        media_type=CONTENT_TYPES["md"],
        headers={"Content-Disposition": f'attachment; filename="assessment-{assessment_id[:8]}.md"'},
    )


@router.get("/api/assessments/{assessment_id}/report.json")
async def get_report_json(request: Request, assessment_id: str) -> Response:
    _, files = _load(request, assessment_id)
    return Response(files["report.json"], media_type="application/json")


@router.get("/api/assessments/{assessment_id}/bundle.zip")
async def get_bundle(request: Request, assessment_id: str) -> Response:
    _, files = _load(request, assessment_id)
    return Response(
        files["bundle.zip"],
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="assessment-{assessment_id[:8]}.zip"'},
    )


@router.get("/api/assessments/{assessment_id}/files/{path:path}")
async def get_file(request: Request, assessment_id: str, path: str) -> Response:
    _, files = _load(request, assessment_id)
    if path not in BUNDLE_FILES or path not in files:
        raise ApiError(404, "not_found", "Not found.")
    return Response(files[path], media_type=CONTENT_TYPES[path.rsplit(".", 1)[-1]])


@router.delete("/api/assessments/{assessment_id}")
async def delete_assessment(request: Request, assessment_id: str) -> dict:
    if not request.app.state.store.delete(assessment_id, _owner_token(request)):
        raise ApiError(404, "not_found", "Not found.")
    log_event("assessment_deleted", stored=request.app.state.store.size)
    return {"deleted": True}
