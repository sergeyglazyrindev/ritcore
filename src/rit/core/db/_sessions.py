from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rit.app.conf import settings


class DbConfigurationException(object):
    pass


class DbSessionHandler(object):

    def __init__(self):
        self.__db_sessions = {}

    def __getitem__(self, db_alias):
        if settings.SETUP_DATABASE_SESSIONS and db_alias not in self.__db_sessions:
            self.setup_database_session(db_alias)
        if not settings.SETUP_DATABASE_SESSIONS and db_alias not in self.__db_sessions:
            raise DbConfigurationException('{} db could not initialized.'.format(db_alias))
        return self.__db_sessions[db_alias]

    def setup_database_session(self, db_alias):
        engine = create_engine(
            settings.DATABASES[db_alias],
            echo=settings.DEBUG,
            isolation_level="AUTOCOMMIT"
        )

        Session = sessionmaker(bind=engine, autocommit=True)
        self.__db_sessions[db_alias] = Session()

sessions = DbSessionHandler()
