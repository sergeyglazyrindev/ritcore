import mock

from .. import cache
from ..exceptions import AttackerDetected
from . import BaseBruteForceTestCase


class RudenessCacheTestCase(BaseBruteForceTestCase):

    def setUp(self):
        patcher = mock.patch('rit.core.security.bruteforce.cache.mc', autospec=True)
        self.memcache_mock = patcher.start()
        self.addCleanup(patcher.stop)

    def make_rudeness_cache(self, tried_count=1):
        self.memcache_mock.incr.return_value = tried_count
        rudeness = cache.RudenessCacheMemcache(self.make_client())
        return rudeness

    def test_success(self):
        cache = self.make_rudeness_cache()
        self.assertFalse(cache.was_too_rude())

    def test_attacker_detected(self):
        with self.assertRaises(AttackerDetected):
            cache = self.make_rudeness_cache(11)
            cache.was_too_rude()

    def test_too_rude(self):
        cache = self.make_rudeness_cache(20)
        self.assertTrue(cache.was_too_rude())
