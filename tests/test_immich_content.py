"""Native SDK content and preset contracts; provider and engine boundaries are faked."""

import importlib.util
import json
from pathlib import Path

from immich_api.mcp_server import build_server

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


def test_domain_registrar_retains_sdk_toggle(monkeypatch):
    from scion_sdk.mcp.tool_surface import registered_tools

    monkeypatch.setenv("MCP_FLEET_REGISTRATION", "false")
    monkeypatch.setenv("ALBUMSTOOL", "false")
    server = build_server(command_args=["--transport", "stdio", "--auth-type", "none"])
    tools = registered_tools(server)
    assert "albums_operations" not in tools
    assert "server_operations" in tools
    assert "server" in tools["server_operations"].tags
