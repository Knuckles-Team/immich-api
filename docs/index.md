# immich-api

Immich Api **API + MCP Server** using the connector SDK — a
typed, action-routed connector.

!!! info "Official documentation"
    This site is the canonical reference for `immich-api`, maintained alongside
    every release.

[![PyPI](https://img.shields.io/pypi/v/immich-api)](https://pypi.org/project/immich-api/)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
[![License](https://img.shields.io/pypi/l/immich-api)](https://github.com/Knuckles-Team/immich-api/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/Knuckles-Team/immich-api)

## Overview

`immich-api` wraps the target service with typed, deterministic MCP tools.

Tools resolve `IMMICH_API_BASE_URL`, `IMMICH_API_TOKEN_REF`, and the SDK TLS
profile when invoked. Discovery requires no vendor credentials or live service.

## Explore the documentation

<div class="grid cards" markdown>

- :material-rocket-launch: **[Installation](installation.md)** — pip, source, extras, and the prebuilt Docker image.
- :material-server-network: **[Deployment](deployment.md)** — run local transports or connect through an authenticated TLS ingress.
- :material-console: **[Usage](usage.md)** — the MCP tools, the Python client, and the CLI.
- :material-database-cog: **[Backing Platform](platform.md)** — deploy the target service with Docker.
- :material-sitemap: **[Overview](overview.md)** — the action-routed tool surface and architecture.
- :material-graph: **[Concepts](concepts.md)** — the CONCEPT ID registry.

</div>
