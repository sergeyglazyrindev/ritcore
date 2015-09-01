BLOCK_HANDLERS = {}


def register(block_name):
    def wrapper(func):
        BLOCK_HANDLERS[block_name] = func
        return func
    return wrapper


@register('foo')
def test(env, element):
    env.output.write_to_header(
        'Tag: {}. Attrib: {}'.format(element.tag, element.attrib)
    )


def render_block(env, element):
    try:
        BLOCK_HANDLERS[element.tag.lower()](env, element)
    except KeyError:
        pass
