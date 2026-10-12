# Usage — API / CLI / MCP

`immich-api` exposes the same capability three ways: as **MCP tools** an agent
calls, as a **Python API** you import, and as a **CLI**.

## As an MCP server

Once [deployed](deployment.md), the server registers consolidated, action-routed
tool modules. Each module is independently togglable with a `*TOOL` environment
flag.

## As a Python API

```python
from immich_api.auth import get_client

api = get_client()        # resolves SDK settings and credential references
status = api.get_system_status()
```

## As a CLI

Configure `IMMICH_API_BASE_URL`, `IMMICH_API_TOKEN_REF`, and one SDK TLS profile
selector through operator-provided settings, then run `immich-mcp --transport stdio`.

### Explicit HTTP endpoint

HTTPS remains the default. For an existing HTTP-only endpoint you are authorized
to use, set `IMMICH_API_BASE_URL=http://service.example.invalid` and explicitly
set `IMMICH_API_ALLOW_PLAINTEXT=true`. This forwards the SDK's
`HttpClientOptions.allow_plaintext` choice only to that vendor client. Requests
remain bound to its exact scheme, host and port; redirects stay disabled.
HTTP carries requests without TLS encryption. The flag never retries HTTPS over
HTTP, changes certificate verification, or authorizes another endpoint. OIDC
token exchanges retain their separate TLS policy. Leave the flag false for HTTPS.
