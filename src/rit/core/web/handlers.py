from wheezy.web.handlers import BaseHandler
from rit.app.conf.configure_template import get_template_handler
from wheezy.http import HTTPResponse
from wheezy.core.descriptors import attribute


class RitHttpHandler(BaseHandler):

    def error_response(self, error):
        resp = self.json_response({'error': error})
        resp.status_code = 400
        return resp

    @attribute
    def helpers(self):
        helpers = super(RitHttpHandler, self).helpers
        helpers['xsrf_token'] = self.xsrf_token
        return helpers


def simple_template_response(template, extra_data=None):

    extra_data = extra_data or {}
    template_handler = get_template_handler()
    response = HTTPResponse()
    response.write(template_handler(template, extra_data))
    return response
