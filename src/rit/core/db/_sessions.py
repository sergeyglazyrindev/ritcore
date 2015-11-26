from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rit.app.conf import settings

sessions = {}
for alias in ('default', 'default_slave'):
    engine = create_engine(
        settings.DATABASES[alias],
        echo=settings.DEBUG,
        isolation_level="AUTOCOMMIT"
    )

    Session = sessionmaker(bind=engine, autocommit=True)
    sessions[alias] = Session()
