"""Explicit album metadata submission through the SDK; no implicit ingestion."""

from __future__ import annotations

import hashlib
import re

from agent_connector_sdk.ingest import (
    ChangeSet,
    Entity,
    IngestBinding,
    KnowledgeIngest,
    current_ingest,
)

from .album_metadata import project_album


async def ingest_album_metadata(
    records: list[dict],
    *,
    source_scope: str,
    ingest: KnowledgeIngest | None = None,
):
    """Submit at most five metadata records and return the unmodified EG receipt.

    source_scope is an operator-assigned opaque label unique to the provider
    instance AND account/authorization scope. It is not a URL or credential.
    The caller must separately authorize graph persistence; this is not an MCP
    tool and listing/calling provider tools never invokes it automatically.
    No photos, person observations, links, withdrawals or reconciliation occur.
    """
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", source_scope):
        raise ValueError("source_scope must be an opaque instance/account label")
    if not 1 <= len(records) <= 5:
        raise ValueError("ingest_album_metadata requires one to five records")
    projected = [project_album(record) for record in records]
    if len({record["id"] for record in projected}) != len(projected):
        raise ValueError("duplicate album identity")
    scope = hashlib.sha256(source_scope.encode()).hexdigest()
    binding = IngestBinding(
        connector="immich-api",
        stream=f"album-metadata:{scope}",
        server="Immich Api",
        tool="album_metadata_sample",
        strict_schema=True,
    )
    entities = tuple(
        Entity(
            id=record["id"],
            node_type="ImmichAlbum",
            properties={
                key: value for key, value in record.items() if key != "node_type"
            },
            updated_at=record["updatedAt"],
        )
        for record in projected
    )
    service = ingest if ingest is not None else current_ingest()
    return await service.submit(binding, ChangeSet(entities=entities))
