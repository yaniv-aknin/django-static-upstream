"""
Views and functions for serving static files; copied from
django.views.static and then modified to my heart's desire.
These CAN be used in a production setting, chillax.
"""

import mimetypes, os, posixpath, re, urllib

from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.template import loader, Template, Context, TemplateDoesNotExist
from django.utils.http import http_date, parse_http_date
from django.utils.cache import patch_response_headers

from . import settings
from .utils import file_digest

def serve(request, path, document_root=None, show_indexes=False, cache_timeout=60*60*24*14, digest=None):
    """
    Serve static files below a given point in the directory structure.

    To use, put a URL pattern such as::

        (r'^(?P<path>.*)$', 'supstream.views.serve', {'document_root' : '/path/to/my/files/'})

    in your URLconf. You must provide the ``document_root`` param. You may
    also set ``show_indexes`` to ``True`` if you'd like to serve a basic index
    of the directory.  This index view will use the template hardcoded below,
    but if you'd like to override it, you can create a template called
    ``static/directory_index.html``.
    """
    path = posixpath.normpath(urllib.unquote(path))
    path = path.lstrip('/')
    newpath = ''
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')
    if newpath and path != newpath:
        return HttpResponseRedirect(newpath)
    fullpath = os.path.join(document_root, newpath)
    if os.path.isdir(fullpath):
        if show_indexes:
            return directory_index(newpath, fullpath)
        raise Http404("Directory indexes are not allowed here.")
    if not os.path.exists(fullpath):
        raise Http404('"%s" does not exist' % fullpath)
    # Respect the If-Modified-Since header.
    statobj = os.stat(fullpath)
    mimetype, encoding = mimetypes.guess_type(fullpath)
    mimetype = mimetype or 'application/octet-stream'
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj.st_mtime, statobj.st_size):
        return HttpResponseNotModified(mimetype=mimetype)
    digest, contents = file_digest(fullpath, return_contents=True)
    etag = '"%s"' % (digest,)
    if request.META.get('HTTP_IF_NONE_MATCH', '') == etag:
        return HttpResponseNotModified(mimetype=mimetype)
    response = HttpResponse(contents, mimetype=mimetype)
    response["Last-Modified"] = http_date(statobj.st_mtime)
    response["Content-Length"] = statobj.st_size
    response["ETag"] = etag
    patch_response_headers(response, cache_timeout = cache_timeout)
    if encoding:
        response["Content-Encoding"] = encoding
    for pattern, mangler in settings.SUPSTREAM_HEADER_MANGLERS.iteritems():
        if pattern.match(request.get_full_path()):
            for header_name, header_value in mangler(request, response):
                response[header_name] = header_value
    return response


DEFAULT_DIRECTORY_INDEX_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
    <meta http-equiv="Content-Language" content="en-us" />
    <meta name="robots" content="NONE,NOARCHIVE" />
    <title>Index of {{ directory }}</title>
  </head>
  <body>
    <h1>Index of {{ directory }}</h1>
    <ul>
      {% ifnotequal directory "/" %}
      <li><a href="../">../</a></li>
      {% endifnotequal %}
      {% for f in file_list %}
      <li><a href="{{ f|urlencode }}">{{ f }}</a></li>
      {% endfor %}
    </ul>
  </body>
</html>
"""

def directory_index(path, fullpath):
    try:
        t = loader.select_template(['static/directory_index.html',
                'static/directory_index'])
    except TemplateDoesNotExist:
        t = Template(DEFAULT_DIRECTORY_INDEX_TEMPLATE, name='Default directory index template')
    files = []
    for f in os.listdir(fullpath):
        if not f.startswith('.'):
            if os.path.isdir(os.path.join(fullpath, f)):
                f += '/'
            files.append(f)
    c = Context({
        'directory' : path + '/',
        'file_list' : files,
    })
    return HttpResponse(t.render(c))

def was_modified_since(header=None, mtime=0, size=0):
    """
    Was something modified since the user last downloaded it?

    header
      This is the value of the If-Modified-Since header.  If this is None,
      I'll just return True.

    mtime
      This is the modification time of the item we're talking about.

    size
      This is the size of the item we're talking about.
    """
    try:
        if header is None:
            raise ValueError
        matches = re.match(r"^([^;]+)(; length=([0-9]+))?$", header,
                           re.IGNORECASE)
        header_mtime = parse_http_date(matches.group(1))
        header_len = matches.group(3)
        if header_len and int(header_len) != size:
            raise ValueError
        if mtime > header_mtime:
            raise ValueError
    except (AttributeError, ValueError, OverflowError):
        return True
    return False
