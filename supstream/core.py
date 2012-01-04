import os

from django.core.cache import cache

from .utils import file_digest
from . import settings

def get_url_for_static_file(filename):
    if filename is None:
        return settings.STATIC_URL + '/'

    cache_key = 'supstream_static-%s-%s' % (settings.RELEASE_ID, filename)
    digest = cache.get(cache_key)
    if cache.get(cache_key) is None:
        digest, _ = file_digest(os.path.join(settings.STATIC_ROOT, filename))
        cache.set(cache_key, digest)
    return '%s/!%s/%s' % (settings.STATIC_URL, digest, filename)
