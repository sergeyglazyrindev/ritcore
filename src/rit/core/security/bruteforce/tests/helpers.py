import contextlib
from rit.core.security.bruteforce.decorators import BruteForceDecorator


def mocked_bruteforce_call_method(func):
    def wrapper(self, orig_request, *args, **kwargs):
        return self.func(*args, **kwargs)
    return wrapper


def get_brute_force_decorator_mocked():
    return BruteForceDecoratorMocked


class BruteForceDecoratorMocked(object):

    def __init__(self, func, *args):
        self.func = func

    def _call(self, *args, **kwargs):
        self.func()


@contextlib.contextmanager
def mock_bruteforce_decorator():
    old_call = BruteForceDecorator._call
    BruteForceDecorator._call = mocked_bruteforce_call_method(old_call)
    yield
    BruteForceDecorator._call = old_call
