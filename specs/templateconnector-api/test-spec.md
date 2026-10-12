# CONN-TEMPLATECONNECTOR-API — Verification plan

Governing specification: [spec.md](spec.md).

These acceptance targets require connector-specific execution and review.
Test names describe source mappings, not successful runs or delivery receipts.
Native content listing needs a connector-owned integration test before the content requirement is delivered.

| Requirement | Verification target |
|---|---|
| `CONN-TEMPLATECONNECTOR-API-R001` | `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup. |
| `CONN-TEMPLATECONNECTOR-API-R002` | `tests/test_api_wrapper.py` must exercise rejected origins, redirects, deadlines, and oversized responses through the real client. |
| `CONN-TEMPLATECONNECTOR-API-R003` | `tests/test_templateconnector_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests. |
| `CONN-TEMPLATECONNECTOR-API-R004` | `scripts/generate_tool_schemas.py --check` must validate live tool contracts. Native content listing verification remains required before delivery. |
| `CONN-TEMPLATECONNECTOR-API-R005` | `tests/test_kg_ingest.py::test_ingest_maps_record_and_uses_submit` must observe typed changes at the submission boundary. |

The owner must retain failure evidence and use canonical lifecycle tooling to regenerate `status.json`.
