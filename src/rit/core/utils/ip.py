def get_ip_address_from_forwarded_for(hxff):
    if not hxff:
        return ''
    l = hxff.split(', ')
    try:
        return l[0]
    except (IndexError, AttributeError):
        return ''


def get_ip_address_from_request_forwarded_for(request):
    hxff = request.environ.get('HTTP_X_FORWARDED_FOR', '')
    if not hxff:
        return request.environ.get('REMOTE_ADDR')
    return get_ip_address_from_forwarded_for(hxff)
