from acmdrunner import register_command

from .trunner import TestRunner

register_command('test', TestRunner)
