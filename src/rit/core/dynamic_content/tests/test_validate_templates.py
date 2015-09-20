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
                # @todo, maybe we can skip this logic, but how do we
                # validate xml without it ? placing it in all template
                # sounds bad, we need to specify namespace, so xml
                # would be validated
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
        xsd_path = self.xsd_path
        with open(xsd_path) as fp:
            schema = fp.read()
            # @todo, improve, bad case:
            # but how to run tests within another projects placed
            # in the same namespace ?
            # nosetests --traverse-namespace does this thing but we
            # need to properly specify current_html_xsd_path, if we
            # don't (means, hardcode in template as relative to
            # current directory), it would fail because it strictly
            # relies on the folder we currently here at (when run tests)
            schema = schema.format(
                current_html_xsd_location=path.dirname(xsd_path)
            )
            return etree.XMLSchema(etree.XML(schema))

    @cached_property
    def xsd_path(self):
        return path.realpath(path.join(
            dynamic_html_settings.TEMPLATES_FOLDER,
            'xsd/base.xsd'
        ))
