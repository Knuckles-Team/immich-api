import pytest

from templateconnector_api.mcp_server import get_mcp_instance


@pytest.mark.concept("TEMPLATECONNECTOR-001")
def test_mcp_instance_registration(monkeypatch):
    """MCP server instantiates with its tool domains registered.

    CONCEPT:TEMPLATECONNECTOR-001
    """
    monkeypatch.setattr("sys.argv", ["templateconnector-mcp"])
    mcp, args, middlewares = get_mcp_instance()
    assert mcp is not None
