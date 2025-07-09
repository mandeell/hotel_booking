from django import template
from django.contrib.contenttypes.models import ContentType
from ..permission_decorators import has_permission, has_section_access, has_model_permission, get_user_accessible_sections

register = template.Library()


@register.filter
def has_perm(user, permission_codename):
    """
    Template filter to check if user has a specific permission
    Usage: {% if user|has_perm:"view_booking" %}
    """
    return has_permission(user, permission_codename)


@register.filter
def has_model_perm(user, model_and_action):
    """
    Template filter to check if user has permission for a model action
    Usage: {% if user|has_model_perm:"booking.view" %}
    """
    try:
        model_name, action = model_and_action.split('.')
        permission_codename = f"{action}_{model_name}"
        return has_permission(user, permission_codename)
    except (ValueError, AttributeError):
        return False


@register.filter
def has_section_access_filter(user, section):
    """
    Template filter to check if user has access to a section
    Usage: {% if user|has_section_access_filter:"booking" %}
    """
    return has_section_access(user, section)


@register.filter
def can_access_model(user, model_and_action):
    """
    Template filter to check if user can access a model with specific action
    Usage: {% if user|can_access_model:"booking.view" %}
    """
    try:
        model_name, action = model_and_action.split('.')
        return has_model_permission(user, model_name, action)
    except (ValueError, AttributeError):
        return False


@register.simple_tag
def user_can(user, action, model_name):
    """
    Template tag to check if user can perform an action on a model
    Usage: {% user_can user "view" "booking" as can_view_booking %}
    """
    permission_codename = f"{action}_{model_name}"
    return has_permission(user, permission_codename)


@register.simple_tag
def user_can_access_section(user, section):
    """
    Template tag to check if user can access a section
    Usage: {% user_can_access_section user "booking" as can_access_booking %}
    """
    return has_section_access(user, section)


@register.simple_tag
def get_accessible_sections(user):
    """
    Get list of sections the user has access to
    Usage: {% get_accessible_sections user as accessible_sections %}
    """
    return get_user_accessible_sections(user)


@register.inclusion_tag('admin_panel/partials/permission_check.html')
def show_if_permitted(user, permission_codename, content=''):
    """
    Inclusion tag to conditionally show content based on permission
    Usage: {% show_if_permitted user "view_booking" "View Bookings" %}
    """
    return {
        'show': has_permission(user, permission_codename),
        'content': content
    }


@register.inclusion_tag('admin_panel/partials/section_check.html')
def show_if_section_access(user, section, content=''):
    """
    Inclusion tag to conditionally show content based on section access
    Usage: {% show_if_section_access user "booking" "Booking Section" %}
    """
    return {
        'show': has_section_access(user, section),
        'content': content
    }


@register.simple_tag
def get_user_role_display(user):
    """
    Get display name for user's role(s)
    """
    if user.is_superuser:
        return "Administrator"
    
    from hotel.models import UserRole
    user_roles = UserRole.objects.filter(user=user, role__is_active=True).select_related('role')
    
    if not user_roles.exists():
        return "No Role Assigned"
    
    role_names = [ur.role.name for ur in user_roles]
    return ", ".join(role_names)