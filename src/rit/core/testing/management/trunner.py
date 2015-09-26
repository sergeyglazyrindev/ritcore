import nose

from acmdrunner import BaseCommand
from rit.app.conf import settings


def setup_test_environment():
    pass


def teardown_test_environment():
    pass


class TestRunner(BaseCommand):

    def _parse_cargs(self, *args):
        nose_argv = ['nosetests'] + (list(args) or [])
        if hasattr(settings, 'NOSE_ARGS'):
            nose_argv = nose_argv + settings.NOSE_ARGS
        return nose_argv

    def execute(self, *args):
        nose_argv = self._parse_cargs(*args)
        setup_test_environment()
        nose.core.TestProgram(argv=nose_argv, exit=False)
        teardown_test_environment()
