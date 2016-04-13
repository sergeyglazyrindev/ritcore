from .migrations import Migrations
from .commit import CommitChangesCommand

from acmdrunner import register_command

register_command('migrations', Migrations)
register_command('commit', CommitChangesCommand)
