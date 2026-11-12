"""Surface contracts: tool use, links, data locations and business roles.

Drafted by ``python -m scion_sdk.testing.surface_draft complete``; edit freely.
"""

from scion_sdk.surface_contracts import (
    BusinessRole,
    Refusal,
    SurfaceLink,
    ToolStep,
    ToolUseContract,
)

CONTRACTS = (
    ToolUseContract(
        task="activities-operations",
        steps=(
            ToolStep(
                tool="activities_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="album-metadata-sample",
        steps=(
            ToolStep(
                tool="album_metadata_sample",
                params=(
                    "limit",
                ),
                result=(
                    "authoritative",
                    "complete",
                    "records",
                    "source_action",
                    "source_schema_sha256",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="NOT_FOUND",
                        when="the requested record does not exist",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="albums-operations",
        steps=(
            ToolStep(
                tool="albums_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="api-keys-operations",
        steps=(
            ToolStep(
                tool="api_keys_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="asset-files-operations",
        steps=(
            ToolStep(
                tool="asset_files_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="assets-operations",
        steps=(
            ToolStep(
                tool="assets_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="authentication-admin-operations",
        steps=(
            ToolStep(
                tool="authentication_admin_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="authentication-operations",
        steps=(
            ToolStep(
                tool="authentication_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="cluster-groups-operations",
        steps=(
            ToolStep(
                tool="cluster_groups_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="config-admin-operations",
        steps=(
            ToolStep(
                tool="config_admin_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="config-public-operations",
        steps=(
            ToolStep(
                tool="config_public_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="NOT_FOUND",
                        when="the requested record does not exist",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="config-user-operations",
        steps=(
            ToolStep(
                tool="config_user_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="NOT_FOUND",
                        when="the requested record does not exist",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="database-backups-admin-operations",
        steps=(
            ToolStep(
                tool="database_backups_admin_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="download-operations",
        steps=(
            ToolStep(
                tool="download_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="duplicates-operations",
        steps=(
            ToolStep(
                tool="duplicates_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="faces-operations",
        steps=(
            ToolStep(
                tool="faces_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="jobs-operations",
        steps=(
            ToolStep(
                tool="jobs_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="libraries-operations",
        steps=(
            ToolStep(
                tool="libraries_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="maintenance-admin-operations",
        steps=(
            ToolStep(
                tool="maintenance_admin_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="map-operations",
        steps=(
            ToolStep(
                tool="map_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="NOT_FOUND",
                        when="the requested record does not exist",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="memories-operations",
        steps=(
            ToolStep(
                tool="memories_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="notifications-admin-operations",
        steps=(
            ToolStep(
                tool="notifications_admin_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="notifications-operations",
        steps=(
            ToolStep(
                tool="notifications_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="partners-operations",
        steps=(
            ToolStep(
                tool="partners_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="people-operations",
        steps=(
            ToolStep(
                tool="people_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="plugins-operations",
        steps=(
            ToolStep(
                tool="plugins_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="NOT_FOUND",
                        when="the requested record does not exist",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="queues-operations",
        steps=(
            ToolStep(
                tool="queues_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="search-operations",
        steps=(
            ToolStep(
                tool="search_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="server-operations",
        steps=(
            ToolStep(
                tool="server_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="sessions-operations",
        steps=(
            ToolStep(
                tool="sessions_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="shared-links-operations",
        steps=(
            ToolStep(
                tool="shared_links_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="stacks-operations",
        steps=(
            ToolStep(
                tool="stacks_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="sync-operations",
        steps=(
            ToolStep(
                tool="sync_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="system-config-operations",
        steps=(
            ToolStep(
                tool="system_config_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="system-metadata-operations",
        steps=(
            ToolStep(
                tool="system_metadata_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="tags-operations",
        steps=(
            ToolStep(
                tool="tags_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="timeline-operations",
        steps=(
            ToolStep(
                tool="timeline_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="NOT_FOUND",
                        when="the requested record does not exist",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="trash-operations",
        steps=(
            ToolStep(
                tool="trash_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="users-admin-operations",
        steps=(
            ToolStep(
                tool="users_admin_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="users-operations",
        steps=(
            ToolStep(
                tool="users_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="views-operations",
        steps=(
            ToolStep(
                tool="views_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="NOT_FOUND",
                        when="the requested record does not exist",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="workflows-operations",
        steps=(
            ToolStep(
                tool="workflows_operations",
                result=(
                    "result",
                ),
                refusals=(
                    Refusal(
                        code="ACCESS_DENIED",
                        when="the credential lacks access to the operation",
                    ),
                    Refusal(
                        code="INVALID_ARGUMENT",
                        when="the upstream system rejects the input",
                    ),
                    Refusal(
                        code="CONFIRMATION_REQUIRED",
                        when="the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
)

LINKS = (
    SurfaceLink(
        task="immich-immich-administrator",
        tools=(
            "activities_operations",
            "album_metadata_sample",
            "albums_operations",
            "api_keys_operations",
            "asset_files_operations",
            "assets_operations",
            "authentication_admin_operations",
            "authentication_operations",
            "cluster_groups_operations",
            "config_admin_operations",
            "config_public_operations",
            "config_user_operations",
            "database_backups_admin_operations",
            "download_operations",
            "duplicates_operations",
            "faces_operations",
            "jobs_operations",
            "libraries_operations",
            "maintenance_admin_operations",
            "map_operations",
            "memories_operations",
            "notifications_admin_operations",
            "notifications_operations",
            "partners_operations",
            "people_operations",
            "plugins_operations",
            "queues_operations",
            "search_operations",
            "server_operations",
            "sessions_operations",
            "shared_links_operations",
            "stacks_operations",
            "sync_operations",
            "system_config_operations",
            "system_metadata_operations",
            "tags_operations",
            "timeline_operations",
            "trash_operations",
            "users_admin_operations",
            "users_operations",
            "views_operations",
            "workflows_operations",
        ),
        prompts=(
            "immich-immich-administrator",
        ),
    ),
    SurfaceLink(
        task="immich-operator",
        tools=(
            "activities_operations",
            "album_metadata_sample",
            "albums_operations",
            "api_keys_operations",
            "asset_files_operations",
            "assets_operations",
            "authentication_admin_operations",
            "authentication_operations",
            "cluster_groups_operations",
            "config_admin_operations",
            "config_public_operations",
            "config_user_operations",
            "database_backups_admin_operations",
            "download_operations",
            "duplicates_operations",
            "faces_operations",
            "jobs_operations",
            "libraries_operations",
            "maintenance_admin_operations",
            "map_operations",
            "memories_operations",
            "notifications_admin_operations",
            "notifications_operations",
            "partners_operations",
            "people_operations",
            "plugins_operations",
            "queues_operations",
            "search_operations",
            "server_operations",
            "sessions_operations",
            "shared_links_operations",
            "stacks_operations",
            "sync_operations",
            "system_config_operations",
            "system_metadata_operations",
            "tags_operations",
            "timeline_operations",
            "trash_operations",
            "users_admin_operations",
            "users_operations",
            "views_operations",
            "workflows_operations",
        ),
        prompts=(
            "immich-operator",
        ),
    ),
    SurfaceLink(
        task="immich_album_review",
        tools=(
            "album_metadata_sample",
            "api_keys_operations",
        ),
        prompts=(
            "immich_album_review",
        ),
    ),
    SurfaceLink(
        task="immich_asset_metadata",
        tools=(
            "assets_operations",
        ),
        prompts=(
            "immich_asset_metadata",
        ),
    ),
    SurfaceLink(
        task="immich_person_record",
        tools=(
            "people_operations",
        ),
        prompts=(
            "immich_person_record",
        ),
    ),
    SurfaceLink(
        task="immich_specialist",
        tools=(
            "server_operations",
        ),
        prompts=(
            "immich_specialist",
        ),
    ),
    SurfaceLink(
        task="main_agent",
        tools=(
            "activities_operations",
            "album_metadata_sample",
            "albums_operations",
            "api_keys_operations",
            "asset_files_operations",
            "assets_operations",
            "authentication_admin_operations",
            "authentication_operations",
            "cluster_groups_operations",
            "config_admin_operations",
            "config_public_operations",
            "config_user_operations",
            "database_backups_admin_operations",
            "download_operations",
            "duplicates_operations",
            "faces_operations",
            "jobs_operations",
            "libraries_operations",
            "maintenance_admin_operations",
            "map_operations",
            "memories_operations",
            "notifications_admin_operations",
            "notifications_operations",
            "partners_operations",
            "people_operations",
            "plugins_operations",
            "queues_operations",
            "search_operations",
            "server_operations",
            "sessions_operations",
            "shared_links_operations",
            "stacks_operations",
            "sync_operations",
            "system_config_operations",
            "system_metadata_operations",
            "tags_operations",
            "timeline_operations",
            "trash_operations",
            "users_admin_operations",
            "users_operations",
            "views_operations",
            "workflows_operations",
        ),
        prompts=(
            "main_agent",
        ),
    ),
    SurfaceLink(
        task="immich-album-review",
        tools=(
            "album_metadata_sample",
            "api_keys_operations",
        ),
        skills=(
            "immich-album-review",
        ),
    ),
    SurfaceLink(
        task="immich-asset-metadata",
        tools=(
            "api_keys_operations",
            "assets_operations",
        ),
        skills=(
            "immich-asset-metadata",
        ),
    ),
    SurfaceLink(
        task="immich-health",
        tools=(
            "server_operations",
        ),
        skills=(
            "immich-health",
        ),
    ),
    SurfaceLink(
        task="immich-person-record",
        tools=(
            "api_keys_operations",
            "people_operations",
        ),
        skills=(
            "immich-person-record",
        ),
    ),
)

LOCATIONS = ()

ROLES = (
    BusinessRole(
        name="immich administrator",
        tasks=(
            "activities-operations",
            "album-metadata-sample",
            "albums-operations",
            "api-keys-operations",
            "asset-files-operations",
            "assets-operations",
            "authentication-admin-operations",
            "authentication-operations",
            "cluster-groups-operations",
            "config-admin-operations",
            "config-public-operations",
            "config-user-operations",
            "database-backups-admin-operations",
            "download-operations",
            "duplicates-operations",
            "faces-operations",
            "jobs-operations",
            "libraries-operations",
            "maintenance-admin-operations",
            "map-operations",
            "memories-operations",
            "notifications-admin-operations",
            "notifications-operations",
            "partners-operations",
            "people-operations",
            "plugins-operations",
            "queues-operations",
            "search-operations",
            "server-operations",
            "sessions-operations",
            "shared-links-operations",
            "stacks-operations",
            "sync-operations",
            "system-config-operations",
            "system-metadata-operations",
            "tags-operations",
            "timeline-operations",
            "trash-operations",
            "users-admin-operations",
            "users-operations",
            "views-operations",
            "workflows-operations",
        ),
    ),
)
