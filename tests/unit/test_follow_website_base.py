"""scripts/follow_website_base.py moves versions.env and every external FROM together, or nothing.

The script is what base-update.yml runs. It reads the website's pin as untrusted text, so each value must match a strict
pattern, and a Dockerfile it cannot move completely is left untouched.
"""

import importlib.util
from pathlib import Path

import pytest

from ..conftest import ROOT

_spec = importlib.util.spec_from_file_location("follow_website_base", ROOT / "scripts" / "follow_website_base.py")
assert _spec is not None and _spec.loader is not None
follow_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(follow_mod)

OLD = "sha256:" + "a" * 64
NEW = "sha256:" + "b" * 64
IMAGE = "python:3.14.8-slim-trixie"

VERSIONS = f"""# Base image comment that must survive the move.
BASE_IMAGE={IMAGE}
BASE_DIGEST={OLD}
BASE_PYTHON_VERSION=3.14.8
"""
DOCKERFILE = f"""# Header comment mentioning FROM {IMAGE}@{OLD} in prose is not a FROM line.
FROM {IMAGE}@{OLD} AS build
RUN true
FROM {IMAGE}@{OLD} AS lab
COPY --from=build /install /usr/local
FROM lab AS final
"""


def website(digest: str = NEW, image: str = IMAGE, version: str = "3.14.9") -> str:
    return f"# comment\nBASE_IMAGE={image}\nBASE_DIGEST={digest}\nBASE_PYTHON_VERSION={version}\nOTHER=1\n"


def make_repo(root: Path, versions: str = VERSIONS, dockerfile: str = DOCKERFILE) -> Path:
    docker = root / "infrastructure" / "docker"
    docker.mkdir(parents=True)
    (docker / "versions.env").write_text(versions, encoding="utf-8", newline="\n")
    (docker / "Dockerfile").write_text(dockerfile, encoding="utf-8", newline="\n")
    return root


def read(root: Path, name: str) -> str:
    return (root / "infrastructure" / "docker" / name).read_text(encoding="utf-8")


def test_moves_versions_env_and_every_external_from_together(tmp_path):
    root = make_repo(tmp_path)
    result = follow_mod.follow(root, website(), write=True)
    assert result["changed"] == "true"
    assert result["old"] == f"{IMAGE}@{OLD}"
    assert result["new"] == f"{IMAGE}@{NEW}"
    assert result["short"] == "b" * 12
    env = follow_mod.parse_env(read(root, "versions.env"))
    assert (env["BASE_IMAGE"], env["BASE_DIGEST"], env["BASE_PYTHON_VERSION"]) == (IMAGE, NEW, "3.14.9")
    assert read(root, "versions.env").startswith("# Base image comment that must survive the move.\n")
    froms = [line for line in read(root, "Dockerfile").splitlines() if line.startswith("FROM ")]
    assert froms == [f"FROM {IMAGE}@{NEW} AS build", f"FROM {IMAGE}@{NEW} AS lab", "FROM lab AS final"]
    assert OLD not in read(root, "Dockerfile").split("\n", 1)[1]  # only the prose comment on line 1 may mention it


def test_a_second_run_finds_nothing_to_do(tmp_path):
    root = make_repo(tmp_path)
    follow_mod.follow(root, website(), write=True)
    assert follow_mod.follow(root, website(), write=True) == {"changed": "false"}


def test_check_mode_reports_the_move_and_writes_nothing(tmp_path):
    root = make_repo(tmp_path)
    assert follow_mod.follow(root, website(), write=False)["changed"] == "true"
    assert read(root, "versions.env") == VERSIONS
    assert read(root, "Dockerfile") == DOCKERFILE


def test_nothing_to_do_when_the_pin_already_matches(tmp_path):
    root = make_repo(tmp_path)
    assert follow_mod.follow(root, website(digest=OLD, version="3.14.8"), write=True) == {"changed": "false"}


