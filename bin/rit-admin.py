#! /usr/bin/env python

import os
import sys

from acmdrunner import Loader, execute_command


def run():
    packages_to_traverse = ('rit.app', 'rit.core')
    for package in packages_to_traverse:
        Loader.load_from_package(package)
    Loader.load_from_directory(os.path.dirname(os.getcwd()))
    execute_command(sys.argv[1], *sys.argv[2:])


if __name__ == '__main__':

    run()
