import json

from agent_connector_sdk.mcp.action_dispatch import resolve_action
from agent_connector_sdk.mcp.concurrency import run_blocking
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ..auth import get_client


def register_system_tools(mcp: FastMCP):
    """Register system tag dynamic tools."""

    @mcp.tool(tags={"system"})
    async def system_operations(
        action: str = Field(
            description="Action to perform. Must be one of: 'status', 'info'."
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage system tag operations. CONCEPT:IMMICH-001"""
        if ctx:
            await ctx.info("Executing system tool...")

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {type(e).__name__}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Action-router trio: resolve_action validates/canonicalizes (and serves the
        # discovery payload), run_blocking runs the sync client call off the event loop.
        resolved = resolve_action(
            action, {"status", "info"}, service="immich-api"
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "status":
            return await run_blocking(client.get_system_status, **kwargs)
        return {"info": "System operations dynamic placeholder."}
