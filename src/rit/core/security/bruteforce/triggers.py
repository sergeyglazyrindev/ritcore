from .cache import RudenessCacheFactory
from .orm import CooldownStoreFactory
from .exceptions import AttackerDetected


class RudenessTrigger(object):

    def __init__(self, bruteforce_client, cache_strategy='memcache', store_rude_strategy='db'):
        self.bruteforce_client = bruteforce_client
        self.cooldown_storage = CooldownStoreFactory.get_strategy(store_rude_strategy)(bruteforce_client)
        self.cache = RudenessCacheFactory.get_strategy(cache_strategy)(bruteforce_client)

    def was_too_rude(self, request):
        self.bruteforce_client.set_attacker(request)
        try:
            return self.cache.was_too_rude()
        except AttackerDetected:
            self.cooldown_storage.remember_rudeness()
            return True

    def if_client_blocked(self, request):
        self.bruteforce_client.set_attacker(request)
        return self.cooldown_storage.if_client_blocked()
