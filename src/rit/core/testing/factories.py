import factory
from .db_sessions import get_session


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:

        sqlalchemy_session = get_session()
