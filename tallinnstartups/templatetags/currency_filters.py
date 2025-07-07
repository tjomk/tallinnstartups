from django import template

register = template.Library()

@register.filter
def format_eur_range(value):
    """
    Format a salary range string like '2035-11930' to '€2035 - €11930'
    """
    if not value or '-' not in value:
        return value
    
    try:
        min_val, max_val = value.split('-', 1)
        return f"€{min_val} - €{max_val}"
    except ValueError:
        return value