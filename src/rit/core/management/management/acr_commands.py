from .migrations import Migrations

from acmdrunner import register_command

register_command('migrations', Migrations)
