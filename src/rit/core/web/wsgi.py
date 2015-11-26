from wheezy.http import WSGIApplication
from wheezy.web.middleware import bootstrap_defaults
from wheezy.web.middleware import path_routing_middleware_factory
from rit.core.web.middleware_debug import rit_http_error_middleware_factory

from rit.core.web.urls import all_urls
from rit.app.conf.configure_template import template_handler

options = {
    'render_template': template_handler
}
application = WSGIApplication(
    middleware=[
        rit_http_error_middleware_factory,
        bootstrap_defaults(url_mapping=all_urls),
        path_routing_middleware_factory,
    ],
    options=options
)
