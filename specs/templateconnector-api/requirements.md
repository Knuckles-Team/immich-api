# CONN-TEMPLATECONNECTOR-API — Requirements

Governing specification: [spec.md](spec.md).

Each row identifies one connector behavior and its verification target.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-TEMPLATECONNECTOR-API-R001` | **Credential references.** The connector must resolve authorized credential references in `templateconnector_api/auth.py` when a client is requested. | `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup. |
| `CONN-TEMPLATECONNECTOR-API-R002` | **Bounded API requests.** The connector must enforce origin, TLS, timeout, and response-size limits in `templateconnector_api/api/api_client_base.py`. | `tests/test_api_wrapper.py` must exercise rejected origins, redirects, deadlines, and oversized responses through the real client. |
| `CONN-TEMPLATECONNECTOR-API-R003` | **MCP registration.** The connector must register its operation router through `templateconnector_api/mcp_server.py` and `templateconnector_api/mcp/mcp_system.py`. | `tests/test_templateconnector_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests. |
| `CONN-TEMPLATECONNECTOR-API-R004` | **Native content contracts.** The connector must publish packaged prompts, skills, ontology, and its manifest through `templateconnector_api/mcp_server.py`. | `scripts/generate_tool_schemas.py --check` must validate live tool contracts. Native content listing verification remains required before delivery. |
| `CONN-TEMPLATECONNECTOR-API-R005` | **Typed source observations.** The connector must submit authorized source observations through the shared ingest service in `templateconnector_api/kg_ingest.py`. | `tests/test_kg_ingest.py::test_ingest_maps_record_and_uses_submit` must observe typed changes at the submission boundary. |
