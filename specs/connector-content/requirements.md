# CONN-IMMICH-API-CONNECTOR-CONTENT — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-IMMICH-API-CONNECTOR-CONTENT-R001` | **Default content.** `pyproject.toml` declares `immich` as the single `scion_sdk.connector` entry point. The server lists the packaged `skill://` and `ontology://` resources and the packaged prompts with no `content=` argument. Proving test: `tests/test_default_content_surfaces.py`. Caller chain: the `immich = immich_api:connector` entry point in `pyproject.toml` -> `immich_api/__init__.py::connector` (Connector(tools="immich_api.mcp")) -> `immich_api/mcp_server.py::get_mcp_instance` (line 15), which passes `ConnectorContent.for_package("immich_api", ...)` to `create_mcp_server`. Shape: content is the SDK `ConnectorContent.for_package` call in `immich_api/mcp_server.py` over the packaged `skills/`, `prompts/` and `ontology/` directories; no per-connector listing code exists, and the test lists resources and prompts through `fastmcp.Client`. | `resources/list` includes `skill://` and `ontology://`; `prompts/list` includes each packaged prompt. Test: `tests/test_default_content_surfaces.py::test_default_content_surfaces`. |
