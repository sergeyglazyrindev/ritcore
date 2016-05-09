import importlib
from rit.app.conf import settings
from acmdrunner import CommandDispatcher


class EnvironmentBuilder(object):

    @classmethod
    def build(cls):
        env = Environment()
        env.cmd_dispatcher = CommandDispatcher()
        return env


class Environment(object):

    @property
    def cmd_dispatcher(self):
        return self._cmd_dispatcher

    @cmd_dispatcher.setter
    def cmd_dispatcher(self, dispatcher):
        self._cmd_dispatcher = dispatcher

app_env = EnvironmentBuilder.build()


def get_env_for_app():
    if settings.CUSTOM_APP_ENVIRONMENT:
        return importlib.import_module(settings.CUSTOM_APP_ENVIRONMENT).app_env
    return app_env
