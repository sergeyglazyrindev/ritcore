from lxml import etree
from .loader import XmlLoader


def parse_dynamic_content_xml(template_path, context):
    return etree.tostring(
        XmlLoader(template_path, context).load()
    )
