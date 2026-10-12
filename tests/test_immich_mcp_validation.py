import pytest

from immich_api.mcp_server import get_mcp_instance


@pytest.mark.concept("IMMICH-001")
def test_mcp_instance_registration(monkeypatch):
    """MCP server instantiates with its tool domains registered.

    CONCEPT:IMMICH-001
    """
    monkeypatch.setattr("sys.argv", ["immich-mcp"])
    mcp, args, middlewares = get_mcp_instance()
    assert mcp is not None
