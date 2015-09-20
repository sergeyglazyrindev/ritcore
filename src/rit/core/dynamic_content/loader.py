from .parsers import XmlParser
from .environment import XmlEnvironment


class XmlLoader(object):

    def __init__(self, template, context):
        self.template = template
        self.env = XmlEnvironment()
        self.env.root_template = template
        self.env.context = context

    def load(self):
        return XmlParser(self.template).parse(self.env)
