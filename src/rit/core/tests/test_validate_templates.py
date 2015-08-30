import unittest

from rit.app import settings
from rit.core.decorators import cached_property
from lxml import etree
from os import path, walk
import fnmatch
from rit.core.dynamic_html import settings as dynamic_html_settings
from rit.core.dynamic_html import parse_dynamic_page_xml


def find_all_templates():
    folders_to_search_in = tuple([path.realpath(path.join(
        dynamic_html_settings.TEMPLATES_FOLDER,
        'basexml'
    )), ] + list(settings.TEMPLATE_FOLDERS))
    templates = []
    for folder in folders_to_search_in:
        for root, dirnames, filenames in walk(folder):
            for filename in fnmatch.filter(filenames, '*.xml'):
                templates.append(path.join(root, filename))
    return templates


class ValidateProjectTemplatesTestCase(unittest.TestCase):

    def test_all_templates(self):
        for template_path in find_all_templates():
            self.__validate_template(template_path)

    def __validate_template(self, template_path):
        dtd = self.dtd
        with open(template_path) as fp:
            try:
                template = etree.XML(fp.read())
                is_valid = dtd.validate(template)
                if not is_valid:
                    self.assertTrue(
                        is_valid,
                        'Error in xml file: {}. Errors: {}'.format(
                            template_path,
                            dtd.error_log.filter_from_errors()
                        )
                    )
                # try to parse a file by our parser
                print(parse_dynamic_page_xml(
                    template_path,
                ))
            except etree.XMLSyntaxError as e:
                raise Exception('Bad xml syntax in file: {}. Error: {}'.format(
                    template_path,
                    e
                ))

    @cached_property
    def dtd(self):
        return etree.DTD(self.dtd_path)

    @cached_property
    def dtd_path(self):
        return path.realpath(path.join(
            dynamic_html_settings.TEMPLATES_FOLDER,
            'dtds/base.dtd'
        ))
