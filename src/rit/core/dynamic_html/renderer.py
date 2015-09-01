import os
from lxml import etree
from collections import defaultdict
from rit.core.decorators import cached_property
from .block_handlers import render_block
from .exceptions import DynamicContentIncludeError


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

    @property
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
        return DynamicContentXmlParser(self.template).parse(self.env)


element_is_xml_include = lambda el: el.tag == 'xmlinclude'


def xml_include(template, element, env):
    base_template_path = os.path.dirname(template)
    new_template_path = os.path.realpath(
        os.path.join(base_template_path, element.attrib['src'])
    )
    if base_template_path not in new_template_path:
        raise DynamicContentIncludeError(
            '{} not placed in folder {}'.format(
                new_template_path,
                base_template_path
            )
        )
    return DynamicContentXmlParser(new_template_path).parse(env)


class DynamicContentXmlParser(object):

    def __init__(self, template, el=None):
        self.template = template
        self.__el = el

    @cached_property
    def el(self):
        if self.__el is not None:
            return self.__el
        with open(self.template) as fp:
            return etree.parse(fp).getroot()

    def parse(self, env):

        el = self.el
        if element_is_xml_include(el):
            return xml_include(self.template, el, env)

        render_block(env, el)

        for _el in el.getchildren():
            DynamicContentXmlParser(self.template, el=_el).parse(env)

        return env.output.context


def parse_dynamic_page_xml(template_path, context={}):
    return DynamicContentXmlLoader(template_path, context).load()
