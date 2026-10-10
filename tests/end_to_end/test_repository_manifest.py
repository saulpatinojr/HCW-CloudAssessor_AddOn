"""repository.manifest.json lists real files and the packaging scripts honour its excludes."""

import json

from ..conftest import ROOT


def test_manifest_required_files_exist_and_excludes_are_honoured():
    manifest = json.loads((ROOT / "repository.manifest.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "hcw-cloudassessor-addon" and manifest["archive"].endswith(".zip")
    missing = [f for f in manifest["requiredFiles"] if not (ROOT / f).is_file()]
    assert missing == []
    for must in (".venv", ".git", "__pycache__", ".env", "*.zip"):
        assert any(must in e for e in manifest["packageExcludes"]), must
    sh = (ROOT / "scripts" / "package-repository.sh").read_text(encoding="utf-8")
    ps = (ROOT / "scripts" / "package-repository.ps1").read_text(encoding="utf-8")
    for exclude in manifest["packageExcludes"]:
        token = exclude.rstrip("/").lstrip("*")
        assert token in sh, f"package-repository.sh does not exclude {exclude}"
        assert token.replace(".", "\\.") in ps or token in ps, f"package-repository.ps1 does not exclude {exclude}"


def test_manifest_version_matches_pyproject():
    manifest = json.loads((ROOT / "repository.manifest.json").read_text(encoding="utf-8"))
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{manifest["version"]}"' in pyproject
    from cloud_assessment_lab import __version__

    assert __version__ == manifest["version"]
