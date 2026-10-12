"""Resolve provider credentials and delegated caller auth through canonical SDK APIs."""

from contextlib import ExitStack

import httpx
from agent_connector_sdk.auth.delegation import DelegatedTokenAuth, DelegationSettings
from agent_connector_sdk.auth.static import api_key_auth, bearer_auth
from agent_connector_sdk.config import load_config, setting
from agent_connector_sdk.http.client import create_http_client
from agent_connector_sdk.http.options import HttpClientOptions
from agent_connector_sdk.tls.resolve import resolve_tls_profile

from .api import ApiClientSystem
from .openapi_runtime import CONTRACT

_client = None
_resources = ExitStack()


def get_client():
    """Build one client; delegated auth resolves the verified caller per request."""
    global _client, _resources
    if _client is not None:
        return _client
    load_config()
    base_url = setting("IMMICH_API_BASE_URL", "")
    if not base_url:
        raise ValueError("Provider base URL is required")
    scheme = setting("IMMICH_API_AUTH_SCHEME", "api_key")
    definition = CONTRACT["security_schemes"].get(scheme, {})
    is_bearer = (
        definition.get("type") == "http"
        and definition.get("scheme", "").lower() == "bearer"
    )
    with ExitStack() as resources:
        tls = resolve_tls_profile("immich-api")
        resources.callback(tls.cleanup)
        delegation = DelegationSettings.from_settings()
        credential_scheme = None
        if delegation.enabled:
            if not is_bearer:
                raise ValueError("Delegation requires a declared HTTP bearer auth scheme")
            token_tls = resolve_tls_profile("oidc")
            resources.callback(token_tls.cleanup)
            token_client = create_http_client(
                HttpClientOptions(base_url=delegation.token_endpoint, tls=token_tls)
            )
            resources.callback(token_client.close)
            auth = DelegatedTokenAuth(delegation, http_client=token_client)
            credential_scheme = scheme
        else:
            reference = setting("IMMICH_API_TOKEN_REF", "")
            auth = httpx.Auth()
            if reference:
                if definition.get("type") == "apiKey" and definition.get("in") == "header":
                    auth = api_key_auth(reference, header=definition["name"])
                elif is_bearer:
                    auth = bearer_auth(reference)
                else:
                    raise ValueError("Unsupported provider authentication scheme")
                credential_scheme = scheme
        client = ApiClientSystem(
            base_url=base_url,
            auth=auth,
            tls_profile=tls,
            credential_scheme=credential_scheme,
            allow_writes=setting("IMMICH_API_ALLOW_WRITES", False),
            allow_plaintext=setting("IMMICH_API_ALLOW_PLAINTEXT", False),
        )
        resources.callback(client.close)
        _resources = resources.pop_all()
        _client = client
    return client


def close_client():
    """Close the cached client, token client and materialized TLS resources."""
    global _client
    try:
        _resources.close()
    finally:
        _client = None
