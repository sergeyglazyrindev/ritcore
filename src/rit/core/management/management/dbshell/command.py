import argparse
from rit.app.conf import settings
from .uri import make_url
from .dialects import get_dialect_by_type


class OpenDbShellCommand(object):

    def parse_cargs(self, *params):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--db',
            help='Database to be connected to',
            action='store',
            choices=settings.DATABASES.keys(),
            default='default'
        )
        parsed_args = parser.parse_args(params)
        return parsed_args

    def __call__(self, *params):
        params = self.parse_cargs(*params)
        uri = make_url(settings.DATABASES[params.db])
        dialect = get_dialect_by_type(uri.get_backend_name())
        print(uri.get_backend_name())
        dialect(uri).open_shell()
