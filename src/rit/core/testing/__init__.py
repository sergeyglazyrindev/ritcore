from unittest import TestCase
from wheezy.http import HTTPResponse
from .db_sessions import get_session
from sqlalchemy.exc import InvalidRequestError


class RitTypeEqualityMixin(object):

    def _compare_two_http_response_objects(self, first_obj, second_obj, msg=None):
        fields_to_be_compared = ('status_code', 'buffer', 'content_type')
        for field in fields_to_be_compared:
            try:
                self.assertEqual(getattr(first_obj, field), getattr(second_obj, field))
            except AssertionError as e:
                raise self.failureException(msg or str(e))

    def _init_all_equality_funcs(self):
        self.addTypeEqualityFunc(HTTPResponse, self._compare_two_http_response_objects)


class DbSessionHandler(object):

    def __init__(self, session):
        self.session = session
        self._transaction_started = False

    def begin(self):
        if self._transaction_started:
            return
        try:
            self.session.begin()
        except InvalidRequestError:
            pass
        self._transaction_started = True

    def __enter__(self):
        self.begin()
        return self.session

    def __exit__(self):
        self.rollback()

    def remove(self):
        self.session.remove()

    def rollback(self):
        if not self._transaction_started:
            raise RuntimeError('Transaction is not started')
        self.session.rollback()
        self._transaction_started = False


class RitDbTestCase(TestCase, RitTypeEqualityMixin):

    def setUp(self):
        # Prepare a new, clean session
        self.session = self.get_db_session()
        self.session.begin()

    def get_db_session(self, alias='default'):
        return DbSessionHandler(get_session(alias))

    def tearDown(self):
        # Rollback the session => no changes to the database
        self.session.rollback()
        # Remove it, so that the next test gets a new Session()
        self.session.remove()

    def __init__(self, *args):
        super(RitDbTestCase, self).__init__(*args)
        self._init_all_equality_funcs()
