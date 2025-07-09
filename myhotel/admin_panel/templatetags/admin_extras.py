from django import template

register = template.Library()

@register.filter
def user_initial(user):
    """
    Get the first letter of user's first name or username as fallback
    Safely handles empty strings
    """
    if user.first_name and len(user.first_name) > 0:
        return user.first_name[0].upper()
    elif user.username and len(user.username) > 0:
        return user.username[0].upper()
    else:
        return 'U'  # Default fallback

@register.filter
def safe_first_char(value):
    """
    Safely get the first character of a string
    Returns empty string if the value is empty or None
    """
    if value and len(str(value)) > 0:
        return str(value)[0].upper()
    return ''