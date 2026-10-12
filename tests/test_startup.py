import importlib

import pytest


@pytest.mark.concept("TEMPLATECONNECTOR-001")
def test_mcp_server_module_importable():
    """MCP server module imports cleanly at startup. CONCEPT:TEMPLATECONNECTOR-001"""
    assert importlib.import_module("templateconnector_api.mcp_server") is not None
