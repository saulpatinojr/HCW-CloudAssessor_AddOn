"""Switch the engine from the local seed to an upstream release wheel (the first adoption, run by core-update.yml).

Until the first adoption, the engine `cloud-assessor-core` is the seed under packages/cloud-assessor-core, a uv
workspace member, and the dependency line in pyproject.toml carries the marker `CORE_REF v<seed version>-seed`.
core-update.yml reads that marker, sees an upstream release that is newer, and runs this script, which rewrites the
files that name the seed so the engine comes from the release wheel instead:

- pyproject.toml: the dependency line becomes the wheel's URL with the marker `CORE_REF <tag>` (the one-line form the
  later bumps of core-update.yml move); the `[tool.uv]` workspace and the `[tool.uv.sources]` entry for the seed go,
  and the seed leaves `testpaths` and the coverage `source`.
- infrastructure/docker/Dockerfile: the two COPY lines that place the seed go; the wheel, hash-checked through
  `uv export`, carries the engine and its catalog (`cloud_assessor_core/catalog_data`).
- .dockerignore: the line for the seed's tests goes.

Every edit is an exact match of the text as it stands; when one does not match, the script changes nothing and exits 1,
so the run fails before a half-edited pull request can be opened. The workflow then deletes the seed with `git rm -r`
(staged, so the bump pull request carries the deletion) and runs `uv lock`, which downloads the wheel and records its
sha256. This script never touches the network and never edits uv.lock.

Usage: python scripts/adopt_core_wheel.py --tag v0.2.1 [--root <repository root>] [--wheel-url <url>]
  --wheel-url   override the wheel's URL (local trials only; the workflow never passes it).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

UPSTREAM = "saulpatinojr/HCW-CloudAssessor_App"
TAG = re.compile(r"^v(\d+\.\d+\.\d+)$")
# The seed line and the comment lines right above it; both are replaced, so no comment about the seed is left behind.
SEED_LINE = re.compile(r'(?m)^(?:  #.*\n)*  "cloud-assessor-core",  # CORE_REF v\d+\.\d+\.\d+-seed\b.*$')
WHEEL_COMMENT = (
    "  # The engine: the upstream release wheel, by URL (uv.lock holds its sha256). core-update.yml moves this line\n"
    "  # to each newer release and re-locks; do not edit it by hand.\n"
)

PYPROJECT_REMOVALS = (
    '[tool.uv]\nworkspace = { members = ["packages/cloud-assessor-core"] }\n\n',
    "[tool.uv.sources]\ncloud-assessor-core = { workspace = true }\n\n",
)
PYPROJECT_REPLACEMENTS = (
    ('testpaths = ["tests", "packages/cloud-assessor-core/tests"]', 'testpaths = ["tests"]'),
    ('source = ["packages/cloud-assessor-core/src", "src"]', 'source = ["src"]'),
)
SITE = "/install/lib/python3.14/site-packages"
DOCKERFILE_REMOVALS = (
    f"COPY packages/cloud-assessor-core/src/cloud_assessor_core {SITE}/cloud_assessor_core\n",
    f"COPY packages/cloud-assessor-core/catalog {SITE}/cloud_assessor_core/catalog_data\n",
)
DOCKERIGNORE_REMOVALS = ("packages/cloud-assessor-core/tests\n",)


class AdoptionError(RuntimeError):
    """A file did not look as expected; nothing was written."""


def wheel_url(tag: str) -> str:
    match = TAG.fullmatch(tag)
    if not match:
        raise AdoptionError(f"tag {tag!r} is not v<major>.<minor>.<patch>")
    version = match.group(1)
    return f"https://github.com/{UPSTREAM}/releases/download/{tag}/cloud_assessor_core-{version}-py3-none-any.whl"


def _remove(text: str, needle: str, name: str) -> str:
    if text.count(needle) != 1:
        raise AdoptionError(f"{name}: expected exactly one {needle.strip()!r}")
    return text.replace(needle, "", 1)


def adopt_pyproject(text: str, tag: str, url: str) -> str:
    if len(SEED_LINE.findall(text)) != 1:
        raise AdoptionError("pyproject.toml: expected exactly one seed line with a CORE_REF v<version>-seed marker")
    text = SEED_LINE.sub(lambda _: f'{WHEEL_COMMENT}  "cloud-assessor-core @ {url}",  # CORE_REF {tag}', text, count=1)
    for needle in PYPROJECT_REMOVALS:
        text = _remove(text, needle, "pyproject.toml")
    for old, new in PYPROJECT_REPLACEMENTS:
        if text.count(old) != 1:
            raise AdoptionError(f"pyproject.toml: expected exactly one {old!r}")
        text = text.replace(old, new, 1)
    if "packages/cloud-assessor-core" in text:
        raise AdoptionError("pyproject.toml: still names packages/cloud-assessor-core after the edits")
    return text


def adopt_lines(text: str, removals: tuple[str, ...], name: str) -> str:
    for needle in removals:
        text = _remove(text, needle, name)
    return text


def adopt(root: Path, tag: str, url: str | None = None) -> list[Path]:
    """Rewrite the three files under root, all or none. Returns the paths written."""
    url = url or wheel_url(tag)
    if not TAG.fullmatch(tag):
        raise AdoptionError(f"tag {tag!r} is not v<major>.<minor>.<patch>")
    plan = {
        root / "pyproject.toml": lambda t: adopt_pyproject(t, tag, url),
        root / "infrastructure" / "docker" / "Dockerfile": lambda t: adopt_lines(t, DOCKERFILE_REMOVALS, "Dockerfile"),
        root / ".dockerignore": lambda t: adopt_lines(t, DOCKERIGNORE_REMOVALS, ".dockerignore"),
    }
    new_texts = {}
    for path, edit in plan.items():
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise AdoptionError(f"{path.name}: {type(exc).__name__}") from None
        new_texts[path] = edit(text)
    for path, text in new_texts.items():
        path.write_text(text, encoding="utf-8")
    return list(new_texts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tag", required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--wheel-url")
    args = parser.parse_args(argv)
    try:
        written = adopt(args.root, args.tag, args.wheel_url)
    except AdoptionError as exc:
        print(f"::error::first adoption refused, nothing written: {exc}")
        return 1
    for path in written:
        print(f"rewrote {path.relative_to(args.root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
