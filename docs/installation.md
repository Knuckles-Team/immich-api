# Installation

`immich-api` is a standard Python package and a prebuilt container image.

## Requirements

- **Python 3.12–3.14**.
- SDK configuration containing the service origin, a credential reference and TLS profile selectors.

## From PyPI (recommended)

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

```bash
IMAGE_REF='<registry>/immich-api@sha256:<digest>'
docker pull "$IMAGE_REF"
```
