> **Work in progress — not released or deployment-ready.**
>
> Immich 3.2.2 supplies 276 operations in 41 domain tools plus the bounded album
> metadata tool. Writes default off. Provider evidence corrects the mobile OAuth
> callback to a 307 response with a validated Location value; redirects are never
> followed. Merged SDK `b9ee9ed0a82f6ecd5ed23d6226ca5ab503f74f9c` prevents a
> shared API-key client from retaining or forwarding login-session cookies.
> Merged canonical builder `2ea1591a5706b37afc79f47168d059de05b4b601` supplies
> the deterministic compiler and frozen source-overlay bootstrap. The 21 focused
> API/native redirect and cookie regressions passed in 5.81 seconds; see
> [current evidence](validation/focused-merged-sdk-b9ee9ed-2026-10-13.json).
> Normal commit and push checks gate publication. Historical 276 API plus 276
> native operation receipts remain under `validation/`; their revision bindings
> are preserved. Mocked tests do not establish provider/account permissions or
> production client discovery budgets. Ingestion presets remain disabled.
> The bootstrap installs locked registry wheels and imports the connector, SDK
> and EG from immutable source checkouts; it is not full release installation
> certification. No deployment, image build, live write or graph receipt is claimed.

# Immich Api

![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/immich-api)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/immich-api)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/immich-api)
![GitHub license](https://img.shields.io/github/license/Knuckles-Team/immich-api)
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/immich-api)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/immich-api)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/immich-api)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/immich-api)
![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/immich-api)
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/immich-api)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/immich-api)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/immich-api)
![PyPI - Version](https://img.shields.io/pypi/v/immich-api)
![PyPI - Downloads](https://img.shields.io/pypi/dd/immich-api)
![PyPI - License](https://img.shields.io/pypi/l/immich-api)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/immich-api)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/immich-api)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')

Immich Api API + MCP Server

The [documentation site](https://knuckles-team.github.io/immich-api/) contains the
planned API, deployment, security, and operational reference. Pages publication is
not configured yet; use the local documentation links below for this pilot. This README is the concise
entry point for installation and the supported runtime surfaces.

## Overview

`immich-api` is a typed provider package for the agent ecosystem. It combines a
small Python client with a governed MCP entry point. Configuration uses runtime credential references; resolved credentials and
private endpoints are never committed.

## Key capabilities

- **Typed boundaries** — Pydantic request and response models keep provider data
  explicit and validate it before it reaches an agent or graph.
- **One package, shared policy** — authentication, telemetry, action routing, and
  error handling follow the `agent-connector-sdk` contracts.
- **Schema-grounded content** — read skills, prompts, ontology and shapes are packaged; extraction presets remain disabled pending
  provider/account stream binding. Graph capture remains unverified.
- **Operational safety** — TLS profiles, bounded responses, loopback defaults, and
  immutable container references are part of the generated deployment contract.

## Quick start

Build and run from this connector checkout. Access to a separate template
repository is not required. The canonical scaffold belongs entirely to the
`mcp-builder` skill; future scaffolding uses its locally generated files and
ordinary repository creation. The pilot's original template commit remains
historical provenance in [validation/scaffold-origin.json](validation/scaffold-origin.json).

This pilot and its required SDK/EG dependency versions are not available from the
checked package index. The source-based development lock records exact tested
revisions; it does not supply native wheels. Once dependencies are provisioned
in an approved environment:

```bash
python -m pip install ".[mcp]"
immich-mcp
```

After a release is published, the distribution entry points will be:

```bash
python -m pip install "immich-api[mcp]"
immich-mcp
```

For an on-demand run, use `uvx`:

```bash
uvx --from "immich-api[mcp]" immich-mcp
```

The networked server binds to loopback by default:

```bash
immich-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

Container builds install this checkout, so the connector need not be published
first. Use the repository root as the context on an approved image-build host:

```bash
docker build --file docker/Dockerfile --target mcp -t immich-api:mcp-local .
```

See [deployment](docs/deployment.md) for an exact-commit build context and the
remaining dependency-closure requirements. No image build is claimed here.

## Architecture

The provider keeps the boundary between transport and domain code explicit:

```text
client → MCP entry point → typed tool module → API client → provider
                                  └── skills, prompts, ontology, connector presets
```

The OpenAPI tools take an `action` plus typed `path`, `query`, or `body` objects
when the selected operation requires them. For example, call `server_operations`
with `{"action":"pingServer"}`. The bounded `album_metadata_sample` tool takes `limit`. Regenerate `schemas/mcp_tools.json` with `python scripts/generate_tool_schemas.py`
after changing a tool contract, and keep the examples below aligned with that schema.

<!-- MCP-TOOLS-TABLE:START -->
<!-- MCP-TOOLS-TABLE:END -->

## MCP configuration

The server supports local `stdio` and authenticated `streamable-http` deployments.
Keep endpoint, credential, selector, and TLS references in SDK configuration; do not put
resolved values in client configuration.

```json
{
  "mcpServers": {
    "immich-mcp": {
      "command": "immich-mcp",
      "args": [],
      "env": {"SYSTEMTOOL": "true"}
    }
  }
}
```

For a networked deployment, use an authenticated TLS ingress and keep the allowlist in
`MCP_ALLOWED_HOSTS`. A configured remote example is `https://service.example.invalid/mcp`;
it is documentation-only and is never contacted by the generator.

<!-- MCP-CONFIG-EXAMPLES:START -->

```json
{
  "mcpServers": {
    "immich-mcp": {
      "command": "immich-mcp",
      "args": ["--transport", "streamable-http", "--port", "8000"],
      "env": {
        "TRANSPORT": "streamable-http",
        "HOST": "127.0.0.1",
        "PORT": "8000",
        "SYSTEMTOOL": "true"
      }
    }
  }
}
```

<!-- MCP-CONFIG-EXAMPLES:END -->

Container builds use immutable, least-privilege runtime stages:

```bash
docker build --file docker/Dockerfile --target mcp -t immich-api:mcp-local .
```

Deploy reviewed images by digest (`immich-api@sha256:<digest>`) and include
`--cap-drop=ALL` in the runtime policy. The [deployment guide](https://knuckles-team.github.io/immich-api/deployment/)
contains the complete transport and container examples.

## Documentation

Use the [Pages documentation](https://knuckles-team.github.io/immich-api/) for
installation details, API capabilities, deployment profiles, platform integration,
and the concept registry. The concise local references remain available at:

- [Installation](docs/installation.md)
- [Usage](docs/usage.md)
- [Immich capabilities and evidence](docs/immich-capabilities.md)
- [Deployment](docs/deployment.md)
- [Platform](docs/platform.md)
- [Concept registry](docs/concepts.md)

## Development

Create an isolated branch, install the test extra, and run the complete local gate:

```bash
uv sync --extra test
pytest tests -q
pre-commit run --all-files
```

Keep MCP examples and environment documentation aligned with the implemented settings.
Add focused positive and adversarial tests for every behavior change. See
`AGENTS.md` for the current module ownership and release checks.

## License

This project is distributed under the MIT license. See [LICENSE](LICENSE) for the
complete terms.
