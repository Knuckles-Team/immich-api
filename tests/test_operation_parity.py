"""Every pinned source operation must execute through the API and native MCP."""

import asyncio
import copy
import json
from pathlib import Path

import pytest
import pytest_asyncio
from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult
from mcp.shared.exceptions import MCPError

import immich_api.auth as auth
from immich_api.openapi_runtime import CONTRACT
from immich_api.parity import require_complete_coverage
from immich_api.parity.openapi_parity import require_declared_authorization
from tests.operation_fixtures import CASES, RecordingProvider
from tests.parity_support import (
    DiscoveredClient,
    bounded_server,
    native_discovery,
    source_inventory,
)

ROOT = Path(__file__).resolve().parents[1]
ACTIONS = sorted(CONTRACT["operations"])
pytestmark = [
    pytest.mark.concept("IMMICH-001"),
    pytest.mark.spec("CONN-IMMICH-API-R006"),
]


def test_source_inventory_and_fixtures_are_complete():
    inventory = source_inventory()
    assert inventory == json.loads(
        (ROOT / "immich_api/openapi_inventory.json").read_text()
    )
    assert inventory["operation_count"] == 276
    assert inventory["path_count"] == 192
    assert set(CASES) == set(ACTIONS)


def test_source_omissions_have_reviewed_classifications():
    inventory = source_inventory()
    review = json.loads(
        (
            ROOT / "validation/immich-authorization-source-classification.json"
        ).read_text()
    )
    unknown = {
        action
        for action, operation in inventory["operations"].items()
        if operation["security_declaration"] == "unknown"
    }
    assert unknown == {row["operation_id"] for row in review["operations"]}
    assert review["source_sha256"] == inventory["source_sha256"]
    for row in review["operations"]:
        operation = inventory["operations"][row["operation_id"]]
        assert row["source_operation_sha256"] == operation["operation_sha256"]
        assert row["method"] == operation["method"]
        assert row["path"] == operation["source_path"]
    assert len(unknown) == 17
    require_declared_authorization(inventory)
    without_evidence = copy.deepcopy(inventory)
    without_evidence.pop("provider_overlay")
    with pytest.raises(
        ValueError,
        match="Authorization classification requires reviewed provider evidence",
    ):
        require_declared_authorization(without_evidence)


@pytest.mark.parametrize("mutation", ["missing", "changed", "wrong-review"])
def test_provider_evidence_must_be_reverified(mutation):
    overrides = {
        "missing": {"overlay_bytes": None},
        "changed": {"overlay_bytes": b"{}"},
        "wrong-review": {"expected_overlay_sha256": "0" * 64},
    }
    with pytest.raises(ValueError):
        source_inventory(**overrides[mutation])


@pytest.fixture
def provider_factory(monkeypatch):
    monkeypatch.setenv("IMMICH_PARITY_FIXTURE_TOKEN", "local-mock-token")
    providers = []

    def create(action, **options):
        provider = RecordingProvider(action, **options)
        providers.append(provider)
        return provider

    yield create
    for provider in providers:
        provider.close()


@pytest.fixture(scope="module")
def coverage():
    return {"api": [], "mcp": []}


@pytest.mark.parametrize("action", ACTIONS)
def test_every_api_operation_dispatches(action, provider_factory, coverage):
    provider = provider_factory(action)
    assert provider.execute() == provider.expected
    assert len(provider.requests) == 1
    coverage["api"].append(action)


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def native_session():
    state = {"confirmations": [], "api": [], "mcp": [], "accept": True}

    async def consent(message, response_type, params, context):
        state["confirmations"].append(message)
        if "response" in state:
            return state["response"]
        return {"confirmed": state["accept"]}

    server = bounded_server()
    async with Client(server, elicitation_handler=consent, timeout=10) as client:
        assert client.protocol_version == "2026-07-28"
        state["discovery"] = await native_discovery(client)
        yield DiscoveredClient(client), state


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize("action", ACTIONS)
async def test_every_native_mcp_operation_dispatches(
    action, provider_factory, native_session, monkeypatch, coverage
):
    client, state = native_session
    provider = provider_factory(action)
    monkeypatch.setattr(auth, "_client", provider.client)
    before = len(state["confirmations"])
    # Modern write approval uses two MCP requests; preserve the SDK's 10/s limit.
    await asyncio.sleep(0.12 if provider.operation["read_only"] else 0.22)
    result = await client.call_tool(
        provider.operation["domain"] + "_operations", provider.arguments
    )
    assert result.structured_content == provider.expected
    assert len(provider.requests) == 1
    if provider.operation["read_only"]:
        assert len(state["confirmations"]) == before
    else:
        assert state["confirmations"][before:] == [
            f"Are you sure you want to {action}?"
        ]
    coverage["mcp"].append(action)


@pytest.mark.asyncio(loop_scope="module")
async def test_complete_native_dispatch_receipt(coverage):
    assert require_complete_coverage(CONTRACT, coverage["api"], coverage["mcp"]) == {
        "api_operations": 276,
        "mcp_operations": 276,
    }


