"""The image must package this checkout and its runtime content before install."""

import fnmatch
import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]


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
