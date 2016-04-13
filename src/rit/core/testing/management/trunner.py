import argparse
import nose

from acmdrunner import BaseCommand, execute_command
from rit.app.conf import settings
from rit.core.db._sessions import dispose_all_db_connections


def setup_test_environment():
    dispose_all_db_connections()
    execute_command('migrations', 'create_db')
    execute_command('migrations', 'apply')


def teardown_test_environment():
    dispose_all_db_connections()
    execute_command('migrations', 'apply', '--to', '0')
    execute_command('migrations', 'drop_db')


class TestRunner(BaseCommand):

    command_params = ('--rit-verbose', )

    def _prepare_nose_cargs(self, *args):
        nose_params = [arg for arg in args if arg not in self.command_params]
        nose_argv = ['nosetests'] + (list(nose_params) or [])
        if hasattr(settings, 'NOSE_ARGS'):
            nose_argv = nose_argv + settings.NOSE_ARGS
        return nose_argv

    def _parse_cargs(self, *params):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--rit-verbose',
            help='Turn on verbose output in tests',
            action='store_true',
        )
        parsed_args, _ = parser.parse_known_args(params)
        return parsed_args

    def _update_settings(self, c_params):
        databases = settings.DATABASES.copy()
        for alias in ('default', 'default_slave'):
            databases[alias] = databases[alias + '_test']

        settings.push_custom_settings({
            'DATABASES': databases,
            'TESTING': True,
            'VERBOSE_LOGGING': bool(c_params.rit_verbose)
        })

    def _downgrade_settings(self):
        settings.pop_custom_settings()

    def execute(self, *args):
        if settings.INST_TYPE != 'dev':
            raise RuntimeError('Impossible to run tests on production')
        c_params = self._parse_cargs(*args)
        self._update_settings(c_params)
        nose_argv = self._prepare_nose_cargs(*args)
        setup_test_environment()
        nose.core.TestProgram(argv=nose_argv, exit=False)
        teardown_test_environment()
        self._downgrade_settings()
