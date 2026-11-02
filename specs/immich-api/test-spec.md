# CONN-IMMICH-API — Verification plan

Governing specification: [spec.md](spec.md).

These acceptance targets require connector-specific execution and review.
Test names describe source mappings, not successful runs or delivery receipts.
Native content listing is proved by the connector-owned SDK test; a source listing does not establish live graph ingestion.

| Requirement | Verification target |
|---|---|
| `CONN-IMMICH-API-R001` | `tests/test_auth.py::test_client_resolves_reference_and_cleans_up` must observe reference resolution and resource cleanup. |
| `CONN-IMMICH-API-R002` | `tests/test_api_wrapper.py` must exercise rejected origins, redirects, deadlines, and oversized responses through the real client. |
| `CONN-IMMICH-API-R003` | `tests/test_immich_mcp_validation.py::test_mcp_instance_registration` must construct the production server without vendor requests. |
| `CONN-IMMICH-API-R004` | `scripts/generate_tool_schemas.py --check` must validate live tool contracts. `tests/test_immich_content.py::test_native_prompt_skill_shapes_and_tool_discovery` must render prompts and read the declared content through the production SDK server. |
| `CONN-IMMICH-API-R005` | `tests/test_kg_ingest.py::test_ingest_uses_scoped_binding_and_preserves_receipt` must observe typed changes at the submission boundary. |
| `CONN-IMMICH-API-R006` | `tests/test_operation_parity.py` must independently verify the pinned source inventory and reviewed provider evidence, retrieve complete native schemas within the explicit fixture budget, and execute every operation through the API and native discovery proxy. It must check serialized parameters and bodies, typed responses, explicit write approval and denial, required asset-file refusal before effects, multipart media, and single-attempt HTTP errors for every declared method. Mocked dispatch does not establish production client budgets, provider permissions or live service behavior. |

The owner must retain failure evidence and use canonical lifecycle tooling to regenerate `status.json`.

## Reviewed redirect and identity regressions

`tests/test_oauth_redirect_response.py` verifies the source-backed 307/Location
contract, bounded validation, no redirect following, and native MCP behavior.
`tests/test_session_auth_isolation.py` verifies login and OAuth responses cannot
replace configured API-key identity through shared API or native MCP clients.
The [merged SDK acceptance receipt](../../validation/focused-merged-sdk-b9ee9ed-2026-10-13.json)
records 21 passing cases. Normal pre-push tests provide the full candidate check;
source-overlay imports do not establish full release installation or live effects.

## CONN-IMMICH-API-R007

`tests/test_fleet_name.py::test_connector_name_is_the_fleet_name` reads every connector name in the package. Each one is `immich`.

## Rows awaiting bound tests
- `CONN-IMMICH-API-R008`: planned proof `tests/test_media_tags_tool.py::test_tool_returns_extracted_tags_with_revision`. Expected: Served tool on a recorded library response returns tags with origin extracted, producer_id immich-ml and a revision of server version plus model name, with image and thumbnail modalities.. Refusal: An asset the caller cannot read returns a refusal with no tags and no outbound read beyond the access check..
- `CONN-IMMICH-API-R009.1`: planned proof `tests/test_version_pin.py::test_unpinned_server_version_refuses_before_data_request`. Expected: A recorded server at the pinned major and minor passes and serves the data request.. Refusal: A recorded server at a newer minor refuses with SERVER_VERSION_UNPINNED and the recording shows zero data requests..
- `CONN-IMMICH-API-R009.2`: planned proof `tests/test_read_tools_served.py::test_read_tools_return_pages_and_refuse_bad_page_size`. Expected: Listing albums through the production server against a recorded library returns a page of at most the configured size with the read-only hint set.. Refusal: IMMICH_PAGE_SIZE of 0 or 1001 refuses with PAGE_SIZE_INVALID and sends no request..
- `CONN-IMMICH-API-R009.4`: planned proof `tests/test_incremental_ingest.py::test_cursor_advances_only_after_accepted_submission`. Expected: Two pages ingested with accepted submissions move the cursor to the largest updatedAt seen.. Refusal: A failed submission leaves the stored cursor unchanged..
- `CONN-IMMICH-API-R009.5`: planned proof `tests/test_incremental_ingest.py::test_replay_of_unchanged_page_submits_nothing`. Expected: Replaying one unchanged page submits zero changes and leaves the cursor; editing one field submits exactly one change.. Refusal: A replay with unchanged digests never calls submit with a changed record..
- `CONN-IMMICH-API-R009.6`: planned proof `tests/test_health_tool.py::test_health_reports_versions_and_refuses_unreachable`. Expected: Against a recorded library the tool returns ok, server_version, pinned_version and schema_digest.. Refusal: A dead address refuses with LIBRARY_UNREACHABLE..
- `CONN-IMMICH-API-R009.7`: planned proof `tests/test_upgrade_digest.py::test_mismatch_lists_added_and_removed_operations`. Expected: A recorded newer schema returns mismatch with the added and removed operation ids and both counts.. Refusal: An identical schema returns match; the pin file is unchanged after either call..
