import collections


def to_list(x, default=None):
    if x is None:
        return default
    if not isinstance(x, collections.Iterable) or \
       isinstance(x, (str, bytes)):
        return [x]
    elif isinstance(x, list):
        return x
    else:
        return list(x)
