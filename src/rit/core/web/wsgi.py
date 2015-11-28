from wheezy.http import WSGIApplication
from wheezy.web.middleware import bootstrap_defaults
from wheezy.web.middleware import path_routing_middleware_factory
from rit.core.web.middleware_debug import rit_http_error_middleware_factory

from rit.core.web.urls import all_urls
from rit.app.conf.configure_template import template_handler
from rit.app.conf.settings import EXTRA_MIDDLEWARES

options = {
    'render_template': template_handler
}

middlewares = EXTRA_MIDDLEWARES + [
    rit_http_error_middleware_factory,
    bootstrap_defaults(url_mapping=all_urls),
    path_routing_middleware_factory,
]
application = WSGIApplication(
    middleware=middlewares,
    options=options
)
