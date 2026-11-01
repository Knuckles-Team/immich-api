"""Destructive writes over real transports: refuse cleanly, then accept confirm=true."""

import asyncio
import base64
import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import httpx
import pytest
from fastmcp import Client
from fastmcp.client.transports import StdioTransport, StreamableHttpTransport
from fastmcp.server.auth.providers.jwt import RSAKeyPair

from tests.operation_fixtures import CASES

pytestmark = [
    pytest.mark.concept("IMMICH-001"),
    pytest.mark.spec("CONN-IMMICH-API-R009.3"),
]

ISSUER = "https://idp.example.invalid/realms/homelab"
AUDIENCE = "agent-services"
ACTION = "createAlbum"
CASE = CASES[ACTION]
CALL_TIMEOUT = 60


class Upstream:
    """A fake Immich that records every request it receives."""

    def __init__(self):
        self.requests = []
        body = json.dumps(CASE["result"]["data"]).encode()
        status = CASE["result"]["status"]
        requests = self.requests

        class Handler(BaseHTTPRequestHandler):
            def _answer(self):
                length = int(self.headers.get("content-length") or 0)
                self.rfile.read(length)
                requests.append((self.command, self.path))
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            do_GET = do_POST = do_PUT = do_DELETE = _answer

            def log_message(self, *_args):
                return

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def writes(self):
        return [item for item in self.requests if item[0] != "GET"]


def jwks(keys):
    from cryptography.hazmat.primitives import serialization

    numbers = serialization.load_pem_public_key(
        keys.public_key.encode()
    ).public_numbers()

    def b64(value):
        raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    return {
        "keys": [
            {
                "kty": "RSA",
                "kid": "test-key",
                "use": "sig",
                "alg": "RS256",
                "n": b64(numbers.n),
                "e": b64(numbers.e),
            }
        ]
    }


def serve_jwks(document):
    body = json.dumps(document).encode()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            return

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/jwks"


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def executable():
    found = Path(sys.executable).parent / "immich-mcp"
    return str(found) if found.exists() else shutil.which("immich-mcp") or ""


def server_env(upstream):
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("IMMICH_", "AUTH_", "FASTMCP_", "CONNECTOR_", "MCP_"))
    }
    env.update(
        IMMICH_API_BASE_URL=upstream.url,
        IMMICH_API_ALLOW_PLAINTEXT="true",
        IMMICH_API_ALLOW_WRITES="true",
        IMMICH_API_AUTH_SCHEME="api_key",
        IMMICH_API_TOKEN_REF="env://IMMICH_TRANSPORT_TEST_KEY",
        IMMICH_TRANSPORT_TEST_KEY="synthetic-scoped-key",
        MCP_FLEET_REGISTRATION="false",
        PYTHONUNBUFFERED="1",
    )
    return env


class HttpServer:
    def __init__(self, argv, env, port, log_dir):
        self.url = f"http://127.0.0.1:{port}/mcp"
        self.log = (log_dir / f"server-{port}.log").open("w+")
        self.proc = subprocess.Popen(
            [executable(), *argv, "--port", str(port)],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=self.log,
        )
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if self.proc.poll() is not None:
                raise AssertionError("server exited early")
            try:
                httpx.get(f"http://127.0.0.1:{port}/health", timeout=1)
                return
            except httpx.HTTPError:
                time.sleep(0.2)
        raise AssertionError("server did not start")

    def stop(self):
        self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()
        self.log.close()


@pytest.fixture(scope="module")
def keys():
    pair = RSAKeyPair.generate()
    server, uri = serve_jwks(jwks(pair))
    yield pair, uri
    server.shutdown()


@pytest.fixture
def upstream():
    fake = Upstream()
    yield fake
    fake.server.shutdown()


async def accept(message, response_type, params, context):
    return response_type(confirmed=True) if response_type else None


async def destructive_flow(open_client, upstream, *, elicits):
    kwargs = {"timeout": CALL_TIMEOUT}
    if elicits:
        kwargs["elicitation_handler"] = accept
    async with open_client(**kwargs) as client:
        if elicits:
            done = await client.call_tool(
                "albums_operations", CASE["arguments"], raise_on_error=False
            )
            assert not done.is_error, done.content
            assert len(upstream.writes()) == 1
            return
        refused = await client.call_tool(
            "albums_operations", CASE["arguments"], raise_on_error=False
        )
        assert not refused.is_error, refused.content
        assert refused.structured_content["cancelled"] is True
        assert refused.structured_content["operation"] == ACTION
        assert "confirm=true" in refused.structured_content["reason"]
        assert not upstream.writes(), "an unconfirmed write must not reach upstream"
        await asyncio.sleep(0.3)
        confirmed = await client.call_tool(
            "albums_operations",
            {**CASE["arguments"], "confirm": True},
            raise_on_error=False,
        )
        assert not confirmed.is_error, confirmed.content
        assert confirmed.structured_content["status"] == CASE["result"]["status"]
        assert len(upstream.writes()) == 1
        assert upstream.writes()[0][0] == "POST"


@pytest.mark.timeout(300)
@pytest.mark.parametrize("elicits", [False, True])
async def test_stdio_no_auth_destructive_call(upstream, elicits):
    def open_client(**kwargs):
        transport = StdioTransport(
            command=executable(),
            args=["--transport", "stdio"],
            env=server_env(upstream),
        )
        return Client(transport, **kwargs)

    await destructive_flow(open_client, upstream, elicits=elicits)


@pytest.mark.timeout(300)
@pytest.mark.parametrize("elicits", [False, True])
async def test_http_no_auth_destructive_call(upstream, tmp_path, elicits):
    port = free_port()
    server = HttpServer(
        [
            "--transport",
            "streamable-http",
            "--auth-type",
            "none",
            "--host",
            "127.0.0.1",
            "--allowed-hosts",
            f"127.0.0.1:{port},localhost:{port}",
        ],
        server_env(upstream),
        port,
        tmp_path,
    )
    try:
        await destructive_flow(
            lambda **kw: Client(StreamableHttpTransport(server.url), **kw),
            upstream,
            elicits=elicits,
        )
    finally:
        server.stop()


@pytest.mark.timeout(300)
@pytest.mark.parametrize("elicits", [False, True])
async def test_http_jwt_destructive_call(upstream, keys, tmp_path, elicits):
    pair, uri = keys
    port = free_port()
    token = pair.create_token(
        subject="arbora-service-account-id",
        issuer=ISSUER,
        audience=AUDIENCE,
        additional_claims={
            "azp": "arbora",
            "client_id": "arbora",
            "tenant_id": "homelab",
        },
        kid="test-key",
    )
    server = HttpServer(
        [
            "--transport",
            "streamable-http",
            "--auth-type",
            "jwt",
            "--host",
            "127.0.0.1",
            "--token-issuer",
            ISSUER,
            "--token-audience",
            AUDIENCE,
            "--token-jwks-uri",
            uri,
            "--allowed-hosts",
            f"127.0.0.1:{port},localhost:{port}",
        ],
        server_env(upstream),
        port,
        tmp_path,
    )
    try:
        await destructive_flow(
            lambda **kw: Client(StreamableHttpTransport(server.url, auth=token), **kw),
            upstream,
            elicits=elicits,
        )
    finally:
        server.stop()
