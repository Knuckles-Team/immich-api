"""One bounded read-only capability built from an allowlisted OpenAPI operation."""

from typing import Annotated

from agent_connector_sdk.mcp.concurrency import run_blocking
from fastmcp import FastMCP
from pydantic import Field

from ..album_metadata import AlbumSample, album_sample
from ..auth import get_client


def register_album_sample_tools(mcp: FastMCP):
    @mcp.tool(
        tags={"album_sample", "read-only"},
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def album_metadata_sample(
        limit: Annotated[int, Field(ge=1, le=5)] = 1,
    ) -> AlbumSample:
        """Sample up to five owned albums; omit membership, paths and share secrets.

        Uses getAllAlbums with isOwned=true. The API has no server-side limit;
        its existing response byte/time limits still apply. This read capability
        returns a non-authoritative sample and never ingests or withdraws.
        CONCEPT:IMMICH-001
        """
        response = await run_blocking(
            get_client().execute,
            "albums",
            {"action": "getAllAlbums", "query": {"isOwned": True}},
        )
        return album_sample(response["data"], limit)
