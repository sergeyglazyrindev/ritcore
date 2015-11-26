import json
from .triggers import RudenessTrigger
from .registry import BruteForceClient
from wheezy.http import HTTPResponse
from restea.errors import ForbiddenError

ERROR_STATUS_CODE = 403


def bruteforce_protected(resource, threshold, period, cooldown, *dec_args,
                         threshold_increment=1, **dec_kwargs):

    def wrapper(func):
        brute_client = BruteForceClient(resource, threshold, period, cooldown, threshold_increment=threshold_increment)
        trigger = RudenessTrigger(brute_client)
        return BruteForceDecorator(func, trigger)
    return wrapper


class BruteForceDecorator(object):

    def __init__(self, func, trigger):
        self.func = func
        self.trigger = trigger

    def __call__(self, view, *args, **kwargs):
        orig_request = view.request
        wheezy_request = None
        if hasattr(orig_request, '_original_request'):
            wheezy_request = orig_request._original_request
        request = wheezy_request or orig_request
        if self.trigger.was_too_rude(request):
            return self.__error_response(orig_request, 'Sorry, but you tried to do that too often')
        if not self.trigger.if_client_blocked(request):
            return self.func(view, *args, **kwargs)
        else:
            return self.__error_response(
                orig_request,
                'Sorry, but you are not able to do this right now.'
                ' You are blocked because of the suspicious activity.'
                ' If you think this is a mistake, please let us know.'
            )

    def __error_response(self, request, error):
        if hasattr(request, '_original_request'):
            raise ForbiddenError(error)
        else:
            resp = HTTPResponse()
            resp.status_code = ERROR_STATUS_CODE
            resp.write_bytes(json.dumps({'error': error}))
            return resp
