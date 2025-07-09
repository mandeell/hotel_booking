from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from hotel.models import UserRole, Permission


def require_superuser(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'Only superusers can perform this action.')
            return redirect('admin_panel:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def has_permission(user, permission_codename):
    """
    Check if a user has a specific permission through their roles
    """
    if user.is_superuser:
        return True
    
    # Get all roles assigned to the user
    user_roles = UserRole.objects.filter(user=user, role__is_active=True)
    
    # Get all permission codenames for the user's roles
    permission_codenames = []
    for user_role in user_roles:
        permission_codenames.extend(user_role.role.get_permission_codenames())
    
    return permission_codename in permission_codenames


def has_section_access(user, section):
    """
    Check if user has access to a specific section
    """
    access_permission = f"access_{section}"
    return has_permission(user, access_permission)


def has_model_permission(user, model_name, action):
    """
    Check if user has permission for a specific model action
    """
    permission_codename = f"{action}_{model_name}"
    return has_permission(user, permission_codename)


def require_permission(permission_codename, redirect_url='admin_panel:dashboard'):
    """
    Decorator to require a specific permission for a view
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if has_permission(request.user, permission_codename):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f'You do not have permission to access this page. Required permission: {permission_codename}')
                return redirect(redirect_url)
        return _wrapped_view
    return decorator


def require_section_access(section, redirect_url='admin_panel:dashboard'):
    """
    Decorator to require access to a specific section
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if has_section_access(request.user, section):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f'You do not have access to the {section} section.')
                return redirect(redirect_url)
        return _wrapped_view
    return decorator


def require_model_permission(model_class, permission_type, redirect_url='admin_panel:dashboard'):
    """
    Decorator to require a specific model permission for a view
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            content_type = ContentType.objects.get_for_model(model_class)
            permission_codename = f"{permission_type}_{content_type.model}"
            
            if has_permission(request.user, permission_codename):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f'You do not have permission to {permission_type} {content_type.model} records.')
                return redirect(redirect_url)
        return _wrapped_view
    return decorator


class PermissionMixin:
    """
    Mixin for class-based views to check permissions
    """
    permission_required = None
    model_permission_type = None
    required_section = None
    redirect_url = 'admin_panel:dashboard'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Check section access first
        if self.required_section:
            if not has_section_access(request.user, self.required_section):
                messages.error(request, f'You do not have access to the {self.required_section} section.')
                return redirect(self.redirect_url)
        
        # Check specific permission
        if self.permission_required:
            if not has_permission(request.user, self.permission_required):
                messages.error(request, f'You do not have permission to access this page. Required permission: {self.permission_required}')
                return redirect(self.redirect_url)
        
        # Check model permission
        elif self.model_permission_type and hasattr(self, 'model'):
            content_type = ContentType.objects.get_for_model(self.model)
            permission_codename = f"{self.model_permission_type}_{content_type.model}"
            
            if not has_permission(request.user, permission_codename):
                messages.error(request, f'You do not have permission to {self.model_permission_type} {content_type.model} records.')
                return redirect(self.redirect_url)
        
        return super().dispatch(request, *args, **kwargs)


def get_user_permissions(user):
    """
    Get all permissions for a user
    """
    if user.is_superuser:
        return Permission.objects.all()
    
    user_roles = UserRole.objects.filter(user=user, role__is_active=True)
    permission_ids = []
    
    for user_role in user_roles:
        permission_ids.extend(user_role.role.permissions.values_list('id', flat=True))
    
    return Permission.objects.filter(id__in=permission_ids).distinct()


def get_user_permission_codenames(user):
    """
    Get all permission codenames for a user
    """
    if user.is_superuser:
        return list(Permission.objects.values_list('codename', flat=True))
    
    user_roles = UserRole.objects.filter(user=user, role__is_active=True)
    permission_codenames = []
    
    for user_role in user_roles:
        permission_codenames.extend(user_role.role.get_permission_codenames())
    
    return list(set(permission_codenames))  # Remove duplicates


def get_user_accessible_sections(user):
    """
    Get list of sections the user has access to
    """
    if user.is_superuser:
        return ['booking', 'guest', 'room_setup', 'hotel_setup', 'contact', 'account']
    
    sections = []
    section_list = ['booking', 'guest', 'room_setup', 'hotel_setup', 'contact', 'account']
    
    for section in section_list:
        if has_section_access(user, section):
            sections.append(section)
    
    return sections