# CONN-IMMICH-API — Immich Api connector

## Outcome

The connector must expose reviewed external-system operations through one governed integration boundary.
The connector must preserve credential, transport, source, and content contracts.

## Scope and owner

The `immich-api` repository owns external-system operations and source mappings.
The shared connector SDK owns reusable transport, authentication, MCP, and ingest contracts.
The shared pipelines repository owns quality gates and delivery rendering.

Component: Connector integration
References: [Connector SDK](https://github.com/Knuckles-Team/agent-connector-sdk/blob/b9ee9ed0a82f6ecd5ed23d6226ca5ab503f74f9c/README.md)
Code: ../../immich_api/auth.py ../../immich_api/openapi_runtime.py ../../immich_api/mcp_server.py ../../immich_api/mcp/__init__.py ../../immich_api/kg_ingest.py ../../tests/test_auth.py ../../tests/test_api_wrapper.py ../../tests/test_immich_mcp_validation.py ../../tests/test_kg_ingest.py ../../tests/test_operation_parity.py ../../tests/operation_fixtures.py ../../scripts/generate_tool_schemas.py

## Non-goals

This specification grants no service access, credential creation, deployment, or approval exception.
The connector must not implement a graph engine, independent policy authority, or duplicate SDK runtime.

## Why a new spec

The scaffold emits the repository's first capability specification.
No existing specification occurs in this newly generated source tree.
An existing repository must reconcile this capability with its current owner before adopting the generated files.

## Requirements

See [requirements.md](requirements.md), [plan.md](plan.md), and [test-spec.md](test-spec.md).
Existing test references identify verification targets. They do not establish delivery.
