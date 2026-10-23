# Connector specifications

Follow the [shared spec standard](https://github.com/Knuckles-Team/pipelines/blob/7b3d18d72b5622d455ece3bbe45a9482bc6e8b5e/reference/spec-standard.md).

## Owner map

| Prefix | Owner |
|---|---|
| `CONN` | This connector's external-system behavior |
| `IMMICH` | This repository's concept registry |

- [`CONN-IMMICH-API`](immich-api/spec.md) — Integrate Immich Api through the shared connector contracts.
- [`CONN-IMMICH-API-CONNECTOR-CONTENT`](connector-content/spec.md) — The connector serves its packaged content.

The lifecycle generator owns delivery receipts in `status.json`.
Run `pipelines-hook spec-status --write` after reviewed source changes enter Git history.
Run `pipelines-hook spec-standard` and `pipelines-hook spec-decomposition` before publishing source changes.
See the [delivery dashboard](https://knuckles-team.github.io/immich-api/spec-delivery/).
