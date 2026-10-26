"""CONN-IMMICH-API-CONNECTOR-CONTENT-R001: the server lists its packaged skills, ontology and prompts by default."""

from __future__ import annotations

import asyncio
import hashlib
import importlib
from importlib.metadata import version
from pathlib import Path

import pytest
from fastmcp import Client

PACKAGE = "immich_api"
ROOT = Path(list(importlib.import_module(PACKAGE).__path__)[0])

pytestmark = pytest.mark.spec("CONN-IMMICH-API-CONNECTOR-CONTENT-R001")


def _server():
    from immich_api.mcp_server import build_server

    return build_server(command_args=["--transport", "stdio", "--auth-type", "none"])


async def _listings():
    async with Client(_server(), mode="legacy") as client:
        initialized = await client.initialize()
        assert initialized.server_info.version == version("immich-api")
        resources = {str(r.uri) for r in await client.list_resources()}
        prompts = {p.name for p in await client.list_prompts()}
        for uri in resources:
            if uri.startswith(("ontology://", "shapes://")):
                relative = uri.split("/", 3)[-1]
                directory = (
                    ROOT
                    / "ontology"
                    / ("shapes" if uri.startswith("shapes://") else "")
                )
                actual = await client.read_resource(uri)
                assert actual[0].text.encode() == (directory / relative).read_bytes()
    return resources, prompts


def test_default_content_surfaces() -> None:
    resources, prompts = asyncio.run(_listings())
    if list(ROOT.glob("skills/*/SKILL.md")):
        assert any(u.startswith("skill://") for u in resources)
    if list(ROOT.glob("ontology/*.ttl")):
        assert any(u.startswith("ontology://immich/") for u in resources)
    for path in ROOT.glob("prompts/*.json"):
        if not path.name.startswith("_"):
            assert path.stem in prompts


def test_publication_preserves_tools(monkeypatch) -> None:
    module = importlib.import_module("immich_api.mcp_server")

    async def tools(server):
        async with Client(server) as client:
            return [tool.model_dump(mode="json") for tool in await client.list_tools()]

    published = asyncio.run(tools(_server()))
    factory = module.create_mcp_server

    def tools_only(*args, **kwargs):
        kwargs.pop("content")
        return factory(*args, **kwargs)

    monkeypatch.setattr(module, "create_mcp_server", tools_only)
    assert asyncio.run(tools(_server())) == published


def test_production_pack_includes_packaged_ontology_and_shapes() -> None:
    from agent_connector_sdk.artifacts.pack import build_content_pack
    from agent_connector_sdk.artifacts.resources import ResourceArtifactKind
    from agent_connector_sdk.ports.session import TransportEndpoint
    from agent_connector_sdk.transports.mcp import McpTransport

    async def capture():
        endpoint = TransportEndpoint(in_process=_server())
        async with McpTransport().session(endpoint) as session:
            return await build_content_pack(
                session, connector="immich", kinds=(ResourceArtifactKind(),)
            )

    pack = asyncio.run(capture())
    assert pack.server_package_version == version("immich-api")
    uris = {str(entry.uri) for entry in pack.archive.entries}
    for entry in pack.archive.entries:
        if entry.uri.startswith(("ontology://", "shapes://")):
            name = entry.uri.rsplit("/", 1)[-1]
            directory = (
                ROOT
                / "ontology"
                / ("shapes" if entry.uri.startswith("shapes://") else "")
            )
            assert (
                entry.body.sha256
                == hashlib.sha256((directory / name).read_bytes()).hexdigest()
            )
    for path in ROOT.glob("ontology/*.ttl"):
        assert f"ontology://immich/{path.name}" in uris
    for path in ROOT.glob("ontology/shapes/*.ttl"):
        assert f"shapes://immich/{path.name}" in uris


@pytest.fixture(autouse=True)
def _no_outbound_network(monkeypatch):
    import socket

    def refuse(*_args, **_kwargs):
        raise AssertionError("content publication must not contact an external system")

    monkeypatch.setenv("MCP_FLEET_REGISTRATION", "false")
    monkeypatch.setattr(socket.socket, "connect", refuse)


def test_sdk_floor_supports_content_identity_and_current_pack_protocol() -> None:
    import tomllib

    from packaging.requirements import Requirement

    project = tomllib.loads((ROOT.parent / "pyproject.toml").read_text())["project"]
    declared = list(project.get("dependencies", []))
    for extra in project.get("optional-dependencies", {}).values():
        declared.extend(extra)
    sdk = [
        Requirement(value)
        for value in declared
        if value.startswith("agent-connector-sdk")
    ]
    assert sdk
    for requirement in sdk:
        assert requirement.specifier.contains("0.5.5")
        assert not requirement.specifier.contains("0.5.4")
