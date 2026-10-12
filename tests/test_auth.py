
from unittest.mock import MagicMock, patch

import httpx
import pytest
from agent_connector_sdk.auth.delegation import DelegatedTokenAuth
from agent_connector_sdk.credentials.references import SecretReferenceError

import immich_api.auth as auth_module


@pytest.fixture(autouse=True)
def configured_client(monkeypatch):
    auth_module.close_client()
    monkeypatch.setattr(auth_module, "load_config", lambda: None)
    monkeypatch.setenv("IMMICH_API_BASE_URL", "https://service.example.invalid")
    monkeypatch.setenv("IMMICH_API_TOKEN_REF", "env://SCAFFOLD_TEST_TOKEN")
    monkeypatch.setenv("SCAFFOLD_TEST_TOKEN", "test-token")
    monkeypatch.setenv("ENABLE_DELEGATION", "false")
    monkeypatch.delenv("IMMICH_API_ALLOW_PLAINTEXT", raising=False)
    yield
    auth_module.close_client()


@pytest.mark.concept("IMMICH-001")
def test_client_resolves_reference_and_cleans_up():
    tls = MagicMock()
    with (
        patch.object(auth_module, "resolve_tls_profile", return_value=tls),
        patch.object(auth_module, "ApiClientSystem") as client_cls,
    ):
        client = auth_module.get_client()
        assert auth_module.get_client() is client
        kwargs = client_cls.call_args.kwargs
        request = httpx.Request("GET", "https://service.example.invalid")
        authorized = next(kwargs["auth"].auth_flow(request))
        assert authorized.headers["Authorization"] == "Bearer test-token"
        assert "test-token" not in repr(kwargs["auth"])
        assert "token" not in kwargs
        assert kwargs["allow_plaintext"] is False
        auth_module.close_client()
        client.close.assert_called_once()
        tls.cleanup.assert_called_once()


@pytest.mark.parametrize("value, expected", [("true", True), ("false", False)])
def test_plaintext_setting_is_explicit(monkeypatch, value, expected):
    monkeypatch.setenv("IMMICH_API_ALLOW_PLAINTEXT", value)
    with (
        patch.object(auth_module, "resolve_tls_profile") as profile,
        patch.object(auth_module, "ApiClientSystem") as client_cls,
    ):
        auth_module.get_client()
        assert client_cls.call_args.kwargs["allow_plaintext"] is expected
        assert client_cls.call_args.kwargs["tls_profile"] is profile.return_value


def test_literal_credential_rejected_and_tls_cleaned(monkeypatch):
    monkeypatch.setenv("IMMICH_API_TOKEN_REF", "not-a-reference")
    tls = MagicMock()
    with patch.object(auth_module, "resolve_tls_profile", return_value=tls):
        with pytest.raises(SecretReferenceError):
            auth_module.get_client()
    tls.cleanup.assert_called_once()
    assert auth_module._client is None


def test_failed_client_creation_cleans_tls():
    tls = MagicMock()
    with (
        patch.object(auth_module, "resolve_tls_profile", return_value=tls),
        patch.object(auth_module, "ApiClientSystem", side_effect=ValueError("invalid")),
        pytest.raises(ValueError, match="invalid"),
    ):
        auth_module.get_client()
    tls.cleanup.assert_called_once()
    assert auth_module._client is None


def test_delegation_uses_per_request_auth(monkeypatch):
    monkeypatch.setenv("ENABLE_DELEGATION", "true")
    monkeypatch.setenv("OIDC_TOKEN_URL", "https://identity.example.invalid/token")
    monkeypatch.setenv("OIDC_CLIENT_ID", "test-client")
    monkeypatch.setenv("OIDC_CLIENT_SECRET_REF", "env://SCAFFOLD_TEST_TOKEN")
    monkeypatch.setenv("AUDIENCE", "test-service")
    token_client = MagicMock()
    tls = MagicMock()
    with (
        patch.object(auth_module, "resolve_tls_profile", return_value=tls),
        patch.object(auth_module, "create_http_client", return_value=token_client),
        patch.object(auth_module, "ApiClientSystem") as client_cls,
        patch.object(auth_module, "bearer_auth") as fixed_auth,
    ):
        auth_module.get_client()
        assert isinstance(client_cls.call_args.kwargs["auth"], DelegatedTokenAuth)
        fixed_auth.assert_not_called()
        auth_module.close_client()
        token_client.close.assert_called_once()
