import importlib
import subprocess
import sys
from contextlib import contextmanager
import argparse
import os


class VcsCommitHandler(object):

    def __init__(self, message):
        self.message = message

    def show_status(self):
        raise NotImplementedError()

    def is_there_any_changes(self):
        raise NotImplementedError()

    def add_all_files(self):
        raise NotImplementedError()

    def show_diff(self):
        raise NotImplementedError()

    def commit(self):
        raise NotImplementedError()

    def exit(self):
        sys.exit()


class GitCommitHandler(VcsCommitHandler):

    status_help_message = 'git status'
    diff_help_message = 'git diff'

    def is_there_any_changes(self):
        return bool(subprocess.check_output(['git', 'status', '-s']))

    def show_status(self):
        subprocess.call(['git status -s | less'], shell=True)

    def show_diff(self):
        subprocess.call(['git diff --cached | less'], shell=True)

    def add_all_files(self):
        subprocess.call(['git add `git rev-parse --show-toplevel`'], shell=True)

    def commit(self):
        subprocess.call(['git', 'commit', '-m', self.message])


def ask_if_user_agrees_with_changes(message):
    is_agree = input('Do you agree with such {} output/changes ? Please answer y/N:'.format(message))
    return is_agree.lower() == 'y'


@contextmanager
def commitcontextmanager(commithandler, pythonpackage=None):
    old_cwd = os.getcwd()

    def back_to_old_cwd():
        if pythonpackage:
            os.chdir(old_cwd)

    try:
        if pythonpackage:
            module = importlib.import_module(pythonpackage)
            os.chdir(os.path.dirname(module.__file__))
        if not commithandler.is_there_any_changes():
            yield
            return
        commithandler.show_status()
        if not ask_if_user_agrees_with_changes(commithandler.status_help_message):
            sys.exit()
        commithandler.add_all_files()
        commithandler.show_diff()
        if not ask_if_user_agrees_with_changes(commithandler.diff_help_message):
            sys.exit()
        commithandler.commit()
        yield
    finally:
        back_to_old_cwd()


def get_vcs_handler(vcs):
    allowed_vcs = {
        'git': GitCommitHandler
    }
    if vcs not in allowed_vcs:
        raise ValueError('We don\'t support {} vcs yet'.format(vcs))
    return allowed_vcs[vcs]


class CommitChangesCommand(object):

    extra_packages_possible_to_interact_with = ('rit.app', 'rit.core')

    def parse_cargs(self, *params):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-m',
            help='Message for migration',
            action='store',
            required=True
        )
        parser.add_argument(
            '--vcs',
            help='Version control system in use in this project',
            action='store',
            default='git',
            choices=('git', )
        )
        parser.add_argument(
            '--package',
            help='Python package you would like to interact with',
            action='store',
            choices=self.extra_packages_possible_to_interact_with
        )
        parsed_args = parser.parse_args(params)
        return parsed_args

    def _try_to_commit(self, commithandler, pythonpackage=None):
        with commitcontextmanager(commithandler, pythonpackage=pythonpackage):
            pass

    def execute(self, *params):
        params = self.parse_cargs(*params)
        commithandler = get_vcs_handler(params.vcs)
        self._try_to_commit(commithandler(params.m), params.package)
        if params.package:
            print('We successfully commited changes')
        else:
            for package in self.extra_packages_possible_to_interact_with:
                self._try_to_commit(commithandler(params.m), package)