@pytest.mark.parametrize(
    "digest",
    [
        "sha256:" + "B" * 64,
        "sha256:" + "b" * 63,
        "sha256:" + "b" * 65,
        "b" * 64,
        "sha256:" + "b" * 63 + "z",
        "sha256:" + "b" * 64 + "\rBASE_IMAGE=evil:1",  # a lone carriage return must not start a second line
        "sha256:" + "b" * 64 + " ",
    ],
)
def test_a_digest_that_is_not_sha256_and_64_lowercase_hex_is_refused(tmp_path, digest):
    root = make_repo(tmp_path)
    with pytest.raises(follow_mod.FollowError):
        follow_mod.follow(root, website(digest=digest), write=True)
    assert read(root, "versions.env") == VERSIONS


@pytest.mark.parametrize(
    "image", ["python", "python:3.14;rm", "python:3 14", "Python:3.14", "$(id):3.14", "python:3.14$X", "", "-x:1"]
)
def test_an_image_that_is_not_name_colon_tag_is_refused(tmp_path, image):
    root = make_repo(tmp_path)
    with pytest.raises(follow_mod.FollowError):
        follow_mod.follow(root, website(image=image), write=True)
    assert read(root, "Dockerfile") == DOCKERFILE


@pytest.mark.parametrize("image", ["evil.example.com/team/python:3.14.9", "node:3.14.9-slim", "library/python:3.14.9"])
def test_a_different_image_repository_is_left_for_a_person_and_writes_nothing(tmp_path, image):
    root = make_repo(tmp_path)
    with pytest.raises(follow_mod.FollowError, match="a person must decide"):
        follow_mod.follow(root, website(image=image), write=True)
    assert (read(root, "versions.env"), read(root, "Dockerfile")) == (VERSIONS, DOCKERFILE)


def test_another_tag_of_the_same_repository_is_followed(tmp_path):
    root = make_repo(tmp_path)
    result = follow_mod.follow(root, website(image="python:3.14.9-slim-trixie", version="3.14.9"), write=True)
    assert result["new"] == f"python:3.14.9-slim-trixie@{NEW}"
    assert f"FROM python:3.14.9-slim-trixie@{NEW} AS build" in read(root, "Dockerfile")


def test_a_move_to_another_python_minor_line_is_left_for_a_person_and_writes_nothing(tmp_path):
    root = make_repo(tmp_path)
    with pytest.raises(follow_mod.FollowError, match="3.14 to 3.15"):
        follow_mod.follow(root, website(image="python:3.15.0-slim-trixie", version="3.15.0"), write=True)
    assert (read(root, "versions.env"), read(root, "Dockerfile")) == (VERSIONS, DOCKERFILE)


@pytest.mark.parametrize("version", ["3.14", "3.14.8-rc1", "v3.14.8", ""])
def test_a_python_version_that_is_not_major_minor_patch_is_refused(tmp_path, version):
    root = make_repo(tmp_path)
    with pytest.raises(follow_mod.FollowError):
        follow_mod.follow(root, website(version=version), write=True)


def test_a_website_file_without_the_keys_is_refused(tmp_path):
    root = make_repo(tmp_path)
    with pytest.raises(follow_mod.FollowError, match="missing"):
        follow_mod.follow(root, "BASE_IMAGE=python:3.14.8-slim-trixie\n", write=True)


def test_a_from_line_that_is_not_the_old_pin_stops_everything_and_writes_nothing(tmp_path):
    odd = DOCKERFILE.replace(f"FROM {IMAGE}@{OLD} AS lab", "FROM debian:trixie-slim AS lab")
    root = make_repo(tmp_path, dockerfile=odd)
    with pytest.raises(follow_mod.FollowError, match="neither an earlier stage"):
        follow_mod.follow(root, website(), write=True)
    assert read(root, "Dockerfile") == odd
    assert read(root, "versions.env") == VERSIONS


