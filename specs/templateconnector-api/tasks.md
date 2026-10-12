# CONN-TEMPLATECONNECTOR-API — Implementation tasks

Governing specification: [spec.md](spec.md).

The owner must reconcile starter behavior with the external system before completing these tasks.

- [ ] `CONN-TEMPLATECONNECTOR-API-R001` — Implement credential references. `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup.
- [ ] `CONN-TEMPLATECONNECTOR-API-R002` — Implement bounded api requests. `tests/test_api_wrapper.py` must exercise rejected origins, redirects, deadlines, and oversized responses through the real client.
- [ ] `CONN-TEMPLATECONNECTOR-API-R003` — Implement mcp registration. `tests/test_templateconnector_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests.
- [ ] `CONN-TEMPLATECONNECTOR-API-R004` — Implement native content contracts. `scripts/generate_tool_schemas.py --check` must validate live tool contracts. Native content listing verification remains required before delivery.
- [ ] `CONN-TEMPLATECONNECTOR-API-R005` — Implement typed source observations. `tests/test_kg_ingest.py::test_ingest_maps_record_and_uses_submit` must observe typed changes at the submission boundary.
