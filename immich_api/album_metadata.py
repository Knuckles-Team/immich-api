"""Bounded, explicit projection of album metadata; no network or graph work."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
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


def album_graph_properties(record: dict) -> dict[str, str | int | bool]:
    """Map selected provider fields to the actual ontology predicate keys."""
    projected = project_album(record)
    provenance = json.loads(
        (Path(__file__).parent / "ontology/schema-provenance.json").read_text()
    )
    targets = {
        item["source_pointer"].rsplit("/", 1)[1]: item["property"]
        for item in provenance["properties"]
        if item["class"] == "ImmichAlbum" and item["range"].startswith("xsd:")
    }
    return {
        targets[field]: value
        for field, value in projected.items()
        if field != "node_type"
    }


def _validate_timestamp(value):
    try:
        valid = (
            isinstance(value, str)
            and datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None
        )
    except ValueError:
        valid = False
    if not valid:
        raise ValueError("album metadata requires timestamps with time zones")


def _validate_album_fields(record):
    name, count = record.get("albumName"), record.get("assetCount")
    if not isinstance(name, str) or type(count) is not int:
        raise ValueError("album metadata does not satisfy its source schema")
    if not 0 <= count <= 9007199254740991:
        raise ValueError("album metadata does not satisfy its source schema")
    for key in ("shared", "hasSharedLink"):
        if type(record.get(key)) is not bool:
            raise ValueError("album metadata does not satisfy its source schema")
    for key in ("createdAt", "updatedAt"):
        _validate_timestamp(record.get(key))


def project_album(record: dict) -> AlbumMetadata:
    """Retain only declared fields; private nested values never leave this function."""
    record_id = record.get("id")
    if not isinstance(record_id, str) or UUID(record_id).version != 4:
        raise ValueError("album requires a stable UUID v4 identity")
    _validate_album_fields(record)
    return AlbumMetadata(
        id=record_id,
        node_type="ImmichAlbum",
        albumName=record["albumName"],
        assetCount=record["assetCount"],
        shared=record["shared"],
        hasSharedLink=record["hasSharedLink"],
        createdAt=record["createdAt"],
        updatedAt=record["updatedAt"],
    )


def _validate_source(records):
    if not isinstance(records, list) or any(
        not isinstance(record, dict) for record in records
    ):
        raise ValueError("album source must return a list of objects")
    identities = [record.get("id") for record in records]
    if any(not isinstance(value, str) for value in identities):
        raise ValueError("album source identities must be unique strings")
    if len(set(identities)) != len(identities):
        raise ValueError("album source identities must be unique strings")


def album_sample(records: list[dict], limit: int = 1) -> AlbumSample:
    """Return a deterministic bounded sample, never an authoritative live set."""
    if type(limit) is not int or not 1 <= limit <= 5:
        raise ValueError("album sample limit must be between one and five")
    _validate_source(records)
    selected = sorted(records, key=lambda record: record["id"])[:limit]
    return AlbumSample(
        records=[project_album(record) for record in selected],
        complete=len(records) <= limit,
        authoritative=False,
        source_action="getAllAlbums",
        source_schema_sha256=SOURCE_SHA256,
    )
