# CONN-IMMICH-API — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

The connector reuses the SDK server factory, credential resolver, HTTP client, and typed ingest service. The connector owns operation arguments, external-system mappings, and package content. Ownership, component identity, SDK reference and implementation inventory are recorded in [the governing scope](spec.md#scope-and-owner). ```mermaid flowchart LR Caller[Authorized caller] --> Server[MCP server] Server --> Router[Operation router] Router --> Client[Connector API client] Client --> Vendor[Configured external system] Resolver[Credential references and TLS policy] --> Client Content[Packaged skills prompts ontology manifest] --> Server Source[Authorized source observations] --> Mapper[Connector ingest mapper] Mapper --> SDK[Shared connector ingest service] ```.

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: scion-sdk, fastmcp
- **Storage**: N/A; the connector stores nothing
- **Testing**: pytest; the proof level each row names
- **Target Platform**: Linux containers
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: one tool per API operation; shared capabilities come from the SDK
- **Scale/Scope**: 16 rows

## Constitution Check

- One owner per concept: pass. The connector owns one external system's calls, mappings and tools only.
- Connectors depend on the SDK and are called through arbora: pass.
- No ratchets: pass. The rows add no suppression.

## Project Structure

```text
immich_api/auth.py  existing
immich_api/mcp_server.py  existing
immich_api/openapi_runtime.py  existing
immich_api/openapi_execution.py  existing
immich_api/mcp/__init__.py  existing
immich_api/kg_ingest.py  existing
pyproject.toml  existing
immich_api/openapi_contract.json  existing
immich_api/album_metadata.py  existing
immich_api/api/api_client_system.py  existing
immich_api/openapi_request.py  existing
immich_api/mcp/album_sample.py  existing
```

## Phase 0: Research

No unknowns. Each row names the code it touches.

## Phase 1: Design

### Interfaces and live integration path

`immich_api/mcp_server.py` exposes `build_server` and the console entry point.
`get_mcp_instance` calls `create_mcp_server`, `register_tool_surface`, and the package tool registrars.
`immich_api/mcp/__init__.py` registers `OpenApiTool` domains from `openapi_runtime.py`; each operation uses `get_client` to obtain `ApiClientSystem(OpenApiClient)`. The bounded album sample registrar calls the same declared-operation client.
`immich_api/auth.py` resolves references only when a caller requests a client.
`immich_api/openapi_runtime.py` enforces transport and response limits before returning external data.
`immich_api/kg_ingest.py` maps observations into SDK types and calls the configured service's `submit` method.
The SDK owns engine transport and durable checkpoints.

### Complete provider operation parity

Keep the exact deployed OpenAPI bytes in `api-spec/immich.openapi.json` and
compile the complete inventory through the canonical builder. Preserve vendor
authorization extensions and unknown declarations; source omission alone does
not establish public access. Reviewed provider source can explain those
declarations without changing the original schema.

Preserve the independently reviewed provider sidecar and its exact source files.
Reverify file, operation and overlay hashes during admission. The sole provider
correction adds the required asset file without removing other constraints.
Configure bounded discovery through the normal server's named client-budget
setting. Retrieve each complete domain schema through native exact search and
exercise every action through FastMCP's proxy. Fixture budgets establish only
the named synthetic client's test scope; production budgets need separate evidence.

The exhaustive test fixture set must equal the source operation IDs. Each fixture
executes once through `ApiClientSystem` and once through an actual FastMCP client,
with only outbound HTTP replaced. The mock checks the method, path, query,
headers and serialized body, and the test checks the structured response. MCP
write approval must complete through the negotiated modern protocol; legacy
negotiation and patched approval helpers are not acceptance evidence. Missing
approval and provider errors must not cause a write retry. Source parity and
mocked transport evidence remain separate from live provider validation.

### Content and contracts

The server serves package prompts, skills, ontology, and `connector_manifest.yml` through native MCP primitives.
The schema generator reads `tools/list` without invoking vendor operations.
It records both input and output schemas. Empty source presets declare no extraction integration.
`tests/test_immich_content.py` exercises production native content discovery and prompt rendering. The extraction preset is disabled pending an SDK-supported provider/account stream binding; no default source mode is claimed.

### Dependencies and decisions

The pinned SDK and the immutable OpenAPI contract govern runtime dispatch and content. Source mapping/graph acceptance remains pending; no ingestion preset is enabled.
The SDK reference records a source dependency; it does not create a cross-repository delivery prerequisite.
Reviewers must add `Depends-on:` declarations only for confirmed prerequisite requirements.
Each source mapping must match the connector's actual external data before ingestion is enabled.

### Quality and release gates

Run `python scripts/check_connector_contract.py . --package immich_api`.
Run `python scripts/generate_tool_schemas.py --check` and `python -m pytest tests -q`.
Run the pinned pre-commit and pre-push gates with the approved scanner toolchain.
The published site must pass the shared readiness checks and render canonical spec records.
Source tests do not authorize release, deployment, or external effects.

### Risks and alternatives

Declared operations and mappings require authenticated external-system validation before production use.
Missing credentials, rejected source observations, and failed transport checks must propagate as explicit failures.
Duplicating shared SDK or pipeline logic would create conflicting owners.

### Adoption of scion-sdk 0.10.0 (CONN-IMMICH-API-R010)

- Owner. This repository, the import lines named in `CONN-IMMICH-API-R010`. The paths belong to scion-sdk.
- Cohesion. The import edits, the pin and the lock change together and sit in one change.
- Dependency direction. The connector imports public modules of the SDK units; no import points to a private module.
- Interface depth. The connector uses the public surface only.
- Special cases. None. Every removed path takes the same replacement, with no alias.
- State. None.
- Environment. None. The pin is package metadata, not environment code.

## Phase 2: Task approach

`tasks.md` holds one task line per row, producer first.

## Complexity Tracking

None. The constitution check passed.

## Build contract

The repository pre-commit hooks apply: `spec-standard`, `spec-status`, `ruff-format`. Each row names its proving test. No suppression and no duplicate implementation.

## Production caller chain

1. `CONN-IMMICH-API-R001`: MCP tool call → `immich_api/mcp_server.py` → `get_client` in `immich_api/auth.py`.
2. `CONN-IMMICH-API-R002`: `OpenApiTool.run` → `OpenApiClient.execute` in `immich_api/openapi_runtime.py`.
3. `CONN-IMMICH-API-R003`: server start → `get_mcp_instance` in `immich_api/mcp_server.py` → `register_domain`.
4. `CONN-IMMICH-API-R004`: server start → `immich_api/mcp_server.py` → SDK content providers.
5. `CONN-IMMICH-API-R005`: ingest trigger → `immich_api/kg_ingest.py` → SDK ingest service.
6. `CONN-IMMICH-API-R007`: SDK entry-point discovery → the `immich` connector declared in `pyproject.toml`.
7. `CONN-IMMICH-API-R008`: (planned) arbora `fleet.call` -> MCP tool surface built by `register_tool_surface(mcp, service="immich-api", tools_module=tool_modules)` in `immich_api/mcp_server.py::get_mcp_instance` (line 28) -> a new `register_asset_tags_tools` exported from `immich_api/mcp/__init__.py` -> new `immich_api/media_tags.py::immich_asset_tags`.
8. `CONN-IMMICH-API-R009.1`: every `<domain>_operations` tool (`immich_api/openapi_runtime.py::OpenApiTool.run`, line 162) -> `OpenApiClient.execute` (line 102) in `immich_api/openapi_runtime.py` -> `immich_api/api/api_client_system.py::ApiClientSystem`; the first-request version read and the pin check are planned in `OpenApiClient.execute`.
9. `CONN-IMMICH-API-R009.2`: arbora `fleet.call` -> read tools registered per domain by `register_domain` (`immich_api/openapi_runtime.py` line 182) through `immich_api/mcp/__init__.py` registrars -> `register_tool_surface` in `immich_api/mcp_server.py::get_mcp_instance`; the page size setting `IMMICH_PAGE_SIZE` is planned in `OpenApiClient.execute`.
10. `CONN-IMMICH-API-R009.4`: (planned) SDK connector-sync runner -> new `ingest_changes(cursor)` in `immich_api/kg_ingest.py`, beside `ingest_album_metadata` (line 21), which submits through `current_ingest().submit(binding, changes)` today; no cursor exists yet.
11. `CONN-IMMICH-API-R009.5`: (planned) `immich_api/kg_ingest.py::ingest_changes` of R009.4, which does not exist yet, called by the SDK connector-sync runner; the unchanged-page check sits in front of its existing `service.submit` call.
12. `CONN-IMMICH-API-R009.6`: (planned) arbora fleet health probe -> new read-only tool `immich_health` registered through a new registrar exported from `immich_api/mcp/__init__.py` -> `register_tool_surface` in `immich_api/mcp_server.py::get_mcp_instance` -> `OpenApiClient.execute` on the `server` domain.
13. `CONN-IMMICH-API-R009.7`: (planned) operator through arbora `fleet.call` -> new read-only tool `immich_upgrade_digest` registered via `immich_api/mcp/__init__.py` -> `register_tool_surface` in `immich_api/mcp_server.py::get_mcp_instance` -> `OpenApiClient.execute` on the `server` domain.

## Cross-repo seams

none. The cited owner rows are library capabilities the connector calls in process; spec.md names them.