def test_optional_backup_file_still_sends_declared_multipart(provider_factory):
    action = "uploadDatabaseBackup"
    arguments = copy.deepcopy(CASES[action]["arguments"])
    body = arguments["body"]
    for field in ("assetData", "sidecarData", "file"):
        body.pop(field, None)
    provider = provider_factory(action, arguments=arguments)
    assert provider.execute() == provider.expected
    assert len(provider.requests) == 1


def test_asset_upload_fixture_includes_vendor_required_file():
    source = json.loads((ROOT / "api-spec/immich.openapi.json").read_bytes())
    asset = source["components"]["schemas"]["AssetMediaCreateDto"]
    assert asset["properties"]["assetData"]["x-immich-required"] is True
    assert CASES["uploadAsset"]["arguments"]["body"]["assetData"]


def test_asset_upload_without_required_file_has_no_effect(provider_factory):
    arguments = copy.deepcopy(CASES["uploadAsset"]["arguments"])
    arguments["body"].pop("assetData")
    provider = provider_factory("uploadAsset", arguments=arguments)
    with pytest.raises(ValueError, match="declared OpenAPI schema"):
        provider.execute()
    assert not provider.requests


@pytest.mark.asyncio(loop_scope="module")
async def test_native_asset_upload_requires_file_before_confirmation(
    provider_factory, native_session, monkeypatch
):
    client, state = native_session
    arguments = copy.deepcopy(CASES["uploadAsset"]["arguments"])
    arguments["body"].pop("assetData")
    provider = provider_factory("uploadAsset", arguments=arguments)
    monkeypatch.setattr(auth, "_client", provider.client)
    before = len(state["confirmations"])
    await asyncio.sleep(0.12)
    with pytest.raises(MCPError):
        await client.call_tool("assets_operations", arguments)
    assert not provider.requests
    assert len(state["confirmations"]) == before


@pytest.mark.parametrize(
    "action",
    [action for action in ACTIONS if not CONTRACT["operations"][action]["read_only"]],
)
def test_every_write_requires_operator_enablement(action, provider_factory):
    provider = provider_factory(action, write_mode="read-only")
    with pytest.raises(
        PermissionError, match="Writes require explicit operator enablement"
    ):
        provider.execute()
    assert not provider.requests


@pytest.mark.asyncio(loop_scope="module")
async def test_write_confirmation_denial_prevents_dispatch(
    native_session, provider_factory, monkeypatch
):
    client, state = native_session
    provider = provider_factory("createAlbum")
    monkeypatch.setattr(auth, "_client", provider.client)
    before = len(state["confirmations"])
    state["accept"] = False
    try:
        await asyncio.sleep(0.22)
        with pytest.raises(MCPError, match="Write was not confirmed"):
            await client.call_tool(
                "albums_operations", provider.arguments, raise_on_error=False
            )
        assert not provider.requests
        assert len(state["confirmations"]) == before + 1
    finally:
        state["accept"] = True


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize(
    "response",
    [
        {"confirmed": "yes"},
        {"confirmed": 1},
        {},
        ElicitResult(action="decline"),
        ElicitResult(action="cancel"),
        ElicitResult(action="accept", content=None),
    ],
    ids=["string", "integer", "missing-field", "decline", "cancel", "missing-content"],
)
async def test_invalid_confirmation_prevents_dispatch(
    response, native_session, provider_factory, monkeypatch
):
    client, state = native_session
    provider = provider_factory("createFace")
    monkeypatch.setattr(auth, "_client", provider.client)
    before = len(state["confirmations"])
    state["response"] = response
    try:
        await asyncio.sleep(0.22)
        with pytest.raises(MCPError, match="Write was not confirmed"):
            await client.call_tool("faces_operations", provider.arguments)
        assert not provider.requests
        assert len(state["confirmations"]) == before + 1
    finally:
        state.pop("response")


METHOD_ACTIONS = sorted(
    {
        next(
            action
            for action in ACTIONS
            if CONTRACT["operations"][action]["method"] == method
        )
        for method in {
            operation["method"] for operation in CONTRACT["operations"].values()
        }
    }
)


@pytest.mark.parametrize("status", [403, 429, 503])
@pytest.mark.parametrize("action", METHOD_ACTIONS)
def test_api_errors_are_single_attempt(action, status, provider_factory):
    provider = provider_factory(action, status=status)
    with pytest.raises(RuntimeError, match=f"HTTP {status}; no automatic retry"):
        provider.execute()
    assert len(provider.requests) == 1


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize("status", [403, 429, 503])
@pytest.mark.parametrize("action", METHOD_ACTIONS)
async def test_native_errors_are_single_attempt(
    action, status, provider_factory, native_session, monkeypatch
):
    client, _ = native_session
    provider = provider_factory(action, status=status)
    monkeypatch.setattr(auth, "_client", provider.client)
    await asyncio.sleep(0.12 if provider.operation["read_only"] else 0.22)
    with pytest.raises(MCPError):
        await client.call_tool(
            provider.operation["domain"] + "_operations",
            provider.arguments,
            raise_on_error=False,
        )
    assert len(provider.requests) == 1
