from rit.core.ritmemcache import mc
from .exceptions import AttackerDetected


class RudenessCacheFactory(object):

    @classmethod
    def get_strategy(cls, strategy):
        return _registered_strategies[strategy]


def get_cache_key_for_client_and_resource(client, resource_name):
    return 'bc_' + client + '_' + resource_name


class RudenessCacheMemcache(object):

    def __init__(self, bruteforce_client):
        self.bruteforce_client = bruteforce_client

    def was_too_rude(self):
        bc = self.bruteforce_client
        key = get_cache_key_for_client_and_resource(bc.client, bc.resource)
        rudeness_count = mc.incr(key, delta=bc.threshold_increment)
        if not rudeness_count:
            success = mc.set(key, bc.threshold_increment, time=bc.period)
            if not success:
                return False
            too_rude = bc.threshold_increment > bc.threshold
        else:
            too_rude = rudeness_count > bc.threshold
        if too_rude and rudeness_count - bc.threshold_increment <= bc.threshold:
            raise AttackerDetected()
        return too_rude

# @todo, add redis strategy. quite important, memccache strategy is not reliable
_registered_strategies = {
    'memcache': RudenessCacheMemcache
}
