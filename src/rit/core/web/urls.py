import os
from wheezy.routing import url
import importlib

from rit.core.dynamic_content.views import testdynamiccomponent

all_urls = [
    url(
        'testdynamiccomponent',
        testdynamiccomponent,
        name='testdynamiccomponent'
    ),
]
project_settings_module = os.getenv('RIT_SETTINGS_MODULE')
if project_settings_module:
    url_mod = importlib.import_module(project_settings_module.replace('settings', 'urls'))
    all_urls.extend(url_mod.urls)
