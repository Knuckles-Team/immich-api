# Immich capabilities and evidence

This package binds the Immich 3.2.2 OpenAPI contract to 41 domain tools covering
276 declared operations. Inputs discriminate by the exact action enum, and the
client uses that action's fixed HTTP method and route. There is no arbitrary URL
or method dispatch. Writes are disabled by default, require MCP confirmation
when enabled, and are never automatically retried.

## Callable read capabilities

| Skill | Registered tools and actions | Scope |
|---|---|---|
| `immich-health` | `server_operations`: `pingServer`, `getServerVersion` | Public GET health/version only |
| `immich-album-review` | `api_keys_operations`: `getMyApiKey`; `album_metadata_sample` | Existing album-read authority; one record by default, five maximum |
| `immich-asset-metadata` | `assets_operations`: `getAssetInfo` | One caller-selected UUID and existing asset-read authority |
| `immich-person-record` | `people_operations`: `getPerson` | One explicitly requested person-record UUID and person-read authority |

The corresponding native MCP prompts contain the complete instructions; they do
not depend on an undeclared agent-connector-sdk prompt-composition runtime. The SDK
serves the skills, ontology, shapes and manifest as native MCP content. The
specialist prompt performs health checks; `main_agent` chooses the narrowest
read capability. User intent still limits use even when a credential has broader
permissions. The API-key introspection result must not be published wholesale.

`album_metadata_sample` is a small handwritten domain adapter in addition to the
41 generated tools. It calls `getAllAlbums` with `isOwned=true`, sorts by the
stable album UUID, and projects only id, album name, count, sharing flags and
creation/update timestamps. It excludes album membership, descriptions, emails,
paths and share secrets. Album names remain private account data. The API lacks
a server-side limit: all owned album metadata may be retrieved before projection,
subject to the fixed response-byte and time limits. The returned sample is always
non-authoritative, including when `complete=true`. It does not retrieve images.

## Structural ontology and shapes

`scripts/generate_immich_content.py` derives eight selected DTO classes and six
object relations from the pinned contract. Every property records its source
JSON pointer. Scalar types, UUID patterns, enum members, bounds, nullability and
required scalar presence come from the schema. Nullable scalar values can be
absent in RDF. Reference edges are validated when present, but their presence
is not required in a partial graph observation; `source_required` in provenance
retains the full DTO requirement. No related records are fabricated to fill gaps.

| Class | Source schema | Reference-backed relations |
|---|---|---|
| `ImmichAsset` | `AssetResponseDto` | owner → user; people → person records; tags → tags; stack → stack |
| `ImmichAlbum` | `AlbumResponseDto` | albumUsers → album memberships |
| `ImmichAlbumMembership` | `AlbumUserResponseDto` | user → user |
| `ImmichPersonRecord` | `PersonResponseDto` | None |
| `ImmichUser` | `UserResponseDto` | None |
| `ImmichLibrary` | `LibraryResponseDto` | None |
| `ImmichTag` | `TagResponseDto` | None |
| `ImmichAssetStack` | `AssetStackResponseDto` | None |

String fields such as thumbnail asset ID and primary asset ID remain scalar
identifiers. No album-contains-asset relationship is inferred. A person record
is a vendor grouping/label and is not equated to a verified real-world person.
Shared `Person`, `MediaAsset`, `Blob` and `Document` classes are not redefined.
The shapes describe the structural projection, not a complete provider response
or a certification of engine mapping. The minimal album sample intentionally
omits membership edges and nullable thumbnail data; it is not presented as a complete
`AlbumResponseDto` instance.

Source SHA256:
`7db8383741eeb5c5c8c87a6221cd1cdd1206c8b1190b83363c64223a00bb020b`.
`ontology/schema-provenance.json` pins the generated contract bytes and every
selected source pointer. Regenerate with `python scripts/generate_immich_content.py`
and verify with `--check`. The source operation and schema hash accompany each
sample. Provider URLs and credentials are runtime configuration.

## Disabled extraction preset and explicit graph submission

No MCP extraction preset is enabled. The reviewed SDK derives the stream from a
preset's fixed name, so a shared preset cannot bind identity to the configured
provider/account scope. It also defaults to FULL mode when neither an explicit
mode parameter nor incremental watermark is provided. A tool's
`authoritative=false` output does not change that SDK mode. Keeping the preset
absent prevents both cross-scope identity collision and empty-FULL ingestion.
The bounded read tool remains available without scheduling or ingestion.

Use an operator-bound source instance/account identity with an existing scoped
credential. The optional Python `ingest_album_metadata` helper requires an opaque
`source_scope` label and submits one to five projected entities through the SDK.
It maps provider fields into the actual `immichAlbum*` predicate names before
SDK submission, sends DELTA only, returns the complete engine receipt and
propagates refusal. Empty inputs fail before submission. It performs no
provider request, runs no import-time work, and is not exposed as a write tool.
The SDK privacy guard remains enabled. A pure SDK request preflight rejects an
identity changed by that guard before any submission; numeric-only UUIDs can
trigger its credit-card detector. Other redactions and engine shape validation
still require actual receipt/readback verification.
The remaining ontology classes are schema declarations, without enabled ingestion
mappings for live asset/person data. An ontology resource being served is not
semantic ingestion evidence.

## Acceptance status and next gates

Source-defined: deterministic OpenAPI dispatch, schema-grounded content,
bounded album projection, safe read capabilities and disabled extraction preset. Earlier SDK
runtime validation discovered the original 41 tools and served starter content;
public ping/version calls passed with HTTPS verification and explicit HTTP opt-in.
Those earlier counts do not certify this content follow-up. See PR evidence for
exact revision-specific checks.

Pending: final-source full checks, authenticated read-only validation, immutable
source-built image, fleet lease, and an actual bounded EG receipt plus readback.
The initial EG acceptance must persist at most one authorized album metadata
record, read it back under the same source/account scope, verify no excluded
fields or unexpected relations, and preserve the receipt and exact source/image
revisions. Do not claim completion based on object counts or successful startup.
