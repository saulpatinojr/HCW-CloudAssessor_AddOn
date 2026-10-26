"""Move this repository's base image to the website's current pin.

The website (saulpatinojr/HCW-HybridCloudWorks, lab-image/versions.env) is the source of truth for the base image
(BASE_IMAGE, BASE_DIGEST, BASE_PYTHON_VERSION). This repository keeps a copy in infrastructure/docker/versions.env and
repeats the reference on every external FROM line of infrastructure/docker/Dockerfile. This script rewrites all of them
together, or none: the `lint` job in ci.yml and the `base-follows-website` job in security.yml fail when they disagree.

It reads the website's file from a path, never from the network, and treats it as untrusted text: each value must match
a strict pattern before it is used. It writes nothing outside the two files above. It also refuses, for a person to
decide, a move to a different image repository, a move to a different Python minor line (the Dockerfile has python3.14
paths), and a Dockerfile it cannot move completely.

Usage: python scripts/follow_website_base.py --website-env <file> [--root <repository root>] [--check]
  --check   report whether a move is needed (exit 0 either way) and write nothing.
Prints `changed=true|false` and, when true, `old=`, `new=`, `short=`, `python=` and `old_python=` lines; they are also
appended to the file named by $GITHUB_OUTPUT when that variable is set. Exit 1 with a `::error::` line when the files
cannot be moved safely; both files are then left as they were.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

IMAGE_RE = re.compile(r"[a-z0-9]+(?:[._/-][a-z0-9]+)*:[A-Za-z0-9][A-Za-z0-9._-]*")
DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}")
VERSION_RE = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
KEYS = ("BASE_IMAGE", "BASE_DIGEST", "BASE_PYTHON_VERSION")
VERSIONS_ENV = Path("infrastructure/docker/versions.env")
DOCKERFILE = Path("infrastructure/docker/Dockerfile")


class FollowError(Exception):
    """The files cannot be moved safely; nothing was written."""


def parse_env(text: str) -> dict[str, str]:
    """KEY=VALUE lines of a plain shell assignment file; comments and blank lines are ignored."""
    values: dict[str, str] = {}
    for line in text.replace("\r\n", "\n").split("\n"):
        match = re.fullmatch(r"([A-Z][A-Z0-9_]*)=(.*)", line)
        if match:
            values[match.group(1)] = match.group(2)
    return values


def read_pin(text: str, where: str) -> dict[str, str]:
    values = parse_env(text)
    missing = [key for key in KEYS if key not in values]
    if missing:
        raise FollowError(f"{where}: missing {', '.join(missing)}")
    if not IMAGE_RE.fullmatch(values["BASE_IMAGE"]):
        raise FollowError(f"{where}: BASE_IMAGE is not an image reference of the form name:tag")
    if not DIGEST_RE.fullmatch(values["BASE_DIGEST"]):
        raise FollowError(f"{where}: BASE_DIGEST is not sha256: followed by 64 lowercase hex characters")
    if not VERSION_RE.fullmatch(values["BASE_PYTHON_VERSION"]):
        raise FollowError(f"{where}: BASE_PYTHON_VERSION is not major.minor.patch")
    return {key: values[key] for key in KEYS}


def repository_of(image: str) -> str:
    """The image name without its tag (read_pin has already shown the reference is name:tag, with no port)."""
    return image.rsplit(":", 1)[0]


def minor_line(version: str) -> str:
    return ".".join(version.split(".")[:2])


def rewrite_dockerfile(text: str, old_ref: str, new_ref: str) -> str:
    """Replace old_ref on every external FROM line. Every external FROM must carry old_ref, as ci.yml demands."""
    lines = text.split("\n")
    stages: set[str] = set()
    moved = 0
    for index, line in enumerate(lines):
        parts = line.rstrip("\r").split()
        if len(parts) < 2 or parts[0] != "FROM":
            continue
        reference = parts[1]
        if reference in stages:
            pass  # FROM an earlier stage
        elif reference == old_ref:
            lines[index] = line.replace(old_ref, new_ref, 1)
            moved += 1
        else:
            raise FollowError(
                f"Dockerfile line {index + 1}: FROM {reference} is neither an earlier stage nor {old_ref}"
            )
        if len(parts) >= 4 and parts[2].lower() == "as":
            stages.add(parts[3])
    if moved == 0:
        raise FollowError(f"Dockerfile: no FROM line carries {old_ref}")
    for index, line in enumerate(lines):
        if old_ref in line and not line.lstrip().startswith("#"):
            raise FollowError(
                f"Dockerfile line {index + 1}: still carries {old_ref} after the move; a person must decide"
            )
    return "\n".join(lines)


def rewrite_versions_env(text: str, new: dict[str, str]) -> str:
    out = text
    for key in KEYS:
        out, count = re.subn(rf"(?m)^{key}=.*$", lambda _m, k=key: f"{k}={new[k]}", out)
        if count != 1:
            raise FollowError(f"versions.env: expected exactly one {key} line, found {count}")
    return out


def replace_file(path: Path, data: bytes) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def follow(root: Path, website_text: str, write: bool) -> dict[str, str]:
    website = read_pin(website_text, "website versions.env")
    env_path = root / VERSIONS_ENV
    docker_path = root / DOCKERFILE
    env_text = env_path.read_bytes().decode("utf-8")
    local = read_pin(env_text, str(VERSIONS_ENV))
    if local == website:
        return {"changed": "false"}
    new_repository, old_repository = repository_of(website["BASE_IMAGE"]), repository_of(local["BASE_IMAGE"])
    if new_repository != old_repository:
        raise FollowError(f"the website's base image is {new_repository}, not {old_repository}; a person must decide")
    if minor_line(website["BASE_PYTHON_VERSION"]) != minor_line(local["BASE_PYTHON_VERSION"]):
        raise FollowError(
            f"the website moved Python from {minor_line(local['BASE_PYTHON_VERSION'])} to "
            f"{minor_line(website['BASE_PYTHON_VERSION'])}; the Dockerfile and pyproject.toml name the minor line, so "
            "a person must decide"
        )
    old_ref = f"{local['BASE_IMAGE']}@{local['BASE_DIGEST']}"
    new_ref = f"{website['BASE_IMAGE']}@{website['BASE_DIGEST']}"
    docker_text = docker_path.read_bytes().decode("utf-8")
    crlf = "\r\n" in docker_text
    new_docker = rewrite_dockerfile(docker_text.replace("\r\n", "\n"), old_ref, new_ref)
    new_env = rewrite_versions_env(env_text.replace("\r\n", "\n"), website)
    if write:
        replace_file(docker_path, (new_docker.replace("\n", "\r\n") if crlf else new_docker).encode("utf-8"))
        replace_file(env_path, new_env.encode("utf-8"))
    return {
        "changed": "true",
        "old": old_ref,
        "new": new_ref,
        "short": website["BASE_DIGEST"][len("sha256:") : len("sha256:") + 12],
        "python": website["BASE_PYTHON_VERSION"],
        "old_python": local["BASE_PYTHON_VERSION"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n", 1)[0])
    parser.add_argument(
        "--website-env", required=True, type=Path, help="the website's lab-image/versions.env, already downloaded"
    )
    parser.add_argument("--root", default=Path("."), type=Path, help="repository root (default: current directory)")
    parser.add_argument("--check", action="store_true", help="report only; write nothing")
    args = parser.parse_args(argv)
    try:
        result = follow(args.root, args.website_env.read_bytes().decode("utf-8"), write=not args.check)
    except FollowError as error:
        print(f"::error::{error}")
        return 1
    lines = [f"{key}={value}" for key, value in result.items()]
    print("\n".join(lines))
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
