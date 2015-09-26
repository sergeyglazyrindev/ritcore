from wheezy.routing import url
from rit.core.dynamic_content.views import testdynamiccomponent

all_urls = [
    url(
        'testdynamiccomponent',
        testdynamiccomponent,
        name='testdynamiccomponent'
    ),
]
