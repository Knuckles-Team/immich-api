> **Work in progress — not released or deployment-ready.**
>
> This pilot converts the Immich 3.2.2 OpenAPI contract into 41 domain tools
> covering 276 declared operations. The canonical scaffold and publication
> bootstrap are reviewed; the auth adapter follow-up remains under integration.
> An isolated 13-case auth run passed, including the six unchanged canonical
> auth cases. Final-source full tests, packaging and deployment remain pending.
> Earlier converted-source tests had six auth-interface failures and one cold
> import timeout; do not treat the isolated follow-up result as a full-suite pass.
> The content follow-up passed 12 focused cases. Native SDK capture now finds
> 42 tools, 6 prompts, 12 resources and 55 content-pack entries, including the
> schema-derived ontology/shapes and four read skills. The new content has not
> been ingested into EG. Earlier public ping/version calls passed live using
> verified HTTPS and explicit HTTP opt-in. Writes remain disabled by default.
> Provider endpoints and credentials are supplied privately at runtime.

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
- **Schema-grounded content** — read skills, prompts, ontology, shapes and an opt-in
  bounded album preset are packaged; graph capture remains unverified.
- **Operational safety** — TLS profiles, bounded responses, loopback defaults, and
  immutable container references are part of the generated deployment contract.

## Quick start

This pilot is not published on PyPI. For source validation in an approved environment:

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
docker build --target mcp -t immich-api:mcp-local docker/
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
