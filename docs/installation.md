# Installation

`templateconnector-api` is a standard Python package and a prebuilt container image.

## Requirements

- **Python 3.12–3.14**.
- SDK configuration containing the service origin, a credential reference and TLS profile selectors.

## From PyPI (recommended)

```bash
pip install templateconnector-api
```

### Optional extras

| Extra | Install | Pulls in |
|---|---|---|
| `mcp` | `pip install "templateconnector-api[mcp]"` | MCP runtime + SDK graph client |
| `all` | `pip install "templateconnector-api[all]"` | Everything above |

## From source

```bash
git clone https://github.com/Knuckles-Team/templateconnector-api.git
cd templateconnector-api
pip install -e ".[mcp]"
```

## Docker

```bash
IMAGE_REF='<registry>/templateconnector-api@sha256:<digest>'
docker pull "$IMAGE_REF"
```
