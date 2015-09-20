from lxml import etree
import unittest
from os import path, walk
import fnmatch

from . import find_all_templates
from rit.core.dynamic_content import parse_dynamic_content_xml


class RenderProjectTemplatesTestCase(unittest.TestCase):

    def test_all_templates(self):
        for template_path in find_all_templates():
            self.__render_template(template_path)

    def __render_template(self, template_path):
        # try to parse a file by our parser
        parse_dynamic_content_xml(
            template_path,
            {}
        )


def find_templates_to_test_parser():
        folders_to_search_in = tuple([path.realpath(path.join(
            path.dirname(__file__),
            'testfixtures'
        )), ])
        templates = []
        for folder in folders_to_search_in:
            for root, dirnames, filenames in walk(folder):
                for filename in fnmatch.filter(filenames, '*.xml'):
                    templates.append(path.join(root, filename))
        return templates

parser = etree.XMLParser(remove_blank_text=True)


class ParserTestCase(unittest.TestCase):

    def test_all_templates(self):
        for template_path in find_templates_to_test_parser():
            self.__render_template(template_path)

    def __render_template(self, template_path):
        with open(template_path.replace('.xml', '.expected')) as fp:
            # try to parse a file by our parser
            self.assertEquals(
                etree.tostring(etree.XML(parse_dynamic_content_xml(
                    template_path,
                    {}
                ), parser=parser)),
                fp.read().encode('utf-8').strip()
            )
