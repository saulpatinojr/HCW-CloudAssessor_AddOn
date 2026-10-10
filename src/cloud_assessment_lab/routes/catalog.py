"""GET /api/catalog: the criteria the pane lists (texts, remediation, links; never the evaluator internals)."""

from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/api/catalog")
async def catalog(request: Request) -> dict:
    cat = request.app.state.catalog
    return {
        "version": cat.version,
        "retrievedOn": cat.retrievedOn,
        "count": len(cat.criteria),
        "attribution": list(cat.attribution),
        "criteria": [
            {
                "id": c.id,
                "framework": c.framework,
                "pillar": c.pillar,
                "severity": c.severity,
                "resourceTypes": list(c.resourceTypes),
                "title": c.title,
                "text": c.text,
                "remediation": c.remediation,
                "learnUrl": c.learnUrl,
                "verify": c.verify,
                "retrievedOn": c.retrievedOn,
                "checks": [{"kind": k.kind} for k in c.checks],
                "anyPass": c.anyPass,
            }
            for c in cat.criteria
        ],
    }
