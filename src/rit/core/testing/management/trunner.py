import nose

from acmdrunner import BaseCommand, execute_command
from rit.app.conf import settings


def setup_test_environment():
    execute_command('migrations', 'apply')


def teardown_test_environment():
    execute_command('migrations', 'apply', '--to', '0')


class TestRunner(BaseCommand):

    def _parse_cargs(self, *args):
        nose_argv = ['nosetests'] + (list(args) or [])
        if hasattr(settings, 'NOSE_ARGS'):
            nose_argv = nose_argv + settings.NOSE_ARGS
        return nose_argv

    def _update_settings(self):
        self._old_databases = settings.DATABASES.copy()
        for alias in ('default', 'default_slave'):
            settings.DATABASES[alias] = settings.DATABASES[alias + '_test']
        setattr(settings, 'TESTING', True)

    def _downgrade_settings(self):
        settings.DATABASES = self._old_databases
        delattr(settings, 'TESTING')

    def execute(self, *args):
        self._update_settings()
        nose_argv = self._parse_cargs(*args)
        setup_test_environment()
        nose.core.TestProgram(argv=nose_argv, exit=False)
        teardown_test_environment()
        self._downgrade_settings()
