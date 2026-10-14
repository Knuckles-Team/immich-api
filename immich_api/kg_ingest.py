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
from agent_connector_sdk.ingest.request import build_request
from epistemic_graph.generated.source_ingestion import SourceIngestionMode

from .album_metadata import album_graph_properties, project_album


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
    changes = _album_changes(projected)
    _validate_privacy(binding, changes)
    service = ingest if ingest is not None else current_ingest()
    return await service.submit(binding, changes)


def _album_changes(projected):
    entities = tuple(
        Entity(
            id=record["id"],
            node_type="ImmichAlbum",
            properties=album_graph_properties(record),
            updated_at=record["updatedAt"],
        )
        for record in projected
    )
    return ChangeSet(entities=entities, mode=SourceIngestionMode.DELTA)


def _validate_privacy(binding, changes):
    preview = build_request(binding, changes, previous=None)
    if any(
        record.payload.get("immichAlbumId") != record.record_id
        for record in preview.records
    ):
        raise ValueError("SDK privacy guard changed album identity; no submission")
