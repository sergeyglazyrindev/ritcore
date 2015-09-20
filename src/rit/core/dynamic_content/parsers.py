import os
from lxml import etree
from .block_handlers import render_block, element_is_registered
from .exceptions import DynamicContentIncludeError

element_is_xml_include = lambda el: el.xpath('local-name()') == 'xmlinclude'


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
    return XmlParser(new_template_path).parse(env)


def _parse_xml(template, env, el):

    def replace_el_in_xml(_el, replace_to):
        if isinstance(replace_to, etree.ElementBase) and\
           replace_to.xpath('local-name()') != 'root':
            _el.getparent().replace(_el, replace_to)
            return
        el_parent = _el.getparent()
        index = el_parent.index(_el)
        for child_el in replace_to.getchildren():
            el_parent.insert(index, child_el)
            index += 1
        el_parent.remove(_el)

    if element_is_xml_include(el):
        replace_el_in_xml(
            el,
            xml_include(template, el, env)
        )
        return el

    if element_is_registered(el):
        replace_el_in_xml(el, render_block(env, el))
    else:
        for _el in el.getchildren():
            _parse_xml(template, env, _el)

    return el


class XmlParser(object):

    def __init__(self, template):
        self.template = template

    @property
    def el(self):
        with open(self.template) as fp:
            return etree.fromstring(fp.read())

    def parse(self, env):
        return _parse_xml(self.template, env, self.el)
