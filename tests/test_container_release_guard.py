"""Fail closed on public wheel drift before the container publishing workflow."""

import hashlib
import importlib.util
import io
from pathlib import Path
from zipfile import ZipFile

import pytest

PATH = Path(__file__).resolve().parents[1] / "scripts/verify_container_release.py"
SPEC = importlib.util.spec_from_file_location("container_release_guard", PATH)
assert SPEC is not None and SPEC.loader is not None
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)


def _wheel(payloads):
    stream = io.BytesIO()
    with ZipFile(stream, "w") as wheel:
        for name, body in payloads.items():
            wheel.writestr(name, body)
    return stream.getvalue()


def test_public_wheel_requires_exact_source_bytes_and_complete_inventory():
    expected = {
        "immich_api/__init__.py": b"",
        "immich_api/ontology/immich.ttl": b"reviewed",
    }
    data = _wheel(expected)
    GUARD.verify_payload(data, hashlib.sha256(data).hexdigest(), expected)
    for changed in (
        {"immich_api/__init__.py": b""},
        {**expected, "immich_api/extra.py": b"unexpected"},
        {**expected, "immich_api/ontology/immich.ttl": b"different"},
    ):
        data = _wheel(changed)
        with pytest.raises(ValueError, match="inventory|payload"):
            GUARD.verify_payload(data, hashlib.sha256(data).hexdigest(), expected)


def test_public_wheel_digest_is_checked_before_archive_contents():
    with pytest.raises(ValueError, match="digest"):
        GUARD.verify_payload(b"not a wheel", "0" * 64, {})


def test_wrong_container_pin_refuses_before_any_network_call(tmp_path, monkeypatch):
    (tmp_path / "docker").mkdir()
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname="immich-api"\nversion="0.2.4"\n'
    )
    (tmp_path / "docker/Dockerfile").write_text(
        "RUN pip install immich-api[mcp]==0.2.3\n"
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("invalid release pins must fail before network access")

    monkeypatch.setattr(GUARD, "urlopen", forbidden)
    with pytest.raises(ValueError, match="pin"):
        GUARD.verify_release(tmp_path)
