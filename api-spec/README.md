# Pinned provider inputs

`immich.openapi.json` retains the original Immich 3.2.2 served OpenAPI bytes.
Its SHA-256 is `7db8383741eeb5c5c8c87a6221cd1cdd1206c8b1190b83363c64223a00bb020b`.
It contains 276 operations on 192 paths. Private deployment endpoints and
credentials are runtime inputs and are not preserved here.

`immich.provider-evidence.json` is the independently reviewed sidecar, SHA-256
`43f936578e5361b4400750ccb9e04747948eabe19baad0e78d90774c9c79c432`.
It classifies 17 absent security declarations using explicit provider decorators
and retains each operation's setup, password, OAuth or maintenance preconditions.
It adds only `assetData` to `AssetMediaCreateDto.required`; the source bytes and
all operation/security objects remain unchanged.

`provider-source/` contains the 13 exact evidence files from
[Immich commit 60b51cb3](https://github.com/immich-app/immich/tree/60b51cb3bc909e72fe963f4dfb1947515cb9ab3b).
The sidecar binds each file's SHA-256 and Git blob identity. These upstream files
retain their upstream [AGPL license](provider-source/LICENSE). The independently
reviewed disposition and citation-range notes are recorded in
`validation/provider-evidence-review-2026-10-13.json` at the repository root.

Regenerate from the exact `mcp-builder` revision recorded in
`validation/canonical-parity-generation-2026-10-13.json`, using its
`scripts/openapi_converter.py`:

```bash
python "$MCP_BUILDER/scripts/openapi_converter.py" \
  api-spec/immich.openapi.json immich_api --auth-scheme api_key \
  --provider-overlay api-spec/immich.provider-evidence.json \
  --expected-overlay-sha256 43f936578e5361b4400750ccb9e04747948eabe19baad0e78d90774c9c79c432 \
  --evidence-root api-spec/provider-source
```

Keep the existing handwritten `register_album_sample_tools` import in
`immich_api/mcp/__init__.py`; the normalized generation receipt identifies that
single domain registration addition. No source classification, synthetic test
budget or generated schema establishes live deployment acceptance.
