"""Pinned, synthetic fixtures and mock HTTP assertions for every source operation."""

import base64
import json
from email.parser import BytesParser
from email.policy import default
from pathlib import Path
from urllib.parse import parse_qsl, quote

import httpx
from agent_connector_sdk.auth.static import bearer_auth

from immich_api.api import ApiClientSystem
from immich_api.openapi_runtime import CONTRACT

CASES = json.loads(
    (Path(__file__).parent / "fixtures/operation-cases.json").read_text()
)


def scalar(value):
    return str(value).lower() if isinstance(value, bool) else str(value)


def query_values(parameter, value):
    if not isinstance(value, list):
        return [value]
    if parameter.get("explode", True):
        return value
    return [",".join(map(scalar, value))]


def check_parameters(request, operation, arguments):
    expected = []
    for parameter in operation["parameters"]:
        name, location = parameter["name"], parameter["in"]
        value = arguments.get(location, {}).get(name)
        if value is None:
            continue
        if location == "query":
            expected.extend(
                (name, scalar(item)) for item in query_values(parameter, value)
            )
        elif location == "header":
            assert request.headers[name] == scalar(value)
    assert sorted(request.url.params.multi_items()) == sorted(expected)


def multipart_value(part, value):
    if part.get_filename():
        return base64.b64decode(value, validate=True)
    if isinstance(value, (dict, list)):
        return json.dumps(value, separators=(",", ":")).encode()
    return scalar(value).encode()


def check_multipart(request, body):
    assert request.headers["content-type"].startswith("multipart/form-data;")
    message = BytesParser(policy=default).parsebytes(
        b"Content-Type: "
        + request.headers["content-type"].encode()
        + b"\r\n\r\n"
        + request.content
    )
    parts = {
        part.get_param("name", header="content-disposition"): part
        for part in message.iter_parts()
    }
    assert set(parts) == set(body)
    for name, value in body.items():
        assert parts[name].get_payload(decode=True) == multipart_value(
            parts[name], value
        )


def check_body(request, operation, arguments):
    if "body" not in arguments:
        return
    body = arguments["body"]
    media = operation["content_type"]
    if media == "application/json":
        assert json.loads(request.content) == body
    elif media == "application/x-www-form-urlencoded":
        assert dict(parse_qsl(request.content.decode())) == {
            key: scalar(value) for key, value in body.items()
        }
    elif media == "multipart/form-data":
        check_multipart(request, body)
    else:
        raise AssertionError(f"Unverified request media type: {media}")


def check_request(request, operation, arguments):
    path = operation["path"]
    for name, value in arguments.get("path", {}).items():
        path = path.replace("{" + name + "}", quote(scalar(value), safe=""))
    assert request.method == operation["method"]
    assert request.url.path == path
    assert request.url.host == "service.example.invalid"
    assert request.headers["Authorization"] == "Bearer local-mock-token"
    check_parameters(request, operation, arguments)
    check_body(request, operation, arguments)


def response_with_media(status, media, data, mode):
    if mode == "json":
        return httpx.Response(status, json=data, headers={"content-type": media})
    content = base64.b64decode(data) if mode == "binary" else data.encode()
    return httpx.Response(status, content=content, headers={"content-type": media})


def response_for(operation, expected):
    status, media, data = (
        expected["status"],
        expected["content_type"],
        expected["data"],
    )
    if str(status) in operation.get("redirect_responses", {}):
        return httpx.Response(
            status, headers={"location": data["location"]}, content=b"Redirecting"
        )
    if not media:
        return httpx.Response(status)
    mode = operation["response_modes"][str(status)][media]
    return response_with_media(status, media, data, mode)


class RecordingProvider:
    """Exercise the real SDK client with only the network boundary replaced."""

    def __init__(self, action, *, arguments=None, status=None, write_mode="read-write"):
        self.action = action
        self.operation = CONTRACT["operations"][action]
        self.arguments = CASES[action]["arguments"] if arguments is None else arguments
        self.expected = CASES[action]["result"]
        self.status = status
        self.requests = []
        self.client = ApiClientSystem(
            base_url="https://service.example.invalid",
            auth=bearer_auth("env://IMMICH_PARITY_FIXTURE_TOKEN"),
            credential_scheme="bearer",
            write_mode=write_mode,
            transport=httpx.MockTransport(self.respond),
        )

    def respond(self, request):
        self.requests.append(request)
        check_request(request, self.operation, self.arguments)
        if self.status is not None:
            return httpx.Response(self.status)
        return response_for(self.operation, self.expected)

    def execute(self):
        return self.client.execute(self.operation["domain"], self.arguments)

    def close(self):
        self.client.close()
