"""Native SDK content and preset contracts; provider and engine boundaries are faked."""

import asyncio
import importlib.util
import json
from pathlib import Path

from agent_connector_sdk.adapters.mcp_tool_paging import tool_arguments
from agent_connector_sdk.adapters.mcp_tool_records import raw_records, source_record
from agent_connector_sdk.manifest.live_contract import validate_preset_tool_contract
from agent_connector_sdk.manifest.loader import (
    load_tool_presets,
    require_valid_connector_package,
)
from fastmcp import Client

from immich_api import mcp as modules
from immich_api.mcp_server import build_server
from tests.test_album_metadata import album

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "immich_api"


def test_generated_structure_is_fresh_and_reference_backed():
    spec = importlib.util.spec_from_file_location(
        "generate_immich_content", ROOT / "scripts/generate_immich_content.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for path, text in module.artifacts().items():
        assert path.read_text() == text
    provenance = json.loads((PACKAGE / "ontology/schema-provenance.json").read_text())
    assert len({item["class"] for item in provenance["properties"]}) == 8
    relations = [
        item
        for item in provenance["properties"]
        if not item["range"].startswith("xsd:")
    ]
    assert len(relations) == 6
    assert not any("contains" in item["property"].lower() for item in relations)
    assert not any(
        item["source_pointer"].endswith("/email") for item in provenance["properties"]
    )


def test_native_prompt_skill_shapes_and_tool_discovery(monkeypatch):
    monkeypatch.setenv("MCP_FLEET_REGISTRATION", "false")

    async def check():
        async with Client(
            build_server(command_args=["--transport", "stdio", "--auth-type", "none"]),
            timeout=5,
            init_timeout=5,
        ) as client:
            tools = await client.list_tools()
            names = {tool.name for tool in tools}
            assert "album_metadata_sample" in names and "server_operations" in names
            sample = next(
                tool for tool in tools if tool.name == "album_metadata_sample"
            )
            assert (
                sample.annotations.readOnlyHint
                and not sample.annotations.destructiveHint
            )
            prompts = await client.list_prompts()
            for name in (
                "immich_specialist",
                "immich_album_review",
                "immich_asset_metadata",
                "immich_person_record",
            ):
                assert name in {prompt.name for prompt in prompts}
                await asyncio.sleep(0.12)
                rendered = await client.get_prompt(name)
                text = " ".join(message.content.text for message in rendered.messages)
                assert "IMMICH_API_ALLOW_WRITES=false" in text
                assert "TODO" not in text
            resources = {
                str(resource.uri) for resource in await client.list_resources()
            }
            assert "shapes://immich-api/immich.ttl" in resources
            assert "skill://immich-health/SKILL.md" in resources
            preset = load_tool_presets(PACKAGE / "connectors/mcp_source_presets.json")[
                "immich_album_metadata_sample"
            ]
            validate_preset_tool_contract(
                tools, tool_name="album_metadata_sample", presets=[preset]
            )

    asyncio.run(check())


def test_bounded_sample_tool_and_sdk_preset_omit_private_values(monkeypatch):
    calls = []

    class FakeClient:
        def execute(self, domain, arguments):
            calls.append((domain, arguments))
            return {"data": [album(2), album(1)]}

    monkeypatch.setattr(modules.album_sample, "get_client", lambda: FakeClient())
    preset = load_tool_presets(PACKAGE / "connectors/mcp_source_presets.json")[
        "immich_album_metadata_sample"
    ]
    manifest = require_valid_connector_package(PACKAGE)

    async def check():
        async with Client(
            build_server(command_args=["--transport", "stdio", "--auth-type", "none"]),
            timeout=5,
            init_timeout=5,
        ) as client:
            result = await client.call_tool(
                preset.tool, tool_arguments(preset, dict(preset.params))
            )
            body = result.structured_content
            assert not body["authoritative"] and not body["complete"]
            raw = raw_records(preset, body)
            assert len(raw) == 1 and raw[0]["id"] == album(1)["id"]
            assert "private" not in json.dumps(body)
            pin = manifest.sync[0].tool_schema_sha256
            record = source_record(
                preset,
                raw[0],
                connector="immich-api",
                schema_sha256=pin,
                mapping_reference="manifest:immich-api#schema_mappings/ImmichAlbum",
            )
            assert record.provenance.tool == "album_metadata_sample"
            assert "albumUsers" not in record.payload

    asyncio.run(check())
    assert calls == [("albums", {"action": "getAllAlbums", "query": {"isOwned": True}})]
