import argparse
import nose

from rit.app.conf import settings
from rit.core.db._sessions import dispose_all_db_connections
from rit.core.environment.app import get_env_for_app

app_env = get_env_for_app()


def setup_test_environment():
    dispose_all_db_connections()
    app_env.cmd_dispatcher.execute_command('migrations', 'create_db')
    app_env.cmd_dispatcher.execute_command('migrations', 'apply')
    if app_env.cmd_dispatcher.is_registered('projectcustom-setup'):
        app_env.cmd_dispatcher.execute_command('projectcustom-setup')


def teardown_test_environment():
    dispose_all_db_connections()
    app_env.cmd_dispatcher.execute_command('migrations', 'apply', '--to', '0')
    app_env.cmd_dispatcher.execute_command('migrations', 'drop_db')
    if app_env.cmd_dispatcher.is_registered('projectcustom-teardown'):
        app_env.cmd_dispatcher.execute_command('projectcustom-teardown')


class TestRunner(object):

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

    def _get_settings_to_be_updated(self, c_params):
        databases = settings.DATABASES.copy()
        for alias in [db_alias for db_alias in databases
                      if not db_alias.endswith('_test')]:
            databases[alias] = databases[alias + '_test']
        return {
            'DATABASES': databases,
            'TESTING': True,
            'VERBOSE_LOGGING': bool(c_params.rit_verbose),
            'SETUP_DATABASE_SESSIONS': True
        }

    def _downgrade_settings(self):
        settings.pop_custom_settings()

    def __call__(self, *args):
        if settings.INST_TYPE != 'dev':
            raise RuntimeError('Impossible to run tests on production')
        c_params = self._parse_cargs(*args)
        with settings.push_custom_settings(
                self._get_settings_to_be_updated(c_params)
        ):
            nose_argv = self._prepare_nose_cargs(*args)
            setup_test_environment()
            nose.core.TestProgram(argv=nose_argv, exit=False)
            teardown_test_environment()
