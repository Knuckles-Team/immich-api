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

## Source dependency status

The tested development integration uses SDK commit `5babc4cc48ad73928468b243842f219f51e2cca1`
and EG Python commit `d33abec1e09b63cdcde01f8e8e4fe810d91cd43d`. The `uv.lock`
file is a resolver-generated development lock for those immutable Git sources.
Their static resolution metadata is copied from those exact package declarations
so lock resolution does not execute a native build. EG is an explicit development
dependency; the SDK runtime requirement remains `epistemic-graph>=2.27.0,<3`.

Resolution is not installation certification: the checked index only provided EG
through 2.23.0, and the SDK was unpublished there. Do not lower the requirement.
Approved SDK/EG distributions or an approved image-build environment are needed
before the following installation commands can succeed. The lock does not imply
PyPI availability, compatible native wheels, or a built container. No native
compilation was performed for this pilot.

## From source (after provisioning dependencies)

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
