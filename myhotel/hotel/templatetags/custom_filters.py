from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Replaces all instances of the first argument with the second argument in the given value.
    Usage: {{ value|replace:"old,new" }}
    """
    if ',' not in arg:
        return value
    
    old, new = arg.split(',', 1)
    # For Font Awesome icons, we need to handle special cases
    if old.strip() == ' ' and new.strip() == '-':
        # Replace all spaces with hyphens for Font Awesome icon names
        return value.replace(' ', '-')
    return value.replace(old, new)

@register.filter
def add_class(field, css_class):
    """
    Adds CSS classes to form fields.
    Usage: {{ field|add_class:"form-control" }}
    """
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={'class': css_class})
    return field