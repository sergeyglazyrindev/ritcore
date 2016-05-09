from rit.core.db import sessions


def get_db_handler_for_db_alias_middleware(request, following):
    assert following is not None
    request.get_db_handler_for_db_alias = lambda db_alias: sessions[db_alias]
    response = following(request)
    return response


def get_db_handler_for_db_alias_middleware_factory(options):
    return get_db_handler_for_db_alias_middleware
