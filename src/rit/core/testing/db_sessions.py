from rit.core.environment.app import get_env_for_app

_local_cached_sessions = {}


def get_session(alias='default'):
    app_env = get_env_for_app()
    if alias in _local_cached_sessions:
        return _local_cached_sessions[alias]

    _local_cached_sessions[alias] = app_env.db_handler[alias]
    return _local_cached_sessions[alias]
