# CONN-IMMICH-API — Immich Api connector

## Outcome

The connector must expose reviewed external-system operations through one governed integration boundary.
The connector must preserve credential, transport, source, and content contracts.

## Scope and owner

The `immich-api` repository owns external-system operations and source mappings.
The shared connector SDK owns reusable transport, authentication, MCP, and ingest contracts.
The shared pipelines repository owns quality gates and delivery rendering.

Component: Connector integration
References: [Connector SDK](https://github.com/Knuckles-Team/scion-sdk/blob/b9ee9ed0a82f6ecd5ed23d6226ca5ab503f74f9c/README.md)
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

## User Scenarios & Testing

### User Story 1 - Confirm a write from any client (Priority: P1)

An operator using any MCP client wants to confirm a destructive Immich write, so that a client that cannot be asked still reaches a defined outcome instead of a connection failure.

**Acceptance Scenarios**:

1. **Given** a client that cannot elicit, **When** it calls a write action without confirmation, **Then** it receives a cancelled refusal naming `confirm=true` and no upstream request is sent.
2. **Given** the same client, **When** it repeats the call with `confirm=true`, **Then** the write is performed once.
3. **Given** a client that can elicit, **When** it calls a write action, **Then** it is asked and the write runs only on acceptance.

### Edge Cases

- A read action never asks for confirmation.
- The `confirm` argument is never forwarded to the Immich API.
- A deployment with writes disabled refuses every write regardless of confirmation.

### Success Criteria

- **SC-001**: (CONN-IMMICH-API-R009.3) Every write action is refused or performed in a single call, with zero upstream requests when refused.

### Assumptions

- The shared connector SDK owns the elicitation and refusal behaviour; this connector only calls it.
