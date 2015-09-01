from functools import wraps


def cached_property(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        cached_property_name = 'cachedprop_' + func.__name__ + '__result'
        if hasattr(self, cached_property_name):
            return getattr(self, cached_property_name)
        setattr(self, cached_property_name, func(self, *args, **kwargs))
        return getattr(self, cached_property_name)
    return property(wrapper)
