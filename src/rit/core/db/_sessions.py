from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rit.app.conf import settings

sessions = {}
for alias in ('default', 'default_slave'):
    Session = sessionmaker()
    engine = create_engine(settings.DATABASES[alias], echo=settings.DEBUG)
    Session.configure(bind=engine)
    sessions[alias] = Session()
