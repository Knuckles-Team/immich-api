"""Expose the source-proven mobile redirect as data, never as another request."""

import hashlib
import json
from pathlib import Path

import httpx
import pytest
from fastmcp import Client
from mcp.shared.exceptions import MCPError

import immich_api.auth as auth
from immich_api.api import ApiClientSystem
from tests.parity_support import DiscoveredClient, bounded_server

ACTION = "redirectOAuthToMobile"
LOCATION = "app.immich:///oauth-callback?code=synthetic-code&state=synthetic-state"
EXPECTED = {
    "action": ACTION,
    "status": 307,
    "content_type": "",
    "data": {"location": LOCATION},
}
pytestmark = [
    pytest.mark.concept("IMMICH-001"),
    pytest.mark.spec("CONN-IMMICH-API-R006"),
]


@pytest.fixture
def redirect_provider():
    clients = []

    def create(*, status=307, headers=None, content=b"Redirecting"):
        requests = []

        def respond(request):
            requests.append(request)
            return httpx.Response(
                status,
                headers={"location": LOCATION} if headers is None else headers,
                content=content,
            )

        client = ApiClientSystem(
            base_url="https://service.example.invalid",
            auth=httpx.Auth(),
            transport=httpx.MockTransport(respond),
        )
        clients.append(client)
        return client, requests

    yield create
    for client in clients:
        client.close()


def test_original_upstream_redirect_evidence_remains_unchanged():
    root = Path(__file__).resolve().parents[1]
    controller = (
        root / "api-spec/provider-source/server/src/controllers/oauth.controller.ts"
    )
    assert hashlib.sha256(controller.read_bytes()).hexdigest() == (
        "bfb11532d958f5c0824b17163c203fb3acf6b9e85a83ea219d008c191a586614"
    )
    raw = json.loads((root / "api-spec/immich.openapi.json").read_text())
    assert set(raw["paths"]["/oauth/mobile-redirect"]["get"]["responses"]) == {"200"}


@pytest.mark.parametrize("body", [b"", b"Temporary Redirect", b"<a>Redirecting</a>"])
def test_api_returns_verified_location_without_following(redirect_provider, body):
    client, requests = redirect_provider(content=body)
    assert client.execute("authentication", {"action": ACTION}) == EXPECTED
    assert len(requests) == 1
    assert (
        requests[0].url == "https://service.example.invalid/api/oauth/mobile-redirect"
    )
    assert not client.session.follow_redirects


@pytest.mark.parametrize("status", [200, 301, 302, 303, 308])
def test_other_statuses_are_not_admitted_by_redirect_correction(
    redirect_provider, status
):
    client, requests = redirect_provider(status=status, content=b"")
    with pytest.raises((ValueError, RuntimeError)):
        client.execute("authentication", {"action": ACTION})
    assert len(requests) == 1


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"location": ""},
        {"location": "relative/path"},
        {"location": "app.immich:///oauth-callback\r\nx-injected: value"},
        [("location", LOCATION), ("location", LOCATION)],
    ],
)
def test_location_must_be_one_valid_value(redirect_provider, headers):
    client, requests = redirect_provider(headers=headers)
    with pytest.raises((ValueError, RuntimeError, httpx.RemoteProtocolError)):
        client.execute("authentication", {"action": ACTION})
    assert len(requests) == 1


def test_unrelated_operation_still_rejects_307(redirect_provider):
    client, requests = redirect_provider()
    with pytest.raises(RuntimeError, match="307"):
        client.execute("server", {"action": "pingServer"})
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_native_mcp_exposes_verified_redirect_data(
    redirect_provider, monkeypatch
):
    provider, requests = redirect_provider()
    monkeypatch.setattr(auth, "_client", provider)
    async with Client(bounded_server()) as native:
        result = await DiscoveredClient(native).call_tool(
            "authentication_operations", {"action": ACTION}
        )
    assert result.structured_content == EXPECTED
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_native_mcp_rejects_unrelated_redirect(redirect_provider, monkeypatch):
    provider, requests = redirect_provider()
    monkeypatch.setattr(auth, "_client", provider)
    async with Client(bounded_server()) as native:
        with pytest.raises(MCPError):
            await DiscoveredClient(native).call_tool(
                "server_operations", {"action": "pingServer"}
            )
    assert len(requests) == 1
