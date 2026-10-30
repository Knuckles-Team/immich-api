"""A shared provider client must never acquire a caller's login session."""

import copy

import httpx
import pytest
from fastmcp import Client
from scion_sdk.http.client import create_http_client as sdk_http_client

import immich_api.auth as auth
import immich_api.openapi_runtime as runtime
from tests.operation_fixtures import CASES, response_for
from tests.parity_support import DiscoveredClient, bounded_server

pytestmark = [
    pytest.mark.concept("IMMICH-001"),
    pytest.mark.spec("CONN-IMMICH-API-R006"),
]


class SessionProvider:
    """Model the pinned provider's session-before-API-key precedence."""

    def __init__(self):
        self.requests = []
        self.identities = []
        self.actions = {
            operation["path"]: action
            for action, operation in runtime.CONTRACT["operations"].items()
            if action in {"login", "finishOAuth", "getMyUser"}
        }

    def respond(self, request):
        self.requests.append(request)
        action = self.actions[request.url.path]
        operation = runtime.CONTRACT["operations"][action]
        expected = copy.deepcopy(CASES[action]["result"])
        if action == "getMyUser":
            identity = "session" if "cookie" in request.headers else "api-key"
            self.identities.append(identity)
            if identity == "session":
                expected["data"]["id"] = "10000000-0000-4000-8000-000000000000"
        response = response_for(operation, expected)
        if action in {"login", "finishOAuth"}:
            response.headers["set-cookie"] = (
                "immich_access_token=synthetic-session; Path=/; Secure; HttpOnly"
            )
        return response


@pytest.fixture
def shared_provider(monkeypatch):
    auth.close_client()
    monkeypatch.setattr(auth, "load_config", lambda: None)
    settings = {
        "IMMICH_API_BASE_URL": "https://service.example.invalid",
        "IMMICH_API_AUTH_SCHEME": "api_key",
        "IMMICH_API_TOKEN_REF": "env://IMMICH_ISOLATION_TEST_TOKEN",
        "IMMICH_ISOLATION_TEST_TOKEN": "synthetic-scoped-key",
        "IMMICH_API_ALLOW_WRITES": "true",
        "IMMICH_API_ALLOW_PLAINTEXT": "false",
        "ENABLE_DELEGATION": "false",
    }
    for name, value in settings.items():
        monkeypatch.setenv(name, value)
    provider = SessionProvider()
    monkeypatch.setattr(
        runtime,
        "create_http_client",
        lambda options, **kwargs: sdk_http_client(
            options, transport=httpx.MockTransport(provider.respond)
        ),
    )
    yield provider
    auth.close_client()


def assert_configured_identity(provider, result):
    assert provider.identities == ["api-key"]
    assert result == CASES["getMyUser"]["result"]
    assert len(provider.requests) == 2
    assert all(
        request.headers["x-api-key"] == "synthetic-scoped-key"
        for request in provider.requests
    )
    assert all("cookie" not in request.headers for request in provider.requests)
    assert not list(auth.get_client().session.cookies.jar)


@pytest.mark.parametrize("action", ["login", "finishOAuth"])
def test_session_response_cannot_replace_configured_api_key(shared_provider, action):
    client = auth.get_client()
    assert (
        client.execute("authentication", CASES[action]["arguments"])
        == CASES[action]["result"]
    )
    result = client.execute("users", CASES["getMyUser"]["arguments"])
    assert_configured_identity(shared_provider, result)


@pytest.mark.asyncio
@pytest.mark.parametrize("action", ["login", "finishOAuth"])
async def test_native_callers_cannot_share_provider_session(shared_provider, action):
    confirmations = []

    async def consent(message, response_type, params, context):
        confirmations.append(message)
        return {"confirmed": True}

    server = bounded_server()
    async with Client(server, elicitation_handler=consent) as caller_a:
        logged_in = await DiscoveredClient(caller_a).call_tool(
            "authentication_operations", CASES[action]["arguments"]
        )
        assert logged_in.structured_content == CASES[action]["result"]
        shared_client = auth.get_client()
        async with Client(server) as caller_b:
            result = await DiscoveredClient(caller_b).call_tool(
                "users_operations", CASES["getMyUser"]["arguments"]
            )
            assert auth.get_client() is shared_client
    assert confirmations == [f"Are you sure you want to {action}?"]
    assert_configured_identity(shared_provider, result.structured_content)
