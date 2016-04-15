import mock
from contextlib import contextmanager


@contextmanager
def mock_db_for_tests(module=None):
    with mock.patch(module or 'rit.core.db.sessions'):
        yield
