"""Reviewed source admission and native discovery for the synthetic test client."""

import asyncio
import hashlib
import json
import os
import re
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import patch

from fastmcp import Client

from immich_api.mcp_server import build_server
from immich_api.openapi_runtime import CONTRACT
from immich_api.parity import verify_contract, verify_mcp
from immich_api.parity.openapi_schema_budget import require_schema_budget

ROOT = Path(__file__).resolve().parents[1]
OVERLAY_SHA256 = "bdd58565bd0ffa7383373ea32425147c6bcb343f135ebc5541a67411e9b7708b"
BUDGET_PATH = ROOT / "tests/fixtures/native-client-budget.json"
BUDGET = json.loads(BUDGET_PATH.read_text())
TOOL_NAMES = sorted(
    {f"{domain}_operations" for domain in CONTRACT["domains"]}
    | {"album_metadata_sample"}
)


def source_inventory(**overrides):
    """Recheck original bytes and pinned evidence, not a cached approval field."""
    source = (ROOT / "api-spec/immich.openapi.json").read_bytes()
    options = {
        "source_bytes": source,
        "overlay_bytes": (
            ROOT / "api-spec/immich.provider-response-evidence.json"
        ).read_bytes(),
        "expected_overlay_sha256": OVERLAY_SHA256,
        "evidence_root": ROOT / "api-spec/provider-source",
    }
    options.update(overrides)
    return verify_contract(
        json.loads(source), CONTRACT, hashlib.sha256(source).hexdigest(), **options
    )


def bounded_server():
    """Configure the ordinary server with an explicitly nonproduction budget."""
    with patch.dict(os.environ, {"IMMICH_API_MCP_CLIENT_BUDGET": str(BUDGET_PATH)}):
        server = build_server(
            command_args=["--transport", "stdio", "--auth-type", "none"]
        )
    assert server._openapi_schema_budget == BUDGET
    return server


async def native_initial_discovery(client):
    listed = await client.list_tools()
    assert {tool.name for tool in listed} == {"search_tools", "call_tool"}
    return require_schema_budget(listed, BUDGET)


async def native_discovery(client, name):
    """Verify one complete tool so discovery has its own bounded test budget."""
    await asyncio.sleep(0.12)
    result = await client.call_tool(
        "search_tools", {"pattern": "^" + re.escape(name) + r"(?:\s|$)"}
    )
    rows = result.data
    if isinstance(rows, dict):
        rows = rows.get("result")
    assert isinstance(rows, list) and len(rows) == 1
    assert rows[0]["name"] == name
    receipt = require_schema_budget(rows, BUDGET, kind="search_result")
    receipt["coverage"] = {"domains": 0, "exposed_operations": 0}
    if name != "album_metadata_sample":
        domain = name.removesuffix("_operations")
        actions = CONTRACT["domains"][domain]
        domain_contract = {
            "domains": {domain: actions},
            "operations": {
                action: CONTRACT["operations"][action] for action in actions
            },
            "schemas": {domain: CONTRACT["schemas"][domain]},
        }
        receipt["coverage"] = verify_mcp(domain_contract, rows)
    return receipt


class DiscoveredClient:
    """Exercise FastMCP's actual proxy, preserving its confirmation round trips."""

    def __init__(self, native):
        self.native = native
        self._pending = set()

    async def call_tool(self, name, arguments, **options):
        task = asyncio.create_task(
            self.native.call_tool(
                "call_tool", {"name": name, "arguments": arguments}, **options
            )
        )
        self._pending.add(task)
        try:
            return await task
        finally:
            self._pending.discard(task)

    async def cancel_pending(self):
        tasks = tuple(self._pending)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


@asynccontextmanager
async def isolated_native_client(server, elicitation_handler):
    """Drain outstanding calls and close the protocol before the next provider."""
    # Each fresh client adds server/discover and result-validation tools/list.
    # Reserve those two requests at the unchanged SDK limit of 10 requests/s.
    await asyncio.sleep(0.22)
    async with Client(
        server, elicitation_handler=elicitation_handler, timeout=10
    ) as native:
        assert native.protocol_version == "2026-07-28"
        client = DiscoveredClient(native)
        try:
            yield client
        finally:
            await client.cancel_pending()
