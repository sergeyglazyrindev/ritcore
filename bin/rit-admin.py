#! /usr/bin/env python

import os
import sys
import importlib

from acmdrunner import Loader, execute_command


def run():
    packages_to_traverse = ('rit.app', 'rit.core')
    for package in packages_to_traverse:
        Loader.load_from_package(package)
    Loader.load_from_directory(os.path.dirname(__file__))
    execute_command(sys.argv[1], *sys.argv[2:])


if __name__ == '__main__':
    if os.getenv('RIT_SETTINGS_MODULE'):
        importlib.import_module(os.getenv('RIT_SETTINGS_MODULE'))
        os.environ['RIT_MIGRATION_PATH'] = os.path.dirname(__file__)
    run()
