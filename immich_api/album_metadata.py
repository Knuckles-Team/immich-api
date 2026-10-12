"""Bounded, explicit projection of album metadata; no network or graph work."""

from __future__ import annotations

from datetime import datetime
from typing import TypedDict
from uuid import UUID


class AlbumMetadata(TypedDict):
    id: str
    node_type: str
    albumName: str
    assetCount: int
    shared: bool
    hasSharedLink: bool
    createdAt: str
    updatedAt: str


class AlbumSample(TypedDict):
    records: list[AlbumMetadata]
    complete: bool
    authoritative: bool
    source_action: str
    source_schema_sha256: str


SOURCE_SHA256 = "7db8383741eeb5c5c8c87a6221cd1cdd1206c8b1190b83363c64223a00bb020b"


def project_album(record: dict) -> AlbumMetadata:
    """Retain only declared fields; private nested values never leave this function."""
    record_id = record.get("id")
    if not isinstance(record_id, str) or UUID(record_id).version != 4:
        raise ValueError("album requires a stable UUID v4 identity")
    name, count = record.get("albumName"), record.get("assetCount")
    if (
        not isinstance(name, str)
        or type(count) is not int
        or not 0 <= count <= 9007199254740991
    ):
        raise ValueError("album metadata does not satisfy its source schema")
    for key in ("shared", "hasSharedLink"):
        if type(record.get(key)) is not bool:
            raise ValueError("album metadata does not satisfy its source schema")
    for key in ("createdAt", "updatedAt"):
        value = record.get(key)
        try:
            valid = (
                isinstance(value, str)
                and datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo
                is not None
            )
        except ValueError:
            valid = False
        if not valid:
            raise ValueError("album metadata requires timestamps with time zones")
    return AlbumMetadata(
        id=record_id,
        node_type="ImmichAlbum",
        albumName=name,
        assetCount=count,
        shared=record["shared"],
        hasSharedLink=record["hasSharedLink"],
        createdAt=record["createdAt"],
        updatedAt=record["updatedAt"],
    )


def album_sample(records: list[dict], limit: int = 1) -> AlbumSample:
    """Return a deterministic bounded sample, never an authoritative live set."""
    if type(limit) is not int or not 1 <= limit <= 5:
        raise ValueError("album sample limit must be between one and five")
    if not isinstance(records, list) or any(
        not isinstance(record, dict) for record in records
    ):
        raise ValueError("album source must return a list of objects")
    identities = [record.get("id") for record in records]
    if any(not isinstance(value, str) for value in identities) or len(
        set(identities)
    ) != len(identities):
        raise ValueError("album source identities must be unique strings")
    selected = sorted(records, key=lambda record: record["id"])[:limit]
    return AlbumSample(
        records=[project_album(record) for record in selected],
        complete=len(records) <= limit,
        authoritative=False,
        source_action="getAllAlbums",
        source_schema_sha256=SOURCE_SHA256,
    )
