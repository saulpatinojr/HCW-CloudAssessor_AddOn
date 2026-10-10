"""GET /api/config: public widget settings for the pane."""

from __future__ import annotations

from fastapi import APIRouter, Request

from cloud_assessment_lab.config import TURNSTILE_ACTION

router = APIRouter()


@router.get("/api/config")
async def config(request: Request) -> dict:
    state = request.app.state
    settings = state.settings
    return {
        "turnstileSiteKey": settings.turnstile_site_key,
        "turnstileRequired": settings.turnstile_enforced,
        "turnstileAction": TURNSTILE_ACTION,
        "limits": {"maxUploadBytes": settings.max_upload_bytes, "maxRows": settings.max_rows},
        "ttlMinutes": settings.ttl_minutes,
        "frameworks": [{"id": fw, "label": spec.label} for fw, spec in state.scoring.frameworks.items()],
        "siteOrigins": list(settings.site_origins),
    }
