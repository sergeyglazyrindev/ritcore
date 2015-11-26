import json
import time
from rit.app.conf import settings

PROJECT_ROOT = settings.PROJECT_ROOT


def load_file_timestamp_map(map_type):
    try:
        with open(PROJECT_ROOT + '/{}.json'.format(map_type)) as fp:
            return json.loads(fp.read())
    except IOError:
        return {}

JS_MAP = load_file_timestamp_map('js')
CSS_MAP = load_file_timestamp_map('css')


class AssetFileManager(object):

    template = None
    ext = None
    static_folder = None
    timestamp_map = None

    @classmethod
    def get_file_url(cls, file_path):
        if file_path.startswith('//'):
            return file_path
        timestamp = cls.timestamp_map.get(file_path, int(time.time()))
        return '{}{}{}/{}.{}?{}'.format(settings.ROOT_URL, settings.STATIC_PATH[1:], cls.static_folder,
                                        file_path, cls.ext, timestamp)

    @classmethod
    def include(cls, file_path):
        return cls.template.format(cls.get_file_url(file_path))


class CssAssetManager(AssetFileManager):

    template = '<link rel="stylesheet" href="{}"/>'
    ext = 'css'
    static_folder = 'stylesheets'
    timestamp_map = CSS_MAP


class JsAssetManager(AssetFileManager):

    template = '<script src="{}"></script>'
    ext = 'js'
    static_folder = 'javascripts'
    timestamp_map = JS_MAP


def include_js(context, js_file):
    return JsAssetManager.include(js_file)


def include_css(context, css_file):
    return CssAssetManager.include(css_file)
