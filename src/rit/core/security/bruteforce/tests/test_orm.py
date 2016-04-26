from dateutil import relativedelta
import datetime
import mock

from .. import orm
from . import BaseBruteForceTestCase


class DbBruteForceOrmTestCase(BaseBruteForceTestCase):

    def test(self):
        db = orm.DbStoreStrategy(self.make_client())
        db.remember_rudeness()
        self.assertTrue(db.if_client_blocked())
        with mock.patch('rit.core.security.bruteforce.orm.RitDateTime', autospec=True) as datetime_mocked:
            datetime_mocked.now.return_value = datetime.datetime.now() + relativedelta.relativedelta(months=1)
            self.assertFalse(db.if_client_blocked())
