import json
from .triggers import RudenessTrigger
from .registry import BruteForceClient
from wheezy.http import HTTPResponse
from restea.errors import ForbiddenError

ERROR_STATUS_CODE = 403


def bruteforce_protected(resource, threshold, period, cooldown, *dec_args,
                         threshold_increment=1, db_alias='default', **dec_kwargs):

    def wrapper(func):
        brute_client = BruteForceClient(resource, threshold, period, cooldown, threshold_increment=threshold_increment)
        trigger = RudenessTrigger(brute_client, db_alias=db_alias)
        return BruteForceDecorator(func, trigger)
    return wrapper


def bruteforce_protected_wheezy(resource, threshold, period, cooldown, *dec_args,
                                threshold_increment=1, db_alias='default', **dec_kwargs):

    def wrapper(func):
        brute_client = BruteForceClient(resource, threshold, period, cooldown, threshold_increment=threshold_increment)
        trigger = RudenessTrigger(brute_client, db_alias=db_alias)
        bruteforce_decorator = BruteForceDecorator(func, trigger)

        def method_wrapper(view, *args, **kwargs):
            return bruteforce_decorator(view, *args, **kwargs)
        return method_wrapper
    return wrapper


class BruteForceDecoratorHandler(object):

    def __init__(self, func, trigger):
        self.func = func
        self.trigger = trigger

    def _call(self, orig_request, *args, **kwargs):
        wheezy_request = None
        if hasattr(orig_request, '_original_request'):
            wheezy_request = orig_request._original_request
        request = wheezy_request or orig_request
        if self.trigger.was_too_rude(request):
            return self.__error_response(orig_request, 'Sorry, but you tried to do that too often')
        if not self.trigger.if_client_blocked(request):
            return self.func(*args, **kwargs)
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


class BruteForceDecorator(BruteForceDecoratorHandler):

    def __call__(self, view, *args, **kwargs):
        orig_request = view.request
        return self._call(orig_request, view, *args, **kwargs)
