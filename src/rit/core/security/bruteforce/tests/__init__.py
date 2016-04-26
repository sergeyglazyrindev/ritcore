from unittest import TestCase

from .. import registry
from wheezy.http import HTTPRequest


class BaseBruteForceTestCase(TestCase):

    def make_client(self):
        client = registry.BruteForceClient('test-resource', 10, 100, 1000)
        request = HTTPRequest({'HTTP_X_FORWARDED_FOR': '127.0.0.1', 'REQUEST_METHOD': 'GET'}, 'utf-8', {})
        client.set_attacker(request)
        return client
