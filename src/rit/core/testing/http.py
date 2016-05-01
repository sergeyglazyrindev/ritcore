import json
from io import BytesIO
from functools import partial
from urllib import parse
from rit.core.web.wsgi import get_application
from rit.core.web.urls import all_urls
from wheezy.http.response import HTTP_STATUS
from wheezy.http import HTTPResponse
from wheezy.routing import PathRouter

application = get_application()

router = PathRouter()

for url in all_urls:
    router.add_route(*url)

HTTP_STATUS_STRING_TO_CODE = dict(zip(HTTP_STATUS.values(), HTTP_STATUS.keys()))


class FakePayload(object):
    """
    A wrapper around BytesIO that restricts what can be read since data from
    the network can't be seeked and cannot be read outside of its content_type    length. This makes sure that views can't do anything under the test client
    that wouldn't work in Real Life.
    """
    def __init__(self, content=None):
        self.__content = BytesIO()
        self.__len = 0
        self.read_started = False
        self.content_length = 0
        if content is not None:
            self.write(content)

    def __len__(self):
        return self.__len

    def read(self, num_bytes=None):
        if not self.read_started:
            self.__content.seek(0)
            self.read_started = True
        if num_bytes is None:
            num_bytes = self.__len or 0
        assert self.__len >= num_bytes, "Cannot read more than the available bytes from the HTTP incoming data."
        content = self.__content.read(num_bytes)
        self.__len -= num_bytes
        return content

    def write(self, content):
        if self.read_started:
            raise ValueError("Unable to write a payload after he's been read")
        self.__content.write(content)
        self.__len += len(content)
        self.content_length += len(content)

    def seek(self, pos):
        self.__content.seek(pos)
        self.__len = self.content_length - pos


class PostDefaultFormatter(object):

    @classmethod
    def format(cls, data):
        return data


class PostJsonFormatter(object):

    @classmethod
    def format(cls, data):
        return json.dumps(data)


def get_formatter_for(content_type):

    content_type_to_formatters = {
        'json': PostJsonFormatter
    }
    return content_type_to_formatters.get(content_type, PostDefaultFormatter)


class RitTestHttpClient(object):

    def __init__(self):
        self.errors = BytesIO()

    def _base_environ(self):
        environ = {
            'HTTP_COOKIE': '',
            'PATH_INFO': str('/'),
            'REMOTE_ADDR': str('127.0.0.1'),
            'REQUEST_METHOD': str('GET'),
            'SCRIPT_NAME': str(''),
            'SERVER_NAME': str('testserver'),
            'SERVER_PORT': str('80'),
            'SERVER_PROTOCOL': str('HTTP/1.1'),
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': str('http'),
            'wsgi.input': FakePayload(b''),
            'wsgi.errors': self.errors,
            'wsgi.multiprocess': True,
            'wsgi.multithread': False,
            'wsgi.run_once': False,
            'QUERY_STRING': '',
        }
        return environ

    def process(self, url=None, method='GET', data=None, environ=None, secure=False,
                content_type='html', route_name=None, encoding='UTF-8'):
        content_type_to_http_protocol_content_types = {
            'html': 'text/html; charset={}'.format(encoding),
            'json': 'application/json; charset={}'.format(encoding)
        }
        original_content_type = content_type
        content_type = content_type_to_http_protocol_content_types[content_type]
        if route_name:
            url = router.path_for(route_name)
        if url is None:
            raise ValueError('Please provide correct url for request or proper route_name')
        data = data or {}
        method = method.upper()
        response = HTTPResponse()
        r = self._base_environ()
        r.update({
            'PATH_INFO': url,
            'REQUEST_METHOD': str(method),
            'SERVER_PORT': str('443') if secure else str('80'),
            'wsgi.url_scheme': str('https') if secure else str('http'),
        })
        if method in ('POST', 'PUT'):
            formatter = get_formatter_for(original_content_type)
            data = formatter.format(data).encode(encoding)
            r.update({
                'CONTENT_LENGTH': len(data),
                'CONTENT_TYPE': str(content_type),
                'wsgi.input': FakePayload(data),
            })
        elif method == 'GET':
            # WSGI requires latin-1 encoded strings.
            r['QUERY_STRING'] = bytes(parse.urlencode(data), 'iso-8859-1').decode()
        r.update(environ or {})

        def wsgi_response_handler(response, status_string, headers):
            response.content_type = [header[1] for header in headers if header[0].lower() == 'content-type'].pop()
            response.status_code = HTTP_STATUS_STRING_TO_CODE[status_string]
            response.headers = headers

        output = application(r, partial(wsgi_response_handler, response))
        response.buffer = output
        return response
