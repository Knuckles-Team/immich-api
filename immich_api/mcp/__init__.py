from ..auth import get_client
from ..openapi_runtime import register_domain
from .album_sample import register_album_sample_tools as register_album_sample_tools


def register_activities_tools(mcp):
    register_domain(mcp, 'activities', get_client)

def register_albums_tools(mcp):
    register_domain(mcp, 'albums', get_client)

def register_api_keys_tools(mcp):
    register_domain(mcp, 'api_keys', get_client)

def register_asset_files_tools(mcp):
    register_domain(mcp, 'asset_files', get_client)

def register_assets_tools(mcp):
    register_domain(mcp, 'assets', get_client)

def register_authentication_tools(mcp):
    register_domain(mcp, 'authentication', get_client)

def register_authentication_admin_tools(mcp):
    register_domain(mcp, 'authentication_admin', get_client)

def register_cluster_groups_tools(mcp):
    register_domain(mcp, 'cluster_groups', get_client)

def register_config_admin_tools(mcp):
    register_domain(mcp, 'config_admin', get_client)

def register_config_public_tools(mcp):
    register_domain(mcp, 'config_public', get_client)

def register_config_user_tools(mcp):
    register_domain(mcp, 'config_user', get_client)

def register_database_backups_admin_tools(mcp):
    register_domain(mcp, 'database_backups_admin', get_client)

def register_download_tools(mcp):
    register_domain(mcp, 'download', get_client)

def register_duplicates_tools(mcp):
    register_domain(mcp, 'duplicates', get_client)

def register_faces_tools(mcp):
    register_domain(mcp, 'faces', get_client)

def register_jobs_tools(mcp):
    register_domain(mcp, 'jobs', get_client)

def register_libraries_tools(mcp):
    register_domain(mcp, 'libraries', get_client)

def register_maintenance_admin_tools(mcp):
    register_domain(mcp, 'maintenance_admin', get_client)

def register_map_tools(mcp):
    register_domain(mcp, 'map', get_client)

def register_memories_tools(mcp):
    register_domain(mcp, 'memories', get_client)

def register_notifications_tools(mcp):
    register_domain(mcp, 'notifications', get_client)

def register_notifications_admin_tools(mcp):
    register_domain(mcp, 'notifications_admin', get_client)

def register_partners_tools(mcp):
    register_domain(mcp, 'partners', get_client)

def register_people_tools(mcp):
    register_domain(mcp, 'people', get_client)

def register_plugins_tools(mcp):
    register_domain(mcp, 'plugins', get_client)

def register_queues_tools(mcp):
    register_domain(mcp, 'queues', get_client)

def register_search_tools(mcp):
    register_domain(mcp, 'search', get_client)

def register_server_tools(mcp):
    register_domain(mcp, 'server', get_client)

def register_sessions_tools(mcp):
    register_domain(mcp, 'sessions', get_client)

def register_shared_links_tools(mcp):
    register_domain(mcp, 'shared_links', get_client)

def register_stacks_tools(mcp):
    register_domain(mcp, 'stacks', get_client)

def register_sync_tools(mcp):
    register_domain(mcp, 'sync', get_client)

def register_system_config_tools(mcp):
    register_domain(mcp, 'system_config', get_client)

def register_system_metadata_tools(mcp):
    register_domain(mcp, 'system_metadata', get_client)

def register_tags_tools(mcp):
    register_domain(mcp, 'tags', get_client)

def register_timeline_tools(mcp):
    register_domain(mcp, 'timeline', get_client)

def register_trash_tools(mcp):
    register_domain(mcp, 'trash', get_client)

def register_users_tools(mcp):
    register_domain(mcp, 'users', get_client)

def register_users_admin_tools(mcp):
    register_domain(mcp, 'users_admin', get_client)

def register_views_tools(mcp):
    register_domain(mcp, 'views', get_client)

def register_workflows_tools(mcp):
    register_domain(mcp, 'workflows', get_client)

