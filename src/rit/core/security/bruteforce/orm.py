import datetime
from sqlalchemy import Integer, Unicode, Column, DateTime, UniqueConstraint
from sqlalchemy.exc import IntegrityError
from rit.core.sqlalchemy_ext import Base
from rit.core.utils.datetime import RitDateTime


class CooldownStoreFactory(object):

    @classmethod
    def get_strategy(cls, strategy):
        return _registered_strategies[strategy]


class DbStoreStrategy(object):

    def __init__(self, bruteforce_client, db_handler=None):
        self.bruteforce_client = bruteforce_client
        self.db_handler = db_handler

    def remember_rudeness(self):
        bc = self.bruteforce_client
        cooldown = Cooldown()
        cooldown.resource = bc.resource
        cooldown.client = bc.client
        cooldown.threshold = bc.threshold
        cooldown.period = bc.period
        cooldown.cooldown = bc.cooldown
        self.db_handler.add(cooldown)
        try:
            self.db_handler.flush()
        except IntegrityError:
            update = {}
            update['expires_at'] = datetime.datetime.now() + datetime.timedelta(seconds=bc.cooldown)
            update['started'] = datetime.datetime.now()
            upd = Cooldown.__table__.update().values(**update).where(
                Cooldown.resource == bc.resource
            ).where(
                Cooldown.client == bc.client
            )
            self.db_handler.execute(upd)

    def if_client_blocked(self):
        bc = self.bruteforce_client
        return self.db_handler.query(Cooldown).filter(
            Cooldown.resource == bc.resource,
            Cooldown.client == bc.client,
            Cooldown.expires_at >= RitDateTime.now()
        ).count()

_registered_strategies = {
    'db': DbStoreStrategy
}


def set_expires_at_based_on_cooldown(context):
    return datetime.datetime.now() + datetime.timedelta(seconds=context.current_parameters['cooldown'])


class Cooldown(Base):
    __tablename__ = 'bruteforce_cooldown'

    id = Column(Integer, primary_key=True)
    resource = Column(Unicode(100), nullable=False)
    client = Column(Unicode(45), nullable=False)
    threshold = Column(Integer(), nullable=False)
    period = Column(Integer(), nullable=False)
    cooldown = Column(Integer(), nullable=False)
    started = Column(DateTime(), default=datetime.datetime.now)
    expires_at = Column(DateTime(), default=set_expires_at_based_on_cooldown)

    UniqueConstraint('resource', 'client', name='resource_client_constraint')
