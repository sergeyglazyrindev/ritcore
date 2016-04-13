from rit.core.db import sessions

_local_cached_sessions = {}


def get_session(alias='default'):
    if alias in _local_cached_sessions:
        return _local_cached_sessions[alias]

    _local_cached_sessions[alias] = sessions[alias]
    return _local_cached_sessions[alias]
