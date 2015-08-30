from lxml import etree
from collections import defaultdict
from rit.core.decorators import cached_property


class DynamicContentElementHandler(object):

    def __init__(self, element):
        self.element = element

    def parse(self, env):

        env.output.write_to_header('<b></b>')


class DynamicContentXmlEnvironment(object):

    def __init__(self, context):

        self.output = DynamicContentXmlOutput()
        self.context = context


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

    def __init__(self, template, context):
        self.template = template
        self.env = DynamicContentXmlEnvironment(context)

    def load(self):
        with open(self.template) as fp:
            tree = etree.parse(fp)
            return DynamicContentXmlParser(tree).parse(self.env)


class DynamicContentXmlParser(object):

    def __init__(self, tree):
        self.tree = tree

    def parse(self, env):

        root = self.tree.getroot()
        DynamicContentElementHandler(root).parse(env)
        for el in root.getchildren():
            DynamicContentXmlParser(el).parse(env)

        return env.output.context


def parse_dynamic_page_xml(template_path, context={}):
    return DynamicContentXmlLoader(template_path, context).load()
