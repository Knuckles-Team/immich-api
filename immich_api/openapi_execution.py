"""Preserve provider-origin and SDK write-confirmation boundaries."""

from urllib.parse import urlsplit

from fastmcp.server.dependencies import get_context
from mcp.types import InputRequiredResult
from scion_sdk.mcp.context import confirmation_refusal, ctx_confirm_destructive


def require_origin(base_url, *, credential_scheme, allow_plaintext):
    parsed = urlsplit(base_url)
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("Base URL must be the provider origin without a path")
    if credential_scheme and parsed.scheme == "http" and not allow_plaintext:
        raise ValueError("Credential-bearing plaintext HTTP requires explicit opt-in")


async def confirm_write(operation, arguments, client):
    """Return None to proceed, an InputRequiredResult, or a clean refusal dict."""
    if operation["read_only"]:
        return None
    if not client.allow_writes:
        raise PermissionError("Writes require explicit operator enablement")
    context = get_context()
    confirmation = await ctx_confirm_destructive(
        context,
        operation["action"],
        confirmation_arguments=arguments,
        explicit_confirm=arguments.get("confirm") is True,
    )
    if isinstance(confirmation, InputRequiredResult):
        return confirmation
    if confirmation is not True:
        return confirmation_refusal(context, operation["action"])
    return None
