
"""Resolve credential references only when constructing a vendor client."""

from contextlib import ExitStack

from agent_connector_sdk.auth.delegation import DelegatedTokenAuth, DelegationSettings
from agent_connector_sdk.auth.static import bearer_auth
from agent_connector_sdk.config import load_config, setting
from agent_connector_sdk.http.client import create_http_client
from agent_connector_sdk.http.options import HttpClientOptions
from agent_connector_sdk.tls.resolve import resolve_tls_profile

from .api import ApiClientSystem

_client: ApiClientSystem | None = None
_resources = ExitStack()


def get_client() -> ApiClientSystem:
    """Build one client; delegated auth resolves the verified caller per request."""
    global _client, _resources
    if _client is not None:
        return _client
    load_config()
    base_url = setting("TEMPLATECONNECTOR_API_BASE_URL", "")
    if not base_url:
        raise ValueError("TEMPLATECONNECTOR_API_BASE_URL is required")
    with ExitStack() as resources:
        tls = resolve_tls_profile("templateconnector")
        resources.callback(tls.cleanup)
        delegation = DelegationSettings.from_settings()
        if delegation.enabled:
            token_tls = resolve_tls_profile("oidc")
            resources.callback(token_tls.cleanup)
            token_client = create_http_client(
                HttpClientOptions(base_url=delegation.token_endpoint, tls=token_tls)
            )
            resources.callback(token_client.close)
            auth = DelegatedTokenAuth(delegation, http_client=token_client)
        else:
            auth = bearer_auth(setting("TEMPLATECONNECTOR_API_TOKEN_REF", ""))
        client = ApiClientSystem(
            base_url=base_url, auth=auth, tls_profile=tls,
            allow_plaintext=setting("TEMPLATECONNECTOR_API_ALLOW_PLAINTEXT", False),
        )
        resources.callback(client.close)
        _resources = resources.pop_all()
        _client = client
    return _client


def close_client() -> None:
    """Release the cached client and any materialized TLS resources."""
    global _client
    try:
        _resources.close()
    finally:
        _client = None
