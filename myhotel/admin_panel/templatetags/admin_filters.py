from django import template

register = template.Library()

@register.filter
def user_initial(user):
    """
    Get the first letter of user's first name or username as fallback
    Safely handles empty strings and None values
    """
    try:
        if hasattr(user, 'first_name') and user.first_name and len(str(user.first_name).strip()) > 0:
            return str(user.first_name).strip()[0].upper()
        elif hasattr(user, 'username') and user.username and len(str(user.username).strip()) > 0:
            return str(user.username).strip()[0].upper()
        else:
            return 'U'  # Default fallback
    except (AttributeError, IndexError, TypeError):
        return 'U'  # Safe fallback for any error

@register.filter
def safe_first_char(value):
    """
    Safely get the first character of a string
    Returns 'U' if the value is empty, None, or invalid
    """
    try:
        if value and len(str(value).strip()) > 0:
            return str(value).strip()[0].upper()
        return 'U'
    except (AttributeError, IndexError, TypeError):
        return 'U'

@register.filter
def safe_username_initial(user):
    """
    Alternative filter specifically for username initials
    """
    try:
        if hasattr(user, 'username') and user.username:
            username = str(user.username).strip()
            if len(username) > 0:
                return username[0].upper()
        return 'U'
    except (AttributeError, IndexError, TypeError):
        return 'U'