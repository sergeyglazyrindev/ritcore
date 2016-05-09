import importlib
from rit.app.conf import settings
from acmdrunner import CommandDispatcher
from rit.core.db import sessions


class EnvironmentBuilder(object):

    @classmethod
    def build(cls):
        env = Environment()
        env.cmd_dispatcher = CommandDispatcher()
        env.db_handler = sessions
        return env


class Environment(object):

    @property
    def cmd_dispatcher(self):
        return self._cmd_dispatcher

    @cmd_dispatcher.setter
    def cmd_dispatcher(self, dispatcher):
        self._cmd_dispatcher = dispatcher

    @property
    def db_handler(self):
        return self._db_handler

    @db_handler.setter
    def db_handler(self, db_handler):
        self._db_handler = db_handler

app_env = EnvironmentBuilder.build()


def get_env_for_app():
    if settings.CUSTOM_APP_ENVIRONMENT:
        return importlib.import_module(settings.CUSTOM_APP_ENVIRONMENT).app_env
    return app_env
