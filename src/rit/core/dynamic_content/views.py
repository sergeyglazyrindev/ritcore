import os
from wheezy.http import HTTPResponse
from lxml import etree

from rit.core.dynamic_content.settings import TEMPLATES_FOLDER
from rit.core.dynamic_content.shortcuts import parse_dynamic_content_xml


def testdynamiccomponent(request):
    resp = HTTPResponse()
    resp.write(
        etree.tostring(etree.XML(parse_dynamic_content_xml(
            os.path.join(TEMPLATES_FOLDER, 'basexml/test.xml'),
            {}
        ))).decode('utf-8')
    )
    return resp
