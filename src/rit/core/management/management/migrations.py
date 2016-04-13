import psycopg2
import os
import argparse

from amigrations import AMigrations
from rit.app.conf import settings
from rit.core.decorators.method_decorators import cached_property
from rit.core.db import sessions


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

    def _check_if_db_exists(self):
        try:
            dbname = sessions[self.alias].bind.url.database
            conn = self.db_client(dbname)
            conn.close()
            return True
        except psycopg2.OperationalError:
            return False

    def db_client(self, dbname=None):
        uri = sessions[self.alias].bind.url
        conn = psycopg2.connect(
            host=uri.host,
            user=uri.username,
            password=uri.password,
            port=uri.port,
            database=dbname
        )
        conn.autocommit = True
        return conn.cursor()

    def _drop_database(self):
        conn = self.db_client()
        dbname = sessions[self.alias].bind.url.database
        conn.execute('DROP DATABASE {}'.format(dbname))
        conn.close()

    def _create_database(self):
        conn = self.db_client()
        dbname = sessions[self.alias].bind.url.database
        conn.execute('CREATE DATABASE {}'.format(dbname))
        conn.close()

    def create_db(self):
        if self._check_if_db_exists():
            answer = input('The database {} exists. Would you like to drop it and create again ? Please answer y/N:'.format(self.alias))
            if answer.lower() == 'y':
                self._drop_database()

        self._create_database()

    def drop_db(self):
        if not self._check_if_db_exists():
            raise RuntimeError('The db {} doesn\'t exists'.format(self.alias))
        self._drop_database()

    def execute(self, action, *params):
        if settings.INST_TYPE != 'dev':
            raise RuntimeError('Impossible to run migrations on production')
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
