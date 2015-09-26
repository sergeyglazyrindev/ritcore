import argparse
import nose

from acmdrunner import BaseCommand
from rit.app.conf import settings


def setup_test_environment():
    pass


def teardown_test_environment():
    pass


class TestRunner(BaseCommand):

    def _parse_cargs(self, *args):
        parser = argparse.ArgumentParser()
        parser.add_argument('--traverse-namespace', help="Traverse all packages in namespace"
                            "and executes all needed tests", action="store_true", default=False)
        args = parser.parse_args(args=args)
        nose_argv = ['-x', '-s']
        if hasattr(settings, 'NOSE_ARGS'):
            nose_argv = nose_argv + settings.NOSE_ARGS
        if args.traverse_namespace:
            nose_argv = nose_argv + ['--traverse-namespace', 'rit']
        return nose_argv

    def execute(self, *args):
        nose_argv = self._parse_cargs(*args)
        setup_test_environment()
        nose.core.TestProgram(argv=nose_argv, exit=False)
        teardown_test_environment()
