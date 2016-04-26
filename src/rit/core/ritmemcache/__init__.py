import memcache

from rit.app.conf import settings

mc = memcache.Client(settings.MEMCACHE_SERVERS, debug=0)
