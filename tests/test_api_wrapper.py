
import ssl

import httpx
import pytest
from agent_connector_sdk.auth.static import bearer_auth
from agent_connector_sdk.tls.errors import TransportSecurityError
from agent_connector_sdk.tls.resolve import resolve_tls_profile

from immich_api.api import ApiClientBase
from immich_api.api import api_client_base


@pytest.fixture
def client_factory(monkeypatch):
    monkeypatch.setenv("SCAFFOLD_TEST_TOKEN", "test-token")
    clients = []

    def create(handler, base_url="https://service.example.invalid", *, allow_plaintext=False):
        client = ApiClientBase(
            base_url=base_url,
            auth=bearer_auth("env://SCAFFOLD_TEST_TOKEN"),
            transport=httpx.MockTransport(handler),
            allow_plaintext=allow_plaintext,
        )
        clients.append(client)
        return client

    yield create
    for client in clients:
        client.close()


@pytest.mark.concept("IMMICH-001")
def test_request_returns_json_and_uses_sdk_auth(client_factory):
    def respond(request):
        assert request.url == httpx.URL("https://service.example.invalid/health")
        assert request.headers["Authorization"] == "Bearer test-token"
        assert all(value == 30.0 for value in request.extensions["timeout"].values())
        return httpx.Response(200, json={"ok": True})

    client = client_factory(respond)
    assert client.request("GET", "/health") == {"ok": True}
    assert client.session.follow_redirects is False
    assert client.session.trust_env is False


@pytest.mark.parametrize("path", [
    "https://other.example.invalid/health",
    "//other.example.invalid/health",
    "https://user:secret@service.example.invalid/health",
    "https://service.example.invalid:8443/health",
])
def test_request_rejects_origin_or_credentials(client_factory, path):
    calls = []
    client = client_factory(lambda request: calls.append(request))
    with pytest.raises(ValueError, match="API path"):
        client.request("GET", path)
    assert not calls


def test_redirect_not_followed(client_factory):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(302, headers={"location": "https://other.example.invalid"})

    client = client_factory(respond)
    with pytest.raises(httpx.HTTPStatusError):
        client.request("GET", "/health")
    assert len(calls) == 1


@pytest.mark.parametrize("options", [{"follow_redirects": True}, {"timeout": None}])
def test_request_rejects_safety_overrides(client_factory, options):
    client = client_factory(lambda request: httpx.Response(200, json={}))
    with pytest.raises(ValueError):
        client.request("GET", "/health", **options)


def test_plaintext_remote_rejected(client_factory):
    with pytest.raises(ValueError, match="plaintext"):
        client_factory(lambda request: httpx.Response(200), "http://service.example.invalid")


def test_plaintext_opt_in_stays_on_configured_origin(client_factory):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(200, json={"ok": True})

    client = client_factory(
        respond, "http://service.example.invalid", allow_plaintext=True
    )
    assert client.request("GET", "/health") == {"ok": True}
    assert calls[0].url.scheme == "http"
    for target in ("http://other.example.invalid/health", "https://service.example.invalid/health"):
        with pytest.raises(ValueError, match="API path"):
            client.request("GET", target)
    assert len(calls) == 1
    assert client.session.follow_redirects is False


def test_plaintext_opt_in_does_not_downgrade_https(client_factory):
    calls = []

    def fail_tls(request):
        calls.append(request)
        try:
            raise ssl.SSLCertVerificationError("certificate verification failed")
        except ssl.SSLCertVerificationError as exc:
            raise httpx.ConnectError("TLS handshake failed", request=request) from exc

    from agent_connector_sdk.http.errors import TlsVerificationError

    client = client_factory(fail_tls, allow_plaintext=True)
    with pytest.raises(TlsVerificationError):
        client.request("GET", "/health")
    assert len(calls) == 1
    assert calls[0].url.scheme == "https"


def test_tls_cannot_disable_verification():
    with pytest.raises(TransportSecurityError):
        resolve_tls_profile("immich", profile={"verify": False})
    profile = resolve_tls_profile("immich", profile={"trust_env": False})
    try:
        assert profile.ssl_context.verify_mode == ssl.CERT_REQUIRED
        assert profile.ssl_context.check_hostname
        assert profile.ssl_context.minimum_version >= ssl.TLSVersion.TLSv1_2
    finally:
        profile.cleanup()


def test_oversized_response_rejected(client_factory, monkeypatch):
    monkeypatch.setattr(api_client_base, "_MAX_RESPONSE_BYTES", 8)
    client = client_factory(lambda request: httpx.Response(200, content=b"too large"))
    with pytest.raises(RuntimeError, match="size limit"):
        client.request("GET", "/health")


def test_stream_without_length_still_bounded(client_factory, monkeypatch):
    class Chunks(httpx.SyncByteStream):
        def __iter__(self):
            yield b"first"
            yield b"second"

    monkeypatch.setattr(api_client_base, "_MAX_RESPONSE_BYTES", 8)
    client = client_factory(lambda request: httpx.Response(200, stream=Chunks()))
    with pytest.raises(RuntimeError, match="size limit"):
        client.request("GET", "/health")


def test_response_deadline_enforced(client_factory, monkeypatch):
    class SlowChunk(httpx.SyncByteStream):
        def __iter__(self):
            monkeypatch.setattr(api_client_base.time, "monotonic", lambda: float("inf"))
            yield b"late"

    client = client_factory(lambda request: httpx.Response(200, stream=SlowChunk()))
    with pytest.raises(RuntimeError, match="time limit"):
        client.request("GET", "/health")
