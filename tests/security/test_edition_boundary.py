"""The lab edition is technically unable to reach Azure (AddOn Integration Standard, section 19)."""

import ast
import re
import shutil
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import cloud_assessor_core
import pytest

from ..conftest import ROOT

FORBIDDEN_PACKAGES = re.compile(r'^(name = "|  )?(azure-|msal|msrest|boto3|botocore)', re.MULTILINE)
FORBIDDEN_ENDPOINTS = ("management.azure.com", "login.microsoftonline.com", "graph.microsoft.com")
FORBIDDEN_MODULES = ("azure", "msal", "boto3", "botocore", "msrest")
SEED = ROOT / "packages" / "cloud-assessor-core"
# Keyed on a tracked file, not the folder: after the bump merges, `git pull` leaves ignored __pycache__ folders behind.
SEEDED = (SEED / "pyproject.toml").is_file()
# The engine is checked wherever it is installed from: the local seed until the first core-update pull request, the
# upstream release wheel (in site-packages) after it. Directories that do not exist are skipped, never an error.
ENGINE_DIR = Path(cloud_assessor_core.__file__).resolve().parent
PY_DIRS = [d for d in (ROOT / "packages", ROOT / "src", ROOT / "scripts", ENGINE_DIR) if d.is_dir()]


def _py_files():
    for base in PY_DIRS:
        yield from (p for p in base.rglob("*.py") if ".venv" not in p.relative_to(base).parts)


def test_the_installed_engine_declares_no_cloud_sdk():
    requires = metadata.requires("cloud-assessor-core") or []
    assert requires, "cloud-assessor-core declares no dependencies at all (expected pydantic)"
    for req in requires:
        name = re.split(r"[\s<>=!~;\[(]", req, maxsplit=1)[0].lower()
        assert not name.startswith(("azure-", "msal", "msrest", "boto3", "botocore")), f"the engine requires {req}"


def test_no_cloud_sdk_in_dependency_manifests():
    names = ["pyproject.toml", "uv.lock"] + (["packages/cloud-assessor-core/pyproject.toml"] if SEEDED else [])
    for name in names:
        text = (ROOT / name).read_text(encoding="utf-8")
        for pkg in ("azure-", "msal", "msrest", "boto3", "botocore"):
            assert not re.search(rf'name = "{pkg}', text), f"{name} depends on {pkg}"
            assert not re.search(rf"^{pkg}[\w-]*==", text, re.MULTILINE), f"{name} pins {pkg}"


def test_no_cloud_sdk_imports_anywhere():
    for path in _py_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                assert name.split(".")[0] not in FORBIDDEN_MODULES, f"{path} imports {name}"


# The engine comes from outside this repository once it is the release wheel, so it is held to pure computation: no
# module that opens a connection. Scoped to the engine only; src/ uses urllib on purpose (human verification).
FORBIDDEN_NETWORK = ("urllib.request", "http.client", "socket", "ssl", "httpx", "requests", "aiohttp")


def _network_imports(base: Path) -> list[str]:
    def forbidden(name: str) -> bool:
        return any(name == f or name.startswith(f + ".") for f in FORBIDDEN_NETWORK)

    found = []
    for path in sorted(base.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module] + [f"{node.module}.{a.name}" for a in node.names]
            elif isinstance(node, ast.Call) and node.args and isinstance(node.args[0], ast.Constant):
                func = node.func
                called = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else ""
                if called in {"__import__", "import_module"} and isinstance(node.args[0].value, str):
                    names = [node.args[0].value]
            found += [f"{path.relative_to(base)}: {n}" for n in names if forbidden(n)]
    return found


def test_the_engine_opens_no_network_connection():
    assert _network_imports(ENGINE_DIR) == []


@pytest.mark.parametrize(
    "source",
    [
        "import socket",
        "from urllib import request",
        "import urllib.request as r",
        "from http.client import HTTPSConnection",
        "import ssl, json",
        "import requests",
        "import httpx",
        "import aiohttp",
        "x = __import__('socket')",
        "import importlib\nimportlib.import_module('http.client')",
    ],
)
def test_the_network_check_catches_an_injected_import(tmp_path, source):
    engine = tmp_path / "cloud_assessor_core"
    shutil.copytree(ENGINE_DIR, engine, ignore=shutil.ignore_patterns("__pycache__"))
    (engine / "paths.py").write_text((engine / "paths.py").read_text(encoding="utf-8") + "\n" + source + "\n")
    assert _network_imports(engine) and all(hit.startswith("paths.py: ") for hit in _network_imports(engine))


def test_the_network_check_leaves_pure_urllib_parse_alone(tmp_path):
    (tmp_path / "m.py").write_text("from urllib.parse import urlsplit\nimport json, re\n")
    assert _network_imports(tmp_path) == []


def test_no_azure_endpoints_in_code_or_pane():
    for base in [d for d in (ROOT / "packages", ROOT / "src", ROOT / "web", ENGINE_DIR) if d.is_dir()]:
        for path in base.rglob("*"):
            if (
                path.is_file()
                and path.suffix in {".py", ".js", ".html", ".css", ".json"}
                and ".venv" not in path.relative_to(base).parts
            ):
                text = path.read_text(encoding="utf-8", errors="ignore")
                for endpoint in FORBIDDEN_ENDPOINTS:
                    assert endpoint not in text, f"{path} references {endpoint}"


def test_guard_refuses_identity_endpoint_in_a_fresh_process():
    proc = subprocess.run(
        [sys.executable, "-c", "import cloud_assessment_lab.app"],
        env={
            "PATH": "/usr/bin:/bin",
            "IDENTITY_ENDPOINT": "http://169.254.169.254/metadata/identity",
            "PYTHONPATH": ":".join(sys.path),
        },
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode != 0


def test_cloud_sdks_not_importable_in_this_environment():
    for module in ("azure", "msal", "boto3"):
        with pytest.raises(ImportError):
            __import__(module)


def test_pane_has_no_credential_inputs():
    for path in (ROOT / "web").glob("*"):
        text = path.read_text(encoding="utf-8")
        assert 'type="password"' not in text and "type='password'" not in text, path
        assert "<input" not in text or 'type="file"' in text, "the only input is the file picker"
    assert "never asks for credentials" in (ROOT / "web" / "index.html").read_text(encoding="utf-8")


def test_dockerfile_and_compose_have_no_azure():
    """Outside comments, the only `azure` in the Dockerfile is the boundary guard's forbidden list."""
    for name in ("infrastructure/docker/Dockerfile", "docker-compose.yml"):
        for line in (ROOT / name).read_text(encoding="utf-8").splitlines():
            code = line.split("#", 1)[0].lower()
            if "azure" in code or "msal" in code or "boto3" in code:
                assert "forbidden" in code or "edition boundary" in code, f"{name}: {line.strip()}"
            assert "pip install" not in code or "requirements.lock.txt" in code, f"{name}: {line.strip()}"
            assert "identity_endpoint=" not in code and "msi_endpoint=" not in code, f"{name}: {line.strip()}"


def test_health_reports_disabled_by_design(client):
    assert client.get("/api/health").json()["azureConnectivity"] == "disabled-by-design"
