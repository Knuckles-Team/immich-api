"""Explicit source/account scope, bounded projection and receipt preservation."""

import asyncio
from types import SimpleNamespace

import pytest

from immich_api import kg_ingest
from tests.test_album_metadata import album


class FakeIngest:
    def __init__(self):
        self.calls = []
        self.receipt = SimpleNamespace(
            affected_count=1, relationship_count=0, accepted_checkpoint="fixture"
        )

    async def submit(self, binding, changes):
        self.calls.append((binding, changes))
        return self.receipt


def test_ingest_uses_scoped_binding_and_preserves_receipt():
    fake = FakeIngest()
    result = asyncio.run(
        kg_ingest.ingest_album_metadata(
            [album()], source_scope="fixture.account", ingest=fake
        )
    )
    assert result is fake.receipt
    binding, changes = fake.calls[0]
    assert binding.connector == "immich-api"
    assert binding.stream.startswith("album-metadata:")
    assert binding.strict_schema
    assert changes.entities[0].node_type == "ImmichAlbum"
    assert "albumUsers" not in changes.entities[0].properties
    assert (
        not changes.withdrawals
        and not changes.relationships
        and changes.live_ids is None
    )


def test_scope_partition_and_invalid_scope():
    fake = FakeIngest()
    for scope in ("fixture.account-a", "fixture.account-b"):
        asyncio.run(
            kg_ingest.ingest_album_metadata([album()], source_scope=scope, ingest=fake)
        )
    assert fake.calls[0][0].stream != fake.calls[1][0].stream
    with pytest.raises(ValueError, match="opaque"):
        asyncio.run(
            kg_ingest.ingest_album_metadata(
                [album()],
                source_scope="https://user:secret@example.invalid",
                ingest=fake,
            )
        )
    assert len(fake.calls) == 2


def test_invalid_or_excess_records_fail_before_submit():
    fake = FakeIngest()
    for records in (
        [],
        [album(n) for n in range(1, 7)],
        [dict(album(), id="missing")],
        [album(), album()],
    ):
        with pytest.raises(ValueError):
            asyncio.run(
                kg_ingest.ingest_album_metadata(
                    records, source_scope="fixture.account", ingest=fake
                )
            )
    assert not fake.calls


def test_submit_failure_propagates():
    class RejectedIngest:
        async def submit(self, binding, changes):
            raise RuntimeError("fixture refusal")

    with pytest.raises(RuntimeError, match="fixture refusal"):
        asyncio.run(
            kg_ingest.ingest_album_metadata(
                [album()], source_scope="fixture.account", ingest=RejectedIngest()
            )
        )
