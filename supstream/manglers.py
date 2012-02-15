import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

def load_manglers(mangler_definitions):
    result = {}
    # lightly adapted from middleware loading at django/core/handlers/base.py
    for pattern_string, mangler_path in mangler_definitions.iteritems():
        try:
            pattern = re.compile(pattern_string)
        except re.error, error:
            raise ImproperlyConfigured("Invalid mangler pattern %s: %s" % (pattern_string, error))

        try:
            ma_module, ma_callable_name = mangler_path.rsplit('.', 1)
        except ValueError:
            raise ImproperlyConfigured('%s isn\'t a mangler' % mangler_path)
        try:
            mod = import_module(ma_module)
        except ImportError, e:
            raise ImproperlyConfigured('Error importing mangler %s: "%s"' % (ma_module, e))
        try:
            ma_callable = getattr(mod, ma_callable_name)
        except AttributeError:
            raise ImproperlyConfigured('Mangler module "%s" does not define a "%s" callable' %
                                       (ma_module, ma_callable_name))
        result[pattern] = ma_callable
    return result

def access_control_allow_origin_for_www(request, response):
    if 'HTTP_HOST' in request.META:
        scheme = 'https' if request.is_secure() else 'http'
        host = request.META['HTTP_HOST']
        host = 'www' + host[host.find('.'):]
        yield 'Access-Control-Allow-Origin', '%s://%s' % (scheme, host)

def access_control_allow_origin_by_http_origin(request, response):
    if not getattr(access_control_allow_origin_for_www, 'patterns', None):
        try:
            access_control_allow_origin_by_http_origin.patterns = \
                map(re.compile, settings.SUPSTREAM_WILDCARD_ACCESS_CONTROL_ALLOW_ORIGIN_BY_HTTP_ORIGIN)
        except re.error:
            raise ImproperlyConfigured("Invalid pattern in "
                                       "SUPSTREAM_WILDCARD_ACCESS_CONTROL_ALLOW_ORIGIN_BY_HTTP_ORIGIN")

    patterns = access_control_allow_origin_by_http_origin.patterns
    if 'HTTP_ORIGIN' in request.META:
        if any(pattern.match(request.META['HTTP_ORIGIN']) for pattern in patterns):
            yield 'Access-Control-Allow-Origin', '*'
