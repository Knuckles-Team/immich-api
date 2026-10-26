import sys
from pathlib import Path

from agent_connector_sdk.config import load_config
from agent_connector_sdk.connector_identity import connector_version
from agent_connector_sdk.mcp.content import ConnectorContent
from agent_connector_sdk.mcp.server import create_mcp_server
from agent_connector_sdk.mcp.tool_surface import register_tool_surface

from . import mcp as tool_modules

__version__ = connector_version("immich_api")


def get_mcp_instance(*, command_args=None):
    """Construct one SDK-governed server and its native package content."""
    load_config()
    package_version = connector_version("immich_api")
    args, mcp, middlewares = create_mcp_server(
        name="Immich Api",
        version=package_version,
        instructions="Immich Api API + MCP Server",
        command_args=command_args,
        content=ConnectorContent.for_package(
            "immich_api", Path(__file__).resolve().parent, package_version
        ),
    )
    register_tool_surface(mcp, service="immich-api", tools_module=tool_modules)
    for middleware in middlewares:
        mcp.add_middleware(middleware)
    return mcp, args, middlewares


def build_server(*, command_args=None):
    return get_mcp_instance(command_args=command_args)[0]


def mcp_server():
    mcp, args, _ = get_mcp_instance()
    print("Starting Immich Api MCP", file=sys.stderr)
    options = (
        {} if args.transport == "stdio" else {"host": args.host, "port": args.port}
    )
    mcp.run(transport=args.transport, **options)


if __name__ == "__main__":
    mcp_server()
