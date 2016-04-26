from rit.core.utils.ip import get_ip_address_from_request_forwarded_for
from .exceptions import AttackerNotRecognized

_registered_resources = []


class BruteForceClient(object):

    def __init__(self, resource, threshold, period, cooldown, threshold_increment=1):
        self.resource = resource
        self.threshold = threshold
        self.period = period
        self.cooldown = cooldown
        self.threshold_increment = threshold_increment
        self.client = None

    def set_attacker(self, request):
        if self.client:
            return
        self.client = get_ip_address_from_request_forwarded_for(request)
        if not self.client:
            raise AttackerNotRecognized()
