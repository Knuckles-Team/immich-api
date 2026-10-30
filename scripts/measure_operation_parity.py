"""Measure complete native/API dispatch using the repository's real test fixtures."""

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scion_sdk
from fastmcp import Client

import immich_api.auth as auth
from immich_api.openapi_runtime import CONTRACT
from immich_api.parity import require_complete_coverage
from immich_api.parity.openapi_parity import require_declared_authorization
from tests.operation_fixtures import CASES, RecordingProvider
from tests.parity_support import (
    BUDGET,
    OVERLAY_SHA256,
    DiscoveredClient,
    bounded_server,
    native_discovery,
    source_inventory,
)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--sdk-revision", required=True)
parser.add_argument("--builder-revision", required=True)
parser.add_argument("--fastmcp-version")
parser.add_argument("--eg-revision")
parser.add_argument("--sdk-overlay-sha256")
options = parser.parse_args()
assert not options.output.exists(), "Preserve prior measurements"
if options.fastmcp_version:
    assert importlib.metadata.version("fastmcp") == options.fastmcp_version
PROJECT = Path(auth.__file__).resolve().parents[1]
SDK_PACKAGE = Path(scion_sdk.__file__).resolve().parent


class RunState:
    def __init__(self):
        self.coverage = {"api": [], "mcp": []}
        self.rows = []
        self.confirmations = []
        self.requests = []
        self.action = None

    async def consent(self, message, response_type, params, context):
        assert message == f"Are you sure you want to {self.action}?"
        assert params.requested_schema["required"] == ["confirmed"]
        assert params.requested_schema["properties"]["confirmed"]["type"] == "boolean"
        self.confirmations.append(self.action)
        return {"confirmed": True}


def source_hashes(directory, relative_to):
    return {
        str(path.relative_to(relative_to)): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in sorted(directory.rglob("*.py"))
    }


async def invoke_surface(surface, provider, client):
    if surface == "api":
        return provider.execute()
    await asyncio.sleep(0.12 if provider.operation["read_only"] else 0.22)
    result = await client.call_tool(
        provider.operation["domain"] + "_operations", provider.arguments
    )
    return result.structured_content


async def dispatch_surface(surface, action, client, state):
    provider = RecordingProvider(action)
    auth._client = provider.client
    before = len(state.confirmations)
    try:
        actual = await invoke_surface(surface, provider, client)
        assert actual == provider.expected
        assert len(provider.requests) == 1
        expected = int(surface == "mcp" and not provider.operation["read_only"])
        assert len(state.confirmations) - before == expected
        state.coverage[surface].append(action)
        return "passed"
    except Exception as exc:
        return {"error_type": type(exc).__name__, "message": str(exc)[:400]}
    finally:
        state.requests.extend(
            {"surface": surface, "action": action} for _ in provider.requests
        )
        auth._client = None
        provider.close()


async def dispatch_operation(action, operation, client, state):
    state.action = action
    row = {
        "action": action,
        "method": operation["method"],
        "path": operation["path"],
        "domain": operation["domain"],
    }
    for surface in state.coverage:
        row[surface] = await dispatch_surface(surface, action, client, state)
    state.rows.append(row)
    if len(state.rows) % 50 == 0:
        print(
            json.dumps(
                {
                    "completed": len(state.rows),
                    "api_passed": len(state.coverage["api"]),
                    "mcp_passed": len(state.coverage["mcp"]),
                }
            ),
            flush=True,
        )


def complete_coverage(state):
    try:
        return require_complete_coverage(
            CONTRACT, state.coverage["api"], state.coverage["mcp"]
        ), True
    except ValueError as exc:
        return {"error": str(exc)}, False


def method_counts(rows):
    return dict(sorted(Counter(row["method"] for row in rows).items()))


def remaining_operations(rows):
    return [{key: row[key] for key in ("action", "method", "path")} for row in rows]


def raw_authorization_omissions(inventory):
    return sorted(
        action
        for action, value in inventory["operations"].items()
        if value["security_declaration"] == "unknown"
    )


def measurement_record(inventory, state, discovery, started):
    complete, passed = complete_coverage(state)
    remaining = [
        row for row in state.rows if row["api"] != "passed" or row["mcp"] != "passed"
    ]
    return {
        "sdk_revision": options.sdk_revision,
        "sdk_overlay_sha256": options.sdk_overlay_sha256,
        "eg_python_revision": options.eg_revision,
        "runtime_versions": {
            name: importlib.metadata.version(name)
            for name in ("fastmcp", "mcp", "pydantic", "httpx", "jsonschema")
        },
        "builder_revision": options.builder_revision,
        "provider_overlay_sha256": OVERLAY_SHA256,
        "client_budget": BUDGET,
        "production_client_approval": False,
        "source_sha256": inventory["source_sha256"],
        "source_operation_count": inventory["operation_count"],
        "path_count": inventory["path_count"],
        "native_discovery": discovery,
        "protocol": "2026-07-28",
        "api_passed": len(state.coverage["api"]),
        "mcp_passed": len(state.coverage["mcp"]),
        "coverage": complete,
        "method_counts": method_counts(state.rows),
        "remaining_operations": remaining_operations(remaining),
        "remaining_method_counts": method_counts(remaining),
        "mock_http_requests": len(state.requests),
        "confirmations": state.confirmations,
        "provider_requests": 0,
        "passed": passed,
        "rows": state.rows,
        "seconds": round(time.monotonic() - started, 2),
        "raw_authorization_omissions": raw_authorization_omissions(inventory),
        "unclassified_authorization_operations": [],
        "runtime_source_sha256": source_hashes(PROJECT / "immich_api", PROJECT),
        "sdk_source_sha256": source_hashes(SDK_PACKAGE, SDK_PACKAGE),
    }


def write_record(record):
    options.output.write_text(json.dumps(record, indent=2) + "\n")
    print(
        json.dumps(
            {
                key: value
                for key, value in record.items()
                if key
                not in {
                    "rows",
                    "runtime_source_sha256",
                    "sdk_source_sha256",
                    "confirmations",
                    "raw_authorization_omissions",
                    "native_discovery",
                }
            }
        ),
        flush=True,
    )
    if not record["passed"]:
        raise SystemExit(1)


async def main():
    started = time.monotonic()
    os.environ["IMMICH_PARITY_FIXTURE_TOKEN"] = "local-mock-token"
    inventory = source_inventory()
    require_declared_authorization(inventory)
    assert set(CASES) == set(inventory["operations"])
    state = RunState()
    async with Client(
        bounded_server(), elicitation_handler=state.consent, timeout=10
    ) as native:
        assert native.protocol_version == "2026-07-28"
        discovery = await native_discovery(native)
        client = DiscoveredClient(native)
        for action, operation in sorted(CONTRACT["operations"].items()):
            await dispatch_operation(action, operation, client, state)
    record = measurement_record(inventory, state, discovery, started)
    write_record(record)


asyncio.run(main())
