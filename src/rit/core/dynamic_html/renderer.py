from lxml import etree
from collections import defaultdict
from rit.core.decorators import cached_property


class DynamicContentElementHandler(object):

    def __init__(self, element, output):
        self.element = element
        self.output = output

    def parse(self):

        self.output.write_to_header('<b></b>')


class DynamicContentXmlOutput(object):

    def __init__(self):
        self._header = defaultdict(str)
        self._body_blocks = defaultdict(str)

    def write_to_header(self, html, header_type='common'):
        self._header[header_type] += html

    @cached_property
    def context(self):
        context = self._body_blocks.copy()
        context.update({
            'header_' + block_key: block_value
            for block_key, block_value in self._header.items()
        })
        return context


class DynamicContentXmlLoader(object):

    def __init__(self, template):
        self.template = template

    def load(self):
        with open(self.template) as fp:
            tree = etree.parse(fp)
            return DynamicContentXmlParser(tree).parse()


class DynamicContentXmlParser(object):

    def __init__(self, tree, context={}, output=None):
        self.tree = tree
        self.context = {}
        self.output = output or DynamicContentXmlOutput()

    def parse(self):

        root = self.tree.getroot()
        DynamicContentElementHandler(root, self.output).parse()
        for el in root.getchildren():
            DynamicContentXmlParser(el, self.context, self.output).parse()

        return self.output.context


def parse_dynamic_page_xml(template_path):
    return DynamicContentXmlLoader(template_path).load()
