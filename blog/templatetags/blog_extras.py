from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='split_keywords')
@stringfilter
def split_keywords(value):
    """Split keywords by comma and return as list"""
    if not value:
        return []
    return [keyword.strip() for keyword in value.split(',') if keyword.strip()]