"""Reviewed source admission and native discovery for the synthetic test client."""

import asyncio
import hashlib
import json
import os
import re
from pathlib import Path
from unittest.mock import patch

from immich_api.mcp_server import build_server
from immich_api.openapi_runtime import CONTRACT
from immich_api.parity import verify_contract, verify_mcp
from immich_api.parity.openapi_schema_budget import require_schema_budget

ROOT = Path(__file__).resolve().parents[1]
OVERLAY_SHA256 = "43f936578e5361b4400750ccb9e04747948eabe19baad0e78d90774c9c79c432"
BUDGET_PATH = ROOT / "tests/fixtures/native-client-budget.json"
BUDGET = json.loads(BUDGET_PATH.read_text())


def source_inventory(**overrides):
    """Recheck original bytes and pinned evidence, not a cached approval field."""
    source = (ROOT / "api-spec/immich.openapi.json").read_bytes()
    options = {
        "source_bytes": source,
        "overlay_bytes": (ROOT / "api-spec/immich.provider-evidence.json").read_bytes(),
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


async def native_discovery(client):
    listed = await client.list_tools()
    assert {tool.name for tool in listed} == {"search_tools", "call_tool"}
    receipt = {"initial": require_schema_budget(listed, BUDGET), "retrievals": {}}
    tools = []
    names = {f"{domain}_operations" for domain in CONTRACT["domains"]}
    names.add("album_metadata_sample")
    for name in sorted(names):
        await asyncio.sleep(0.12)
        result = await client.call_tool(
            "search_tools", {"pattern": "^" + re.escape(name) + r"(?:\s|$)"}
        )
        rows = result.data
        if isinstance(rows, dict):
            rows = rows.get("result")
        assert isinstance(rows, list) and len(rows) == 1
        assert rows[0]["name"] == name
        receipt["retrievals"][name] = require_schema_budget(
            rows, BUDGET, kind="search_result"
        )
        tools.extend(rows)
    receipt["coverage"] = verify_mcp(CONTRACT, tools)
    receipt["production_client_approval"] = False
    return receipt


class DiscoveredClient:
    """Exercise FastMCP's actual proxy, preserving its confirmation round trips."""

    def __init__(self, native):
        self.native = native

    async def call_tool(self, name, arguments, **options):
        return await self.native.call_tool(
            "call_tool", {"name": name, "arguments": arguments}, **options
        )
