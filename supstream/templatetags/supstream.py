from django import template

from ..core import get_url_for_static_file

register = template.Library()

@register.simple_tag
def statix(filename=None):
    return get_url_for_static_file(filename)
