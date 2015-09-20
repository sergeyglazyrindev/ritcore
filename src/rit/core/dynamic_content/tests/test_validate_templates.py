import unittest

from rit.core.decorators import cached_property
from lxml import etree
from rit.core.dynamic_content import settings as dynamic_html_settings
from . import find_all_templates
from os import path


class ValidateProjectTemplatesTestCase(unittest.TestCase):

    def test_all_templates(self):
        for template_path in find_all_templates():
            self.__validate_template(template_path)

    def __validate_template(self, template_path):
        xsd_schema = self.xsd_schema
        parser = etree.XMLParser(schema=xsd_schema)
        with open(template_path) as fp:
            try:
                xml = fp.read()
                if not xml.startswith('<?xml version="1.0"?>'):
                    xml = u'<?xml version="1.0"?><root '
                    u' xmlns="http://www.w3.org/1999/xhtml">{}</root>'.format(
                        xml
                    )
                etree.fromstring(xml, parser)
            except etree.XMLSyntaxError as e:
                raise Exception('Bad xml syntax in file: {}. Error: {}'.format(
                    template_path,
                    e
                ))

    @cached_property
    def xsd_schema(self):
        with open(self.xsd_path) as fp:
            return etree.XMLSchema(etree.XML(fp.read()))

    @cached_property
    def xsd_path(self):
        return path.realpath(path.join(
            dynamic_html_settings.TEMPLATES_FOLDER,
            'xsd/base.xsd'
        ))