@pytest.mark.parametrize(
    "extra",
    [
        f"from {IMAGE}@{OLD} AS shout\n",  # lower-case FROM: ci.yml's grep ignores it, so it would be left behind
        f"ARG BASE={IMAGE}@{OLD}\n",
        f"COPY --from={IMAGE}@{OLD} /x /x\n",
        f"FROM --platform=linux/amd64 {IMAGE}@{OLD} AS plat\n",
    ],
)
def test_the_old_pin_left_anywhere_else_in_the_dockerfile_stops_everything(tmp_path, extra):
    odd = DOCKERFILE + extra
    root = make_repo(tmp_path, dockerfile=odd)
    with pytest.raises(follow_mod.FollowError):
        follow_mod.follow(root, website(), write=True)
    assert (read(root, "versions.env"), read(root, "Dockerfile")) == (VERSIONS, odd)


def test_a_dockerfile_with_no_from_on_the_old_pin_is_refused(tmp_path):
    root = make_repo(tmp_path, dockerfile="# no FROM lines\n")
    with pytest.raises(follow_mod.FollowError, match="no FROM line"):
        follow_mod.follow(root, website(), write=True)


def test_a_versions_env_that_repeats_a_key_is_refused(tmp_path):
    root = make_repo(tmp_path, versions=VERSIONS + f"BASE_DIGEST={OLD}\n")
    with pytest.raises(follow_mod.FollowError, match="exactly one"):
        follow_mod.follow(root, website(), write=True)
    assert read(root, "Dockerfile") == DOCKERFILE


def test_a_crlf_versions_env_from_the_website_is_read_like_an_lf_one(tmp_path):
    root = make_repo(tmp_path)
    follow_mod.follow(root, website().replace("\n", "\r\n"), write=True)
    assert follow_mod.parse_env(read(root, "versions.env"))["BASE_DIGEST"] == NEW


def test_no_temporary_file_is_left_behind(tmp_path):
    root = make_repo(tmp_path)
    follow_mod.follow(root, website(), write=True)
    assert sorted(path.name for path in (root / "infrastructure" / "docker").iterdir()) == [
        "Dockerfile",
        "versions.env",
    ]


def test_a_crlf_dockerfile_keeps_its_line_endings(tmp_path):
    root = make_repo(tmp_path)
    path = root / "infrastructure" / "docker" / "Dockerfile"
    path.write_bytes(DOCKERFILE.replace("\n", "\r\n").encode("utf-8"))
    follow_mod.follow(root, website(), write=True)
    raw = path.read_bytes()
    assert raw.count(b"\r\n") == raw.count(b"\n") and NEW.encode() in raw


def test_main_prints_the_result_and_appends_it_to_github_output(tmp_path, monkeypatch, capsys):
    root = make_repo(tmp_path / "repo")
    site = tmp_path / "website.env"
    site.write_text(website(), encoding="utf-8")
    output = tmp_path / "github_output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    assert follow_mod.main(["--website-env", str(site), "--root", str(root)]) == 0
    printed = capsys.readouterr().out
    assert "changed=true" in printed and f"new={IMAGE}@{NEW}" in printed
    assert f"short={'b' * 12}" in output.read_text(encoding="utf-8")
    assert follow_mod.parse_env(read(root, "versions.env"))["BASE_DIGEST"] == NEW


def test_main_exits_nonzero_with_an_error_annotation_on_a_bad_website_file(tmp_path, capsys):
    root = make_repo(tmp_path / "repo")
    site = tmp_path / "website.env"
    site.write_text(website(digest="not-a-digest"), encoding="utf-8")
    assert follow_mod.main(["--website-env", str(site), "--root", str(root)]) == 1
    assert capsys.readouterr().out.startswith("::error::")


def test_this_repositorys_own_files_are_in_the_shape_the_script_can_move():
    """The real Dockerfile and versions.env: a different digest would move cleanly (check mode, nothing written)."""
    own = follow_mod.parse_env((ROOT / "infrastructure" / "docker" / "versions.env").read_text(encoding="utf-8"))
    assert follow_mod.follow(
        ROOT,
        website(digest=own["BASE_DIGEST"], image=own["BASE_IMAGE"], version=own["BASE_PYTHON_VERSION"]),
        write=False,
    ) == {"changed": "false"}
    moved = follow_mod.follow(ROOT, website(digest=NEW, image=own["BASE_IMAGE"]), write=False)
    assert moved["changed"] == "true" and moved["new"].endswith(NEW)
