# CONN-IMMICH-API — Requirements

Governing specification: [spec.md](spec.md).

Each row identifies one connector behavior and its verification target.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-IMMICH-API-R001` | **Credential references.** The connector must resolve authorized credential references in `immich_api/auth.py` when a client is requested. | `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup. |
| `CONN-IMMICH-API-R002` | **Bounded API requests.** The connector must enforce origin, TLS, timeout, and response-size limits in `immich_api/openapi_runtime.py`. | `tests/test_api_wrapper.py` must exercise rejected origins, redirects, deadlines, and oversized responses through the real client. |
| `CONN-IMMICH-API-R003` | **MCP registration.** The connector must register its operation router through `immich_api/mcp_server.py` and `immich_api/mcp/__init__.py`. | `tests/test_immich_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests. |
| `CONN-IMMICH-API-R004` | **Native content contracts.** The connector must publish packaged prompts, skills, ontology, and its manifest through `immich_api/mcp_server.py`. | `scripts/generate_tool_schemas.py --check` must validate live tool contracts. `tests/test_immich_content.py::test_native_prompt_skill_shapes_and_tool_discovery` must render prompts and read the declared content through the production SDK server. |
| `CONN-IMMICH-API-R005` | **Typed source observations.** The connector must submit authorized source observations through the shared ingest service in `immich_api/kg_ingest.py`. | `tests/test_kg_ingest.py::test_ingest_uses_scoped_binding_and_preserves_receipt` must observe typed changes at the submission boundary. |
