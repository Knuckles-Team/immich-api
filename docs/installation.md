# Installation

This pilot is available as source. A published Python distribution and prebuilt
container image remain pending validation and release. Work from the connector
repository; no separate template repository access is required.

## Requirements

- **Python 3.12–3.14**.
- SDK configuration containing the service origin, a credential reference and TLS profile selectors.

## From PyPI (after release)

```bash
pip install immich-api
```

### Optional extras

| Extra | Install | Pulls in |
|---|---|---|
| `mcp` | `pip install "immich-api[mcp]"` | MCP runtime + SDK graph client |
| `all` | `pip install "immich-api[all]"` | Everything above |

## From source

```bash
git clone https://github.com/Knuckles-Team/immich-api.git
cd immich-api
pip install -e ".[mcp]"
```

## Docker

Use this only after a validated image digest has been published.

```bash
IMAGE_REF='<registry>/immich-api@sha256:<digest>'
docker pull "$IMAGE_REF"
```
