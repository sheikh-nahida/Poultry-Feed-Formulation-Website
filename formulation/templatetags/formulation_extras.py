from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """Get dictionary value by key safely."""
    return d.get(key, None)

