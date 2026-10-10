"""docs/api/openapi.yaml and the implementation agree two-way: every documented path+method exists and vice versa."""

import re
from pathlib import Path

from cloud_assessment_lab.app import api_routes, create_app

from ..conftest import ROOT, make_settings

SPEC = Path(ROOT / "docs" / "api" / "openapi.yaml").read_text(encoding="utf-8")


def _spec_routes() -> dict[str, set[str]]:
    routes: dict[str, set[str]] = {}
    current = None
    for line in SPEC.splitlines():
        m = re.match(r"^  (/api/\S+):\s*$", line)
        if m:
            current = m.group(1)
            routes[current] = set()
            continue
        m = re.match(r"^    (get|post|put|patch|delete):\s*$", line)
        if m and current:
            routes[current].add(m.group(1).upper())
    return routes


def _normalise(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "{}", path)


def test_openapi_paths_and_methods_match_app_both_ways():
    spec = {_normalise(p): m for p, m in _spec_routes().items()}
    app = {_normalise(p): m for p, m in api_routes(create_app(make_settings(), sweep=False)).items()}
    assert spec, "spec parsed no paths"
    assert set(spec) == set(app), f"spec-only: {set(spec) - set(app)}; app-only: {set(app) - set(spec)}"
    for path in spec:
        assert spec[path] == app[path], f"{path}: spec {spec[path]} vs app {app[path]}"


def test_spec_documents_every_error_code_the_api_emits():
    src = "".join(p.read_text(encoding="utf-8") for p in (ROOT / "src" / "cloud_assessment_lab").rglob("*.py"))
    for code in sorted(set(re.findall(r'ApiError\(\d{3}, "([a-z_]+)"', src)) - {"forbidden"}):
        assert code in SPEC, f"error code {code} is not documented"
    assert "turnstile_not_configured" in SPEC and "not_found" in SPEC and "rate_limited" in SPEC
