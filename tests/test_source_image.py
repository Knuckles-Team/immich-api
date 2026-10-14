"""The image must package this checkout and its runtime content before install."""

import configparser
import fnmatch
import hashlib
import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_source_image_matches_reviewed_generated_delta():
    provenance = json.loads(
        (ROOT / "validation/source-image-2026-10-12.json").read_text()
    )
    for name, digest in provenance["exact_generated_files"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
    docker = (ROOT / "docker/Dockerfile").read_text()
    assert docker.index("COPY immich_api/ ./immich_api/") < docker.index(
        '--prerelease=allow ".[mcp]"'
    )
    assert "COPY pyproject.toml README.md LICENSE ./" in docker
    assert "immich-api[mcp]" not in docker and "git clone" not in docker
    assert "FROM mcp AS default" in docker
    config = configparser.ConfigParser(interpolation=None)
    config.read(ROOT / ".bumpversion.cfg")
    assert not any("docker/Dockerfile" in section for section in config.sections())


def test_source_image_package_data_covers_served_content():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    patterns = project["tool"]["setuptools"]["package-data"]["immich_api"]
    package = ROOT / "immich_api"
    files = [package / "openapi_contract.json", package / "connector_manifest.yml"]
    for directory in ("prompts", "skills", "ontology", "connectors"):
        files.extend(
            path for path in (package / directory).rglob("*") if path.is_file()
        )
    for path in files:
        if "__pycache__" not in path.parts:
            assert any(
                fnmatch.fnmatchcase(path.relative_to(package).as_posix(), pattern)
                for pattern in patterns
            ), path
