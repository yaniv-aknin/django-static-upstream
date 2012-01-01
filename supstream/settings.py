import uuid
import os

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

RELEASE_ID=uuid.uuid4().hex

STATIC_URL=getattr(settings, 'STATIC_URL', None)
if not STATIC_URL:
    raise ImproperlyConfigured("django-static-upstream requires a non-empty STATIC_URL in settings")

STATIC_ROOT=getattr(settings, 'STATIC_ROOT', None)
if not STATIC_ROOT or not os.path.isdir(STATIC_ROOT):
    raise ImproperlyConfigured("django-static-upstream requires you to point STATIC_ROOT at "
                               "the location of your statics")
