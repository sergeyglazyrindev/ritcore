from lxml import etree

BLOCK_HANDLERS = {}


def register(block_name):
    def wrapper(func):
        BLOCK_HANDLERS[block_name.lower()] = func
        return func
    return wrapper


@register('foo')
def test(env, element):
    return etree.fromstring('<b></b>')


def render_block(env, element):
    return BLOCK_HANDLERS[element.xpath('local-name()').lower()](env, element)


def element_is_registered(el):
    return el.xpath('local-name()').lower() in BLOCK_HANDLERS
