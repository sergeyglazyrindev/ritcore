import importlib

from wheezy.http import WSGIApplication
from wheezy.web.middleware import bootstrap_defaults
from wheezy.web.middleware import path_routing_middleware_factory
from rit.core.web.middleware_debug import rit_http_error_middleware_factory

from rit.core.web.urls import all_urls
from rit.app.conf.configure_template import get_template_handler
from rit.app.conf import settings


def get_application():

    imported_middlewares = []

    for middleware in settings.EXTRA_MIDDLEWARES:
        middleware_parts = list(middleware.rsplit('.', 1))
        mod = importlib.import_module(middleware_parts[0])
        imported_middlewares.append(getattr(mod, middleware_parts[1]))

    middlewares = [
        rit_http_error_middleware_factory,
        bootstrap_defaults(url_mapping=all_urls),
    ] + imported_middlewares + [
        path_routing_middleware_factory
    ]
    return WSGIApplication(
        middleware=middlewares,
        options={
            'render_template': get_template_handler()
        }
    )
