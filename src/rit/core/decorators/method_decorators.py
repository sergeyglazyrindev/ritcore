from functools import wraps


def cached_property(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if hasattr(self, '__result'):
            return getattr(self, '__result')
        setattr(self, '__result', func(self, *args, **kwargs))
        return getattr(self, '__result')
    return property(wrapper)
