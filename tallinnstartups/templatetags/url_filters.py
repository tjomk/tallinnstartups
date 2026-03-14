from django import template
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

register = template.Library()


@register.filter
def add_utm(url):
    """Append utm_source=estonianstartupjobs to an external URL."""
    if not url:
        return url
    parsed = urlparse(url)
    if not parsed.scheme:
        return url
    params = parse_qs(parsed.query, keep_blank_values=True)
    params['utm_source'] = ['estonianstartupjobs']
    new_query = urlencode(params, doseq=True)
    return urlunparse(parsed._replace(query=new_query))
