"""Small mocked-transport checks for the generated Immich auth adapter."""

from unittest.mock import MagicMock

import httpx
import pytest
from scion_sdk.credentials.references import SecretReferenceError
from scion_sdk.http.client import create_http_client as sdk_http_client

import immich_api.auth as auth
import immich_api.openapi_runtime as runtime


@pytest.fixture(autouse=True)
def configured(monkeypatch):
    auth.close_client()
    monkeypatch.setattr(auth, "load_config", lambda: None)
    for key, value in {
        "IMMICH_API_BASE_URL": "https://service.example.invalid",
        "IMMICH_API_AUTH_SCHEME": "api_key",
        "IMMICH_API_TOKEN_REF": "env://AUTH_FOLLOWUP_TEST_TOKEN",
        "AUTH_FOLLOWUP_TEST_TOKEN": "fixture-token",
        "IMMICH_API_ALLOW_PLAINTEXT": "false",
        "IMMICH_API_ALLOW_WRITES": "false",
        "ENABLE_DELEGATION": "false",
        "OIDC_TOKEN_URL": "https://identity.example.invalid/token",
        "OIDC_CLIENT_ID": "fixture-client",
        "OIDC_CLIENT_SECRET_REF": "env://AUTH_FOLLOWUP_TEST_TOKEN",
        "AUDIENCE": "fixture-service",
    }.items():
        monkeypatch.setenv(key, value)
    yield
    auth.close_client()


@pytest.fixture
def vendor(monkeypatch):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"res": "pong"})

    monkeypatch.setattr(
        runtime,
        "create_http_client",
        lambda options, **kwargs: sdk_http_client(
            options, transport=httpx.MockTransport(handler)
        ),
    )
    return seen


def test_api_key_factory_uses_sdk_and_bound_operation(vendor):
    client = auth.get_client()
    assert isinstance(client, runtime.OpenApiClient)
    assert client.credential_scheme == "api_key"
    result = client.execute("server", {"action": "pingServer"})
    assert result["data"] == {"res": "pong"}
    assert len(vendor) == 1
    assert vendor[0].headers["x-api-key"] == "fixture-token"
    assert "authorization" not in vendor[0].headers
    assert str(vendor[0].url) == "https://service.example.invalid/api/server/ping"


def test_public_factory_refuses_protected_operation(monkeypatch, vendor):
    monkeypatch.setenv("IMMICH_API_TOKEN_REF", "")
    client = auth.get_client()
    client.execute("server", {"action": "pingServer"})
    assert "x-api-key" not in vendor[0].headers
    assert "authorization" not in vendor[0].headers
    monkeypatch.setitem(
        runtime.CONTRACT["operations"]["pingServer"], "security", [{"api_key": []}]
    )
    with pytest.raises(PermissionError):
        client.execute("server", {"action": "pingServer"})
    assert len(vendor) == 1


def test_delegation_requires_declared_bearer_and_cleans_tls(monkeypatch):
    monkeypatch.setenv("ENABLE_DELEGATION", "true")
    tls = MagicMock()
    monkeypatch.setattr(auth, "resolve_tls_profile", lambda _: tls)
    with pytest.raises(ValueError, match="declared HTTP bearer"):
        auth.get_client()
    tls.cleanup.assert_called_once()
    assert auth._client is None


def test_vendor_http_opt_in_never_enables_plaintext_token_exchange(monkeypatch):
    monkeypatch.setenv("ENABLE_DELEGATION", "true")
    monkeypatch.setenv("IMMICH_API_AUTH_SCHEME", "bearer")
    monkeypatch.setenv("IMMICH_API_ALLOW_PLAINTEXT", "true")
    monkeypatch.setenv("OIDC_TOKEN_URL", "http://identity.example.invalid/token")
    vendor_tls, token_tls = MagicMock(), MagicMock()
    monkeypatch.setattr(
        auth,
        "resolve_tls_profile",
        lambda name: token_tls if name == "oidc" else vendor_tls,
    )
    with pytest.raises(ValueError, match="allow_plaintext"):
        auth.get_client()
    vendor_tls.cleanup.assert_called_once()
    token_tls.cleanup.assert_called_once()
    assert auth._client is None


def test_failed_delegated_factory_closes_all_resources(monkeypatch):
    monkeypatch.setenv("ENABLE_DELEGATION", "true")
    monkeypatch.setenv("IMMICH_API_AUTH_SCHEME", "bearer")
    vendor_tls, token_tls, token_client = MagicMock(), MagicMock(), MagicMock()
    monkeypatch.setattr(
        auth,
        "resolve_tls_profile",
        lambda name: token_tls if name == "oidc" else vendor_tls,
    )
    monkeypatch.setattr(auth, "create_http_client", lambda options: token_client)

    def fail(**kwargs):
        raise ValueError("factory failure")

    monkeypatch.setattr(auth, "ApiClientSystem", fail)
    with pytest.raises(ValueError, match="factory failure"):
        auth.get_client()
    vendor_tls.cleanup.assert_called_once()
    token_tls.cleanup.assert_called_once()
    token_client.close.assert_called_once()
    assert auth._client is None


def test_api_key_literal_rejected_with_tls_cleanup(monkeypatch):
    monkeypatch.setenv("IMMICH_API_TOKEN_REF", "not-a-reference")
    tls = MagicMock()
    monkeypatch.setattr(auth, "resolve_tls_profile", lambda _: tls)
    with pytest.raises(SecretReferenceError):
        auth.get_client()
    tls.cleanup.assert_called_once()
    assert auth._client is None


def test_failed_factory_can_recover_without_cached_credentials(monkeypatch, vendor):
    monkeypatch.setenv("IMMICH_API_TOKEN_REF", "not-a-reference")
    with pytest.raises(SecretReferenceError):
        auth.get_client()
    monkeypatch.setenv("IMMICH_API_TOKEN_REF", "env://AUTH_FOLLOWUP_TEST_TOKEN")
    client = auth.get_client()
    client.execute("server", {"action": "pingServer"})
    assert len(vendor) == 1
    assert vendor[0].headers["x-api-key"] == "fixture-token"
