#!/usr/bin/env python3
"""Verify the public wheel before publishing a container from its pinned release."""

from __future__ import annotations

import hashlib
import io
import json
import subprocess
import tomllib
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile


def verify_payload(data: bytes, digest: str, expected: dict[str, bytes]) -> None:
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError("Public wheel digest differs from the PyPI receipt")
    with ZipFile(io.BytesIO(data)) as wheel:
        names = {
            n
            for n in wheel.namelist()
            if n.startswith("immich_api/") and not n.endswith("/")
        }
        if names != expected.keys():
            raise ValueError(
                "Public wheel package inventory differs from reviewed source"
            )
        for name in names:
            if wheel.read(name) != expected[name]:
                raise ValueError(
                    f"Public wheel payload differs from reviewed source: {name}"
                )


def reviewed_payload(root: Path) -> dict[str, bytes]:
    files = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", "HEAD", "immich_api/"],
        cwd=root,
        text=True,
    ).splitlines()
    return {
        name: subprocess.check_output(["git", "show", f"HEAD:{name}"], cwd=root)
        for name in files
    }


def verify_release(root: Path) -> dict[str, object]:
    project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    name, version = project["name"], project["version"]
    pin = f"{name}[mcp]=={version}"
    if pin not in (root / "docker/Dockerfile").read_text().split():
        raise ValueError("Dockerfile must pin the reviewed package version")
    with urlopen(
        f"https://pypi.org/pypi/{name}/{version}/json", timeout=30
    ) as response:
        metadata = json.load(response)
    item = next(row for row in metadata["urls"] if row["filename"].endswith(".whl"))
    with urlopen(item["url"], timeout=30) as response:
        data = response.read()
    expected = reviewed_payload(root)
    verify_payload(data, item["digests"]["sha256"], expected)
    return {
        "package": name,
        "version": version,
        "wheel_sha256": item["digests"]["sha256"],
        "verified_payload_files": len(expected),
    }


if __name__ == "__main__":
    print(
        json.dumps(verify_release(Path(__file__).resolve().parents[1]), sort_keys=True)
    )
