"""Self-contained generated API/MCP parity checks; no sibling builder required."""

from .openapi_parity import (
    operation_inventory,
    require_complete_coverage,
    verify_contract,
    verify_mcp,
)
from .openapi_transport_parity import verify_transport

__all__ = [
    "operation_inventory",
    "require_complete_coverage",
    "verify_contract",
    "verify_mcp",
    "verify_transport",
]
