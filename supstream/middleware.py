from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed

class VHostMiddleware(object):
    def __init__(self):
        try:
            self.urls = settings.VHOST_URLCONFS
        except AttributeError:
            raise MiddlewareNotUsed()
    def process_request(self, request):
        request.urlconf = settings.ROOT_URLCONF

        if 'HTTP_HOST' not in request.META:
            return None

        for host_prefix, urlconf_import_path in self.urls.iteritems():
            if request.META['HTTP_HOST'].startswith(host_prefix):
                request.urlconf = urlconf_import_path
                break

        return None
