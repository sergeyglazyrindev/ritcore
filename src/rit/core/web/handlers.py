from wheezy.web.handlers import BaseHandler


class RitHttpHandler(BaseHandler):

    def error_response(self, error):
        resp = self.json_response({'error': error})
        resp.status_code = 400
        return resp
