from hotel.models import UserRole, Permission


def user_initial_context(request):
    """
    Context processor to add safe user initial to all templates
    """
    def get_user_initial(user):
        try:
            if hasattr(user, 'first_name') and user.first_name and len(str(user.first_name).strip()) > 0:
                return str(user.first_name).strip()[0].upper()
            elif hasattr(user, 'username') and user.username and len(str(user.username).strip()) > 0:
                return str(user.username).strip()[0].upper()
            else:
                return 'U'
        except (AttributeError, IndexError, TypeError):
            return 'U'
    
    return {
        'user_initial': get_user_initial(request.user) if hasattr(request, 'user') else 'U'
    }


def user_permissions_context(request):
    """
    Context processor to add user permissions and roles to all templates
    """
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {
            'user_roles': [],
            'user_permissions': [],
            'user_permission_codenames': [],
            'is_admin_user': False,
            'user_role_names': [],
        }
    
    user = request.user
    
    # Check if user is superuser (Django admin)
    if user.is_superuser:
        return {
            'user_roles': [],
            'user_permissions': Permission.objects.all(),
            'user_permission_codenames': list(Permission.objects.values_list('codename', flat=True)),
            'is_admin_user': True,
            'user_role_names': ['Administrator'],
        }
    
    # Get user roles (custom admin panel roles)
    user_roles = UserRole.objects.filter(user=user, role__is_active=True).select_related('role')
    
    # Get all permissions for the user's roles
    permission_ids = []
    role_names = []
    
    for user_role in user_roles:
        permission_ids.extend(user_role.role.permissions.values_list('id', flat=True))
        role_names.append(user_role.role.name)
    
    user_permissions = Permission.objects.filter(id__in=permission_ids).distinct()
    user_permission_codenames = list(user_permissions.values_list('codename', flat=True))
    
    return {
        'user_roles': user_roles,
        'user_permissions': user_permissions,
        'user_permission_codenames': user_permission_codenames,
        'is_admin_user': False,
        'user_role_names': role_names,
    }
