import os
import argparse

from amigrations import AMigrations
from rit.app.conf import settings


class Migrations(object):

    def __init__(self, alias='default'):
        self.migration_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "migrations"
        ))
        self.amigrations = AMigrations(settings.DATABASES[alias], self.migration_path)

    def parse_cargs(self, *params):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-m',
            help='Message for migration',
            action='store'
        )
        parser.add_argument(
            '--to',
            help='Downgrade database to passed id in database',
            action='store'
        )
        parsed_args = parser.parse_args(params)
        return parsed_args

    def execute(self, action, *params):
        args = self.parse_cargs(*params)
        getattr(self, action)(args)

    def apply(self, args):
        if not args.to:
            print("Applying migrations")
            self.amigrations.upgrade()
        else:
            print("Downgrading migrations")
            self.amigrations.downgrade_to(args.to)

    def create(self, args):
        if not args.m:
            raise ValueError('Please provide message for migration')
        self.amigrations.create(args.m)
