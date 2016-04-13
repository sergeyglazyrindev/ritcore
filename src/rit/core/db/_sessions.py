import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from rit.app.conf import settings


class DbConfigurationException(object):
    pass


def get_db_session_for_non_testing_environment(database_alias):
    kwargs_for_create_engine = {'isolation_level': 'AUTOCOMMIT', 'echo': settings.DEBUG}
    engine = create_engine(
        settings.DATABASES[database_alias],
        **kwargs_for_create_engine
    )

    kwargs_for_sessionmaker = {'autocommit': True}
    Session = sessionmaker(bind=engine, **kwargs_for_sessionmaker)
    return Session()


def get_db_session_for_testing_environment(db_alias):
    kwargs_for_create_engine = {'isolation_level': 'READ UNCOMMITTED'}
    if settings.VERBOSE_LOGGING:
        kwargs_for_create_engine['echo'] = True
    engine = create_engine(
        settings.DATABASES[db_alias],
        **kwargs_for_create_engine
    )

    kwargs_for_sessionmaker = {}
    Session = sessionmaker(bind=engine, **kwargs_for_sessionmaker)
    Session = scoped_session(Session)
    return Session


class DbSessionHandler(object):

    def __init__(self):
        self.__db_sessions = {}

    def __getitem__(self, db_alias):
        if settings.TESTING:
            '''We want to work always with masters in test environment'''
            db_alias = re.sub(r'_slave$', '', db_alias)
        if settings.SETUP_DATABASE_SESSIONS and db_alias not in self.__db_sessions:
            self.setup_database_session(db_alias)
        if not settings.SETUP_DATABASE_SESSIONS and db_alias not in self.__db_sessions:
            raise DbConfigurationException('{} db could not initialized.'.format(db_alias))
        return self.__db_sessions[db_alias]

    def setup_database_session(self, db_alias):
        if settings.TESTING:
            self.__db_sessions[db_alias] = get_db_session_for_testing_environment(db_alias)
        else:
            self.__db_sessions[db_alias] = get_db_session_for_non_testing_environment(db_alias)

    def __iter__(self):

        for session in self.__db_sessions.values():
            yield session

sessions = DbSessionHandler()


def dispose_all_db_connections():
    '''To be used in test runner but placed in right place'''
    for session in sessions:
        session.connection().close()
        session.bind.dispose()
