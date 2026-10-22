# CONN-IMMICH-API — Implementation tasks

Governing specification: [spec.md](spec.md).

The owner must reconcile starter behavior with the external system before completing these tasks.

- [ ] `CONN-IMMICH-API-R001` — Implement credential references. `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup.
- [ ] `CONN-IMMICH-API-R002` — Implement bounded api requests. `tests/test_api_wrapper.py` must exercise rejected origins, redirects, deadlines, and oversized responses through the real client.
- [ ] `CONN-IMMICH-API-R003` — Implement mcp registration. `tests/test_immich_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests.
- [ ] `CONN-IMMICH-API-R004` — Implement native content contracts. `scripts/generate_tool_schemas.py --check` must validate live tool contracts. `tests/test_immich_content.py::test_native_prompt_skill_shapes_and_tool_discovery` must render prompts and read the declared content through the production SDK server.
- [ ] `CONN-IMMICH-API-R005` — Implement typed source observations. `tests/test_kg_ingest.py::test_ingest_uses_scoped_binding_and_preserves_receipt` must observe typed changes at the submission boundary.
- [ ] `CONN-IMMICH-API-R006` — Prove complete source parity with `tests/test_operation_parity.py`, canonical source inventory and native MCP confirmation. Retain remaining operation IDs and failures until every declared operation passes both surfaces.
- [x] **CONN-IMMICH-API-R007:** File the pack, manifest and ingest binding under the fleet name `immich`.
