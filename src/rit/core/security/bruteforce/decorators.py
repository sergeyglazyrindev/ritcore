import json
from .triggers import RudenessTrigger
from .registry import BruteForceClient
from wheezy.http import HTTPResponse
from restea.errors import ForbiddenError

ERROR_STATUS_CODE = 403


def bruteforce_protected_restea(resource, threshold, period, cooldown, *dec_args,
                                threshold_increment=1, db_alias='default', **dec_kwargs):
    def real_decorator(func):
        def wrapper(*args, **kwargs):
            brute_client = BruteForceClient(resource, threshold, period, cooldown, threshold_increment=threshold_increment)
            return BruteForceDecoratorRestEa(func, brute_client, db_alias)(*args, **kwargs)
        return wrapper
    return real_decorator


def bruteforce_protected_wheezy(resource, threshold, period, cooldown, *dec_args,
                                threshold_increment=1, db_alias='default', **dec_kwargs):

    def wrapper(func):
        brute_client = BruteForceClient(resource, threshold, period, cooldown, threshold_increment=threshold_increment)
        bruteforce_decorator = BruteForceDecoratorWheezy(func, brute_client, db_alias)

        def method_wrapper(view, *args, **kwargs):
            return bruteforce_decorator(view, *args, **kwargs)
        return method_wrapper
    return wrapper


class BruteForceDecoratorHandler(object):

    def __init__(self, func, brute_client, db_alias):
        self.func = func
        self.brute_client = brute_client
        self.db_alias = db_alias

    def _call(self, orig_request, *args, **kwargs):
        wheezy_request = None
        if hasattr(orig_request, '_original_request'):
            wheezy_request = orig_request._original_request
        request = wheezy_request or orig_request
        trigger = RudenessTrigger(self.brute_client, db_handler=request.get_db_handler_for_db_alias(self.db_alias))
        if trigger.was_too_rude(request):
            return self._error_response(orig_request, 'Sorry, but you tried to do that too often')
        if not trigger.if_client_blocked(request):
            return self.func(*args, **kwargs)
        else:
            return self._error_response(
                orig_request,
                'Sorry, but you are not able to do this right now.'
                ' You are blocked because of the suspicious activity.'
                ' If you think this is a mistake, please let us know.'
            )


class BruteForceDecoratorRestEa(BruteForceDecoratorHandler):

    def __call__(self, view, *args, **kwargs):
        orig_request = view.request
        return self._call(orig_request, view, *args, **kwargs)

    def _error_response(self, request, error):
        raise ForbiddenError(error)


class BruteForceDecoratorWheezy(BruteForceDecoratorHandler):

    def __call__(self, view, *args, **kwargs):
        orig_request = view.request
        return self._call(orig_request, view, *args, **kwargs)

    def _error_response(self, request, error):
        resp = HTTPResponse()
        resp.status_code = ERROR_STATUS_CODE
        resp.write_bytes(json.dumps({'error': error}))
        return resp
