
"""A bounded vendor HTTP client using the connector SDK transport contract."""

import json
import time
from typing import Any
from urllib.parse import SplitResult, urljoin, urlsplit

import httpx
from agent_connector_sdk.http.client import create_http_client
from agent_connector_sdk.http.options import HttpClientOptions
from agent_connector_sdk.tls.profile import ResolvedTLSProfile

from ..error_authority import AGENT_ERROR_ACCEPT

_MAX_RESPONSE_BYTES = 16 * 1024 * 1024
_MAX_RESPONSE_SECONDS = 60.0
_REQUEST_TIMEOUT_S = 30.0


def _origin(parsed: SplitResult) -> tuple[str, str, int]:
    scheme = parsed.scheme.lower()
    port = parsed.port or (443 if scheme == "https" else 80)
    return scheme, (parsed.hostname or "").lower(), port


def _validate_base_url(base_url: str) -> tuple[str, tuple[str, str, int]]:
    rendered = str(base_url or "").strip()
    if not rendered or len(rendered) > 2048 or any(c in rendered for c in "\x00\r\n"):
        raise ValueError("Invalid service base URL")
    try:
        parsed = urlsplit(rendered)
        origin = _origin(parsed)
    except ValueError as exc:
        raise ValueError("Invalid service base URL") from exc
    if (
        parsed.scheme.lower() not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Service base URL must be HTTP(S) without credentials")
    return rendered.rstrip("/") + "/", origin


def _request_url(
    base_url: str, expected_origin: tuple[str, str, int], path: str
) -> str:
    rendered = str(path or "")
    if len(rendered) > 4096 or any(c in rendered for c in "\x00\r\n"):
        raise ValueError("Invalid API path")
    try:
        supplied = urlsplit(rendered)
        if supplied.username is not None or supplied.password is not None:
            raise ValueError("API path must not contain credentials")
        url = urljoin(base_url, rendered)
        if _origin(urlsplit(url)) != expected_origin:
            raise ValueError("API path changed the configured service origin")
    except ValueError as exc:
        raise ValueError("Invalid API path") from exc
    return url


class ApiClientBase:
    """Use SDK auth objects; tokens never travel through default headers."""

    def __init__(
        self,
        base_url: str,
        auth: httpx.Auth,
        tls_profile: ResolvedTLSProfile | None = None,
        *,
        allow_plaintext: bool = False,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url, self._origin = _validate_base_url(base_url)
        self.session = create_http_client(
            HttpClientOptions(
                base_url=self.base_url,
                timeout=_REQUEST_TIMEOUT_S,
                auth=auth,
                tls=tls_profile,
                allow_plaintext=allow_plaintext,
                headers={"Accept": AGENT_ERROR_ACCEPT},
            ),
            transport=transport,
        )

    def close(self) -> None:
        """Close the owned HTTP connection pool."""
        self.session.close()

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Return bounded JSON or a bounded text response from the same origin."""
        url = _request_url(self.base_url, self._origin, path)
        if kwargs.get("follow_redirects") not in (None, False):
            raise ValueError("Redirect following is disabled")
        if "timeout" in kwargs:
            raise ValueError("Request timeout is controlled by the client")
        kwargs["follow_redirects"] = False
        with self.session.stream(method, url, **kwargs) as response:
            response.raise_for_status()
            declared = response.headers.get("content-length")
            if declared:
                try:
                    declared_size = int(declared)
                except ValueError as exc:
                    raise RuntimeError("Invalid response content length") from exc
                if declared_size < 0 or declared_size > _MAX_RESPONSE_BYTES:
                    raise RuntimeError("Response size limit exceeded")
            body = bytearray()
            deadline = time.monotonic() + _MAX_RESPONSE_SECONDS
            for chunk in response.iter_bytes():
                if time.monotonic() > deadline:
                    raise RuntimeError("Response time limit exceeded")
                if len(body) + len(chunk) > _MAX_RESPONSE_BYTES:
                    raise RuntimeError("Response size limit exceeded")
                body.extend(chunk)
        if response.status_code == 204 or not body:
            return {"status": response.status_code}
        try:
            return json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {
                "status": response.status_code,
                "text": body.decode("utf-8", errors="replace")[:4096],
            }
