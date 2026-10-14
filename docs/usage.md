# Usage — API and MCP

The pilot provides a Python client and the `immich-mcp` server entry point.
Its OpenAPI domain tools take typed operation arguments, not a free-form URL or
method. Read the [capability and evidence guide](immich-capabilities.md) first.

```json
{"action":"getAssetInfo","path":{"id":"00000000-0000-4000-8000-000000000001"}}
```

This example is for `assets_operations`; replace the illustrative UUID with one
explicitly selected by the caller. The client equivalent is:

```python
from immich_api.auth import get_client

result = get_client().execute("server", {"action": "pingServer"})
```

Configure `IMMICH_API_BASE_URL` as the provider origin without a path,
`IMMICH_API_AUTH_SCHEME` as a supported declared scheme, and
`IMMICH_API_TOKEN_REF` as an existing credential reference. Public health checks
can use an empty token reference. Keep `IMMICH_API_ALLOW_WRITES=false`.
Use `immich-mcp --transport stdio` for the local MCP transport.

## Explicit HTTP endpoint

HTTPS remains the default. For an existing HTTP-only endpoint you are authorized
to use, set `IMMICH_API_BASE_URL=http://service.example.invalid` and explicitly
set `IMMICH_API_ALLOW_PLAINTEXT=true`. The SDK permits this exact vendor origin
only; redirects remain disabled. This never downgrades HTTPS, disables certificate
verification, or changes the separate OIDC token client's TLS policy.
Leave the flag false for HTTPS.

## Reproduce the source test environment

Run `python scripts/bootstrap_environment.py` from this checkout, then use
`.ci/connector-venv/bin/python scripts/generate_tool_schemas.py --check` and
`.ci/connector-venv/bin/python -m pytest tests -q`. The helper verifies the frozen
lock, uses immutable SDK/EG source pins, refuses native builds, and records import
origins in `.ci/connector-environment.json`. This source-overlay environment does
not certify a complete release installation. Hosted checks use the same helper
before invoking the runner's provisioned pre-commit and scanner tools.

Mobile OAuth redirect responses expose the validated `location` as response data
with status 307. The client never follows that URI. Shared API-key clients discard
session cookies; subsequent requests retain the configured credential identity.
