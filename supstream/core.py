import os
from urlparse import urljoin

from django.core.cache import get_cache

from .utils import file_digest
from . import settings

cache = get_cache(settings.CACHE_ALIAS)

def get_url_for_static_file(filename):
    if filename is None:
        return settings.STATIC_URL

    cache_key = 'supstream_static-%s-%s' % (settings.RELEASE_ID, filename)
    digest = cache.get(cache_key)
    if digest is None:
        digest, _ = file_digest(os.path.join(settings.STATIC_ROOT, filename))
        cache.set(cache_key, digest)
    return urljoin(settings.STATIC_URL, '!%s/%s' % (digest, filename))
