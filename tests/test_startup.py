import importlib

import pytest


@pytest.mark.concept("IMMICH-001")
def test_mcp_server_module_importable():
    """MCP server module imports cleanly at startup. CONCEPT:IMMICH-001"""
    assert importlib.import_module("immich_api.mcp_server") is not None
