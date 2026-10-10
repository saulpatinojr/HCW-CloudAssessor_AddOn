import importlib
import subprocess
import sys

import pytest

from cloud_assessment_lab import edition
from cloud_assessment_lab.edition import (
    AZURE_CONNECTIVITY,
    CAPABILITIES,
    EDITION,
    FORBIDDEN_MODULES,
    IDENTITY_ENV_VARS,
    EditionBoundaryError,
    assert_lab_cannot_reach_azure,
    install_import_guard,
)


def test_constants():
    assert EDITION == "lab" and AZURE_CONNECTIVITY == "disabled-by-design"
    assert "scorecard" in CAPABILITIES and FORBIDDEN_MODULES == ("azure", "msal", "boto3")
    assert set(IDENTITY_ENV_VARS) == {
        "IDENTITY_ENDPOINT",
        "MSI_ENDPOINT",
        "AZURE_CLIENT_SECRET",
        "AZURE_FEDERATED_TOKEN_FILE",
        "AZURE_CLIENT_ID",
        "AZURE_TENANT_ID",
    }


@pytest.mark.parametrize("name", IDENTITY_ENV_VARS)
def test_refuses_identity_environment(name):
    with pytest.raises(EditionBoundaryError, match=name):
        assert_lab_cannot_reach_azure({name: "http://169.254.169.254"})


def test_refuses_when_sdk_importable(monkeypatch):
    monkeypatch.setattr(edition.importlib.util, "find_spec", lambda m: object() if m == "msal" else None)
    monkeypatch.setattr(
        edition.sys, "meta_path", [f for f in sys.meta_path if not isinstance(f, edition._RefuseCloudSdk)]
    )
    with pytest.raises(EditionBoundaryError, match="msal"):
        assert_lab_cannot_reach_azure({})


def test_import_guard_blocks_cloud_sdks_and_is_idempotent():
    install_import_guard()
    install_import_guard()
    assert sum(1 for f in sys.meta_path if isinstance(f, edition._RefuseCloudSdk)) == 1
    for module in ("azure", "azure.identity", "msal", "boto3"):
        with pytest.raises(ImportError):
            importlib.import_module(module)
    assert_lab_cannot_reach_azure({})


def test_app_import_exits_non_zero_under_identity_endpoint():
    proc = subprocess.run(
        [sys.executable, "-c", "import cloud_assessment_lab.app"],
        env={"PATH": "/usr/bin:/bin", "IDENTITY_ENDPOINT": "http://169.254.169.254", "PYTHONPATH": ":".join(sys.path)},
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode != 0 and "EditionBoundaryError" in proc.stderr


def test_main_refuses_with_exit_code_3():
    proc = subprocess.run(
        [sys.executable, "-m", "cloud_assessment_lab"],
        env={"PATH": "/usr/bin:/bin", "MSI_ENDPOINT": "http://169.254.169.254", "PYTHONPATH": ":".join(sys.path)},
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 3 and "startup_refused" in proc.stderr and "169.254" not in proc.stderr
