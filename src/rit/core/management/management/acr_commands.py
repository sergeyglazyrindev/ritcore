from .migrations import Migrations
from .commit import CommitChangesCommand
from .shell import ShellCommand
from .dbshell.command import OpenDbShellCommand

from rit.core.environment.app import get_env_for_app

app_env = get_env_for_app()
app_env.cmd_dispatcher.register_command('migrations', Migrations())
app_env.cmd_dispatcher.register_command('commit', CommitChangesCommand())
app_env.cmd_dispatcher.register_command('shell', ShellCommand())
app_env.cmd_dispatcher.register_command('dbshell', OpenDbShellCommand())
