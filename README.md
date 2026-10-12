# Templateconnector Api

![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/templateconnector-api)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/templateconnector-api)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/templateconnector-api)
![GitHub license](https://img.shields.io/github/license/Knuckles-Team/templateconnector-api)
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/templateconnector-api)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/templateconnector-api)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/templateconnector-api)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/templateconnector-api)
![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/templateconnector-api)
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/templateconnector-api)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/templateconnector-api)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/templateconnector-api)
![PyPI - Version](https://img.shields.io/pypi/v/templateconnector-api)
![PyPI - Downloads](https://img.shields.io/pypi/dd/templateconnector-api)
![PyPI - License](https://img.shields.io/pypi/l/templateconnector-api)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/templateconnector-api)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/templateconnector-api)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')

Templateconnector Api API + MCP Server

The [documentation site](https://knuckles-team.github.io/templateconnector-api/) contains the
full API, deployment, security, and operational reference. This README is the concise
entry point for installation and the supported runtime surfaces.

## Overview

`templateconnector-api` is a typed provider package for the agent ecosystem. It combines a
small Python client with a governed MCP entry point. Configuration uses runtime credential references; resolved credentials and
private endpoints are never committed.

## Key capabilities

- **Typed boundaries** — Pydantic request and response models keep provider data
  explicit and validate it before it reaches an agent or graph.
- **One package, shared policy** — authentication, telemetry, action routing, and
  error handling follow the `agent-connector-sdk` contracts.
- **Graph-ready content** — skills, prompts, ontology, and connector presets are
  packaged as discoverable data for the epistemic graph.
- **Operational safety** — TLS profiles, bounded responses, loopback defaults, and
  immutable container references are part of the generated deployment contract.

## Quick start

Install the package and run its generated entry points:

```bash
python -m pip install "templateconnector-api[mcp]"
templateconnector-mcp
```

For an on-demand run, use `uvx`:

```bash
uvx --from "templateconnector-api[mcp]" templateconnector-mcp
```

The networked server binds to loopback by default:

```bash
templateconnector-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

## Architecture

The provider keeps the boundary between transport and domain code explicit:

```text
client → MCP entry point → typed tool module → API client → provider
                                  └── skills, prompts, ontology, connector presets
```

The MCP surface uses action-routed tools. Pass an `action` and a JSON `params_json`
payload. Regenerate `schemas/mcp_tools.json` with `python scripts/generate_tool_schemas.py`
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
    "templateconnector-mcp": {
      "command": "templateconnector-mcp",
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
    "templateconnector-mcp": {
      "command": "templateconnector-mcp",
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
docker build --target mcp -t templateconnector-api:mcp-local docker/
```

Deploy reviewed images by digest (`templateconnector-api@sha256:<digest>`) and include
`--cap-drop=ALL` in the runtime policy. The [deployment guide](https://knuckles-team.github.io/templateconnector-api/deployment/)
contains the complete transport and container examples.

## Documentation

Use the [Pages documentation](https://knuckles-team.github.io/templateconnector-api/) for
installation details, API capabilities, deployment profiles, platform integration,
and the concept registry. The concise local references remain available at:

- [Installation](docs/installation.md)
- [Usage](docs/usage.md)
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
