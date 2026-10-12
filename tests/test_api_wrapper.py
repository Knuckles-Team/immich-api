"""Transport controls through the production ApiClientSystem/OpenApiClient path."""

import ssl

import httpx
import pytest
from agent_connector_sdk.auth.static import bearer_auth
from agent_connector_sdk.tls.errors import TransportSecurityError
from agent_connector_sdk.tls.resolve import resolve_tls_profile

from immich_api import openapi_runtime
from immich_api.api import ApiClientSystem


@pytest.fixture
def client_factory(monkeypatch):
    monkeypatch.setenv("IMMICH_TEST_TOKEN", "test-token")
    clients = []

    def create(
        handler, base_url="https://service.example.invalid", *, allow_plaintext=False
    ):
        client = ApiClientSystem(
            base_url=base_url,
            auth=bearer_auth("env://IMMICH_TEST_TOKEN"),
            credential_scheme="bearer",
            transport=httpx.MockTransport(handler),
            allow_plaintext=allow_plaintext,
        )
        clients.append(client)
        return client

    yield create
    for client in clients:
        client.close()


def ping(client):
    return client.execute("server", {"action": "pingServer"})


@pytest.mark.concept("IMMICH-001")
def test_declared_operation_uses_real_client_and_sdk_auth(client_factory):
    def respond(request):
        assert request.method == "GET"
        assert request.url == httpx.URL(
            "https://service.example.invalid/api/server/ping"
        )
        assert request.headers["Authorization"] == "Bearer test-token"
        assert all(value == 30.0 for value in request.extensions["timeout"].values())
        return httpx.Response(200, json={"res": "pong"})

    client = client_factory(respond)
    assert isinstance(client, openapi_runtime.OpenApiClient)
    assert ping(client)["data"] == {"res": "pong"}
    assert not client.session.follow_redirects
    assert not client.session.trust_env


@pytest.mark.parametrize(
    "target",
    [
        "https://other.example.invalid/api/server/ping",
        "//other.example.invalid/api/server/ping",
        "https://service.example.invalid:8443/api/server/ping",
    ],
)
def test_catalog_cannot_escape_provider_origin(client_factory, monkeypatch, target):
    calls = []
    client = client_factory(lambda request: calls.append(request))
    monkeypatch.setitem(
        openapi_runtime.CONTRACT["operations"]["pingServer"], "path", target
    )
    with pytest.raises(ValueError, match="origin"):
        ping(client)
    assert not calls


@pytest.mark.parametrize(
    "arguments",
    [
        {"action": "pingServer", "url": "https://other.example.invalid"},
        {"action": "pingServer", "method": "DELETE"},
        {"action": "pingServer", "follow_redirects": True},
        {"action": "pingServer", "timeout": None},
    ],
)
def test_arbitrary_dispatch_or_safety_overrides_rejected(client_factory, arguments):
    calls = []
    client = client_factory(lambda request: calls.append(request))
    with pytest.raises(ValueError, match="schema"):
        client.execute("server", arguments)
    assert not calls


@pytest.mark.parametrize("status", (302, 429, 503))
def test_redirect_and_provider_errors_are_not_retried(client_factory, status):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(
            status, headers={"location": "https://other.example.invalid"}
        )

    client = client_factory(respond)
    with pytest.raises(RuntimeError, match=f"HTTP {status}"):
        ping(client)
    assert len(calls) == 1


def test_writes_disabled_before_http(client_factory):
    calls = []
    client = client_factory(lambda request: calls.append(request))
    with pytest.raises(PermissionError, match="Writes"):
        client.execute(
            "albums", {"action": "createAlbum", "body": {"albumName": "fixture"}}
        )
    assert not calls


def test_plaintext_remote_rejected(client_factory):
    with pytest.raises(ValueError, match="plaintext"):
        client_factory(
            lambda request: httpx.Response(200), "http://service.example.invalid"
        )


def test_plaintext_opt_in_uses_only_configured_origin(client_factory, monkeypatch):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(200, json={"res": "pong"})

    client = client_factory(
        respond, "http://service.example.invalid", allow_plaintext=True
    )
    assert ping(client)["data"] == {"res": "pong"}
    assert calls[0].url.scheme == "http"
    monkeypatch.setitem(
        openapi_runtime.CONTRACT["operations"]["pingServer"],
        "path",
        "https://service.example.invalid/api/server/ping",
    )
    with pytest.raises(ValueError, match="origin"):
        ping(client)
    assert len(calls) == 1


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
        ping(client)
    assert len(calls) == 1 and calls[0].url.scheme == "https"


def test_tls_cannot_disable_verification():
    with pytest.raises(TransportSecurityError):
        resolve_tls_profile("immich-api", profile={"verify": False})
    profile = resolve_tls_profile("immich-api", profile={"trust_env": False})
    try:
        assert profile.ssl_context.verify_mode == ssl.CERT_REQUIRED
        assert profile.ssl_context.check_hostname
    finally:
        profile.cleanup()


def test_oversized_and_chunked_responses_rejected(client_factory, monkeypatch):
    class Chunks(httpx.SyncByteStream):
        def __iter__(self):
            yield b"first"
            yield b"second"

    monkeypatch.setattr(openapi_runtime, "MAX_BYTES", 8)
    for respond in (
        lambda request: httpx.Response(200, content=b"too large"),
        lambda request: httpx.Response(200, stream=Chunks()),
    ):
        with pytest.raises(RuntimeError, match="response limit"):
            ping(client_factory(respond))


def test_response_deadline_enforced(client_factory, monkeypatch):
    class SlowChunk(httpx.SyncByteStream):
        def __iter__(self):
            monkeypatch.setattr(openapi_runtime.time, "monotonic", lambda: float("inf"))
            yield b"late"

    with pytest.raises(RuntimeError, match="response limit"):
        ping(client_factory(lambda request: httpx.Response(200, stream=SlowChunk())))
