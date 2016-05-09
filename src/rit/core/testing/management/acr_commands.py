from .trunner import TestRunner
from rit.core.environment.app import get_env_for_app

app_env = get_env_for_app()

app_env.cmd_dispatcher.register_command('test', TestRunner())
