from django import template
from django.utils.safestring import mark_safe
import markdown as md

register = template.Library()


@register.filter(name='markdown')
def markdown_format(text):
    """Convert markdown text to HTML with common extensions."""
    if not text:
        return ''

    return mark_safe(md.markdown(
        text,
        extensions=[
            'extra',  # Enables tables, fenced code blocks, and more
            'nl2br',  # Converts newlines to <br> tags
        ]
    ))
