from functools import wraps


def cached_property(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if hasattr(wrapper, '__result'):
            return getattr(wrapper, '__result')
        setattr(wrapper, '__result', func(*args, **kwargs))
        return getattr(wrapper, '__result')
    return property(wrapper)
