import os
import argparse

from amigrations import AMigrations
from rit.app.conf import settings
from rit.core.decorators.method_decorators import cached_property


class Migrations(object):

    def __init__(self, alias='default'):
        self.alias = alias
        self.migration_path = os.path.abspath(os.path.join(
            settings.PROJECT_ROOT,
            "migrations"
        ))

    @cached_property
    def amigrations(self):
        return AMigrations(
            settings.DATABASES[self.alias],
            self.migration_path,
            current_package=self.args.package,
            supported_packages=('rit.core', )
        )

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
        parser.add_argument(
            '--package',
            help='Use package for migrations',
            action='store'
        )
        parsed_args = parser.parse_args(params)
        return parsed_args

    def execute(self, action, *params):
        self.args = self.parse_cargs(*params)
        getattr(self, action)()

    def apply(self):
        if not self.args.to:
            print("Applying migrations")
            self.amigrations.upgrade()
        else:
            print("Downgrading migrations")
            self.amigrations.downgrade_to(self.args.to)

    def create(self):
        if not self.args.m:
            raise ValueError('Please provide message for migration')
        self.amigrations.create(self.args.m)
