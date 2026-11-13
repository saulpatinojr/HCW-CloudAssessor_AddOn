"""Move the engine pin for core-update.yml: every bump from one release wheel to the next.

The engine `cloud-assessor-core` is the upstream release wheel, pinned in pyproject.toml on one line that carries the
marker `CORE_REF <tag>`. (It used to be a local seed under packages/; the first adoption, pull request 69, deleted it,
and the code for that one-time switch has been removed since.)

A bump (--bump --from <old tag>) replaces two lines, each built exactly from the old tag, with the lines for the new
tag: the pinned line, and the version line of the engine's static metadata in pyproject.toml,
`version = "<version>"  # CORE_METADATA` (the `[[tool.uv.dependency-metadata]]` entry that keeps uv from asking the
wheel's address; the same entry and marker as the Cloud Crawler add-on). Either both lines are replaced or nothing is
written. No pattern language is involved, so a tag cannot inject an edit or a command (the workflow also refuses any
tag that is not v<major>.<minor>.<patch> before it gets here). The workflow then runs `uv lock`, which downloads the
wheel and records its sha256. This script never touches the network and never edits uv.lock.

Usage: python scripts/adopt_core_wheel.py --bump --from v0.2.1 --tag v0.2.2 [--root <repository root>]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

UPSTREAM = "saulpatinojr/HCW-CloudAssessor_App"
TAG = re.compile(r"^v(\d+\.\d+\.\d+)$")


class AdoptionError(RuntimeError):
    """A file did not look as expected; nothing was written."""


def wheel_url(tag: str) -> str:
    match = TAG.fullmatch(tag)
    if not match:
        raise AdoptionError(f"tag {tag!r} is not v<major>.<minor>.<patch>")
    version = match.group(1)
    return f"https://github.com/{UPSTREAM}/releases/download/{tag}/cloud_assessor_core-{version}-py3-none-any.whl"


def pinned_line(tag: str) -> str:
    return f'  "cloud-assessor-core @ {wheel_url(tag)}",  # CORE_REF {tag}'


def metadata_line(tag: str) -> str:
    """The version line of the engine's static metadata (`[[tool.uv.dependency-metadata]]`) for a release tag."""
    match = TAG.fullmatch(tag)
    if not match:
        raise AdoptionError(f"tag {tag!r} is not v<major>.<minor>.<patch>")
    return f'version = "{match.group(1)}"  # CORE_METADATA'


def _replace_line(text: str, old: str, new: str, what: str) -> str:
    lines = text.split("\n")
    found = [i for i, line in enumerate(lines) if line == old]
    if len(found) != 1:
        raise AdoptionError(f"pyproject.toml: expected exactly one {what} line for the old tag, found {len(found)}")
    lines[found[0]] = new
    return "\n".join(lines)


def bump_pyproject(text: str, old_tag: str, new_tag: str) -> str:
    """Replace the pinned line and the CORE_METADATA line for old_tag with those for new_tag, both or neither."""
    if old_tag == new_tag:
        raise AdoptionError("the old and the new tag are the same")
    text = _replace_line(text, pinned_line(old_tag), pinned_line(new_tag), "pinned CORE_REF")
    return _replace_line(text, metadata_line(old_tag), metadata_line(new_tag), "CORE_METADATA")


def bump(root: Path, old_tag: str, new_tag: str) -> list[Path]:
    path = root / "pyproject.toml"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AdoptionError(f"{path.name}: {type(exc).__name__}") from None
    path.write_text(bump_pyproject(text, old_tag, new_tag), encoding="utf-8")
    return [path]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tag", required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    # Required, and kept as a flag so the workflow's command line reads the same as before the seed code was removed.
    parser.add_argument("--bump", action="store_true", help="move the existing wheel pin (the only mode)")
    parser.add_argument("--from", dest="old_tag")
    args = parser.parse_args(argv)
    try:
        if not args.bump or not args.old_tag:
            raise AdoptionError("--bump and --from are required (the first adoption from the seed has happened)")
        written = bump(args.root, args.old_tag, args.tag)
    except AdoptionError as exc:
        print(f"::error::bump refused, nothing written: {exc}")
        return 1
    for path in written:
        print(f"rewrote {path.relative_to(args.root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
