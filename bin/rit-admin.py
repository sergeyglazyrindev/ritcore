#! /usr/bin/env python

import os
import sys
import importlib

from acmdrunner import Loader, execute_command, list_all_commands


def run():
    packages_to_traverse = ('rit.app', 'rit.core')
    for package in packages_to_traverse:
        Loader.load_from_package(package)
    Loader.load_from_directory(os.path.dirname(__file__))
    try:
        execute_command(sys.argv[1], *sys.argv[2:])
    except IndexError:
        print("All registered commands are:")
        list_all_commands()


if __name__ == '__main__':
    if os.getenv('RIT_SETTINGS_MODULE'):
        importlib.import_module(os.getenv('RIT_SETTINGS_MODULE'))
        os.environ['RIT_MIGRATION_PATH'] = os.path.dirname(__file__)
    run()
