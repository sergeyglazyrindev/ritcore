#! /usr/bin/env python

import os
import sys
import importlib

from acmdrunner import Loader
from rit.core.environment.app import get_env_for_app


def run():
    packages_to_traverse = ('rit.app', 'rit.core')
    for package in packages_to_traverse:
        Loader.load_from_package(package)
    Loader.load_from_directory(os.path.dirname(__file__))
    app_env = get_env_for_app()
    try:
        app_env.cmd_dispatcher.execute_command(
            sys.argv[1], *sys.argv[2:]
        )
    except IndexError:
        print("All registered commands are:")
        app_env.cmd_dispatcher.list_all_commands()


if __name__ == '__main__':
    if os.getenv('RIT_SETTINGS_MODULE'):
        importlib.import_module(os.getenv('RIT_SETTINGS_MODULE'))
        os.environ['RIT_MIGRATION_PATH'] = os.path.dirname(__file__)
    run()
