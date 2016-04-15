from .migrations import Migrations
from .commit import CommitChangesCommand
from .shell import ShellCommand
from .dbshell.command import OpenDbShellCommand

from acmdrunner import register_command

register_command('migrations', Migrations)
register_command('commit', CommitChangesCommand)
register_command('shell', ShellCommand)
register_command('dbshell', OpenDbShellCommand)
