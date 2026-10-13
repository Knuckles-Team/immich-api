# CONN-IMMICH-API — Verification plan

Governing specification: [spec.md](spec.md).

These acceptance targets require connector-specific execution and review.
Test names describe source mappings, not successful runs or delivery receipts.
Native content listing is proved by the connector-owned SDK test; a source listing does not establish live graph ingestion.

| Requirement | Verification target |
|---|---|
| `CONN-IMMICH-API-R001` | `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup. |
| `CONN-IMMICH-API-R002` | `tests/test_api_wrapper.py` must exercise rejected origins, redirects, deadlines, and oversized responses through the real client. |
| `CONN-IMMICH-API-R003` | `tests/test_immich_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests. |
| `CONN-IMMICH-API-R004` | `scripts/generate_tool_schemas.py --check` must validate live tool contracts. `tests/test_immich_content.py::test_native_prompt_skill_shapes_and_tool_discovery` must render prompts and read the declared content through the production SDK server. |
| `CONN-IMMICH-API-R005` | `tests/test_kg_ingest.py::test_ingest_uses_scoped_binding_and_preserves_receipt` must observe typed changes at the submission boundary. |
| `CONN-IMMICH-API-R006` | `tests/test_operation_parity.py` must independently verify the pinned source inventory and reviewed provider evidence, retrieve complete native schemas within the explicit fixture budget, and execute every operation through the API and native discovery proxy. It must check serialized parameters and bodies, typed responses, explicit write approval and denial, required asset-file refusal before effects, multipart media, and single-attempt HTTP errors for every declared method. Mocked dispatch does not establish production client budgets, provider permissions or live service behavior. |

The owner must retain failure evidence and use canonical lifecycle tooling to regenerate `status.json`.

## Reviewed redirect and identity regressions

`tests/test_oauth_redirect_response.py` verifies the source-backed 307/Location
contract, bounded validation, no redirect following, and native MCP behavior.
`tests/test_session_auth_isolation.py` verifies login and OAuth responses cannot
replace configured API-key identity through shared API or native MCP clients.
The [merged SDK acceptance receipt](../../validation/focused-merged-sdk-b9ee9ed-2026-10-13.json)
records 21 passing cases. Normal pre-push tests provide the full candidate check;
source-overlay imports do not establish full release installation or live effects.
