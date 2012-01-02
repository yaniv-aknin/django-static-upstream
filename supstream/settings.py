import os

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from .utils import automagical_release_id, AutomagicalReleaseIDError


STATIC_URL=getattr(settings, 'STATIC_URL', None)
if not STATIC_URL:
    raise ImproperlyConfigured("django-static-upstream requires a non-empty STATIC_URL in settings")

STATIC_ROOT=getattr(settings, 'STATIC_ROOT', None)
if not STATIC_ROOT or not os.path.isdir(STATIC_ROOT):
    raise ImproperlyConfigured("django-static-upstream requires you to point STATIC_ROOT at "
                               "the location of your statics")

try:
    RELEASE_ID=getattr(settings, 'RELEASE_ID', automagical_release_id(STATIC_ROOT))
except AutomagicalReleaseIDError, error:
    # if you caught this, you should either provide a RELEASE_ID setting in your settings.py, as the docs say
    # OR file a bug report, because the automagical_release_id() mechanism is Supposed To Always Work (tm)
    raise ImproperlyConfigured("django-static-upstream failed getting you an automatic release id: %s" % (error,))
