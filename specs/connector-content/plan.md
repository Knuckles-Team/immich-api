# CONN-IMMICH-API-CONNECTOR-CONTENT — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Architecture

`pyproject.toml` declares `immich` as the connector identity. `create_mcp_server` resolves the packaged content of `immich_api` from it.
