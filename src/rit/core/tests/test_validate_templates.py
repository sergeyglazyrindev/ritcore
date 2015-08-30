import unittest

from rit.app import settings
from rit.core.decorators import cached_property
from lxml import etree
from os import path, walk
import fnmatch

cur_file_path = path.dirname(__file__)
basecore_folder = path.realpath(path.join(cur_file_path, '../'))


def find_all_templates():
    folders_to_search_in = tuple([path.realpath(path.join(
        basecore_folder,
        'templates/basexml'
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
        with open(template_path, 'r') as fp:
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
            except etree.XMLSyntaxError as e:
                raise Exception('Bad xml syntax in file: {}. Error: {}'.format(
                    template_path,
                    e
                ))

    @cached_property
    def dtd(self):
        dtd_path = path.realpath(path.join(
            basecore_folder,
            'templates/base.dtd'
        ))
        return etree.DTD(dtd_path)
