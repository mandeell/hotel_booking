from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from ..models import Permission, Role, UserRole, Hotel, Room, RoomType, RoomAmenity, HotelAmenity, Booking, Guest, ContactForm
from django.contrib.auth.models import User


@login_required
def admin_permissions(request):
    """List all permissions with search and filtering"""
    search_query = request.GET.get('search', '')
    content_type_filter = request.GET.get('content_type', '')
    permission_type_filter = request.GET.get('permission_type', '')
    
    permissions = Permission.objects.select_related('content_type').all()
    
    if search_query:
        permissions = permissions.filter(
            Q(name__icontains=search_query) |
            Q(codename__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if content_type_filter:
        permissions = permissions.filter(content_type_id=content_type_filter)
    
    if permission_type_filter:
        permissions = permissions.filter(permission_type=permission_type_filter)
    
    # Pagination
    paginator = Paginator(permissions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get content types for filter dropdown
    content_types = ContentType.objects.filter(
        model__in=['hotel', 'room', 'roomtype', 'roomamenity', 'hotelamenity', 'booking', 'guest', 'contactform']
    ).order_by('model')
    
    context = {
        'permissions': page_obj,
        'search_query': search_query,
        'content_types': content_types,
        'content_type_filter': content_type_filter,
        'permission_type_filter': permission_type_filter,
        'permission_types': Permission.PERMISSION_TYPES,
        'page_title': 'Permission Manager',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin/permissions.html', context)


@login_required
def admin_permission_create(request):
    """Create a new permission"""
    if request.method == 'POST':
        name = request.POST.get('name')
        codename = request.POST.get('codename')
        content_type_id = request.POST.get('content_type')
        permission_type = request.POST.get('permission_type')
        description = request.POST.get('description', '')
        
        try:
            content_type = ContentType.objects.get(id=content_type_id)
            
            # Check if permission already exists
            if Permission.objects.filter(content_type=content_type, permission_type=permission_type).exists():
                messages.error(request, f'Permission "{permission_type}" for "{content_type.model}" already exists.')
                return redirect('admin_permissions')
            
            permission = Permission.objects.create(
                name=name,
                codename=codename,
                content_type=content_type,
                permission_type=permission_type,
                description=description
            )
            
            messages.success(request, f'Permission "{permission.name}" created successfully.')
            return redirect('admin_permissions')
            
        except Exception as e:
            messages.error(request, f'Error creating permission: {str(e)}')
    
    # Get content types for dropdown
    content_types = ContentType.objects.filter(
        model__in=['hotel', 'room', 'roomtype', 'roomamenity', 'hotelamenity', 'booking', 'guest', 'contactform']
    ).order_by('model')
    
    context = {
        'content_types': content_types,
        'permission_types': Permission.PERMISSION_TYPES,
        'page_title': 'Create Permission',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin/permission_create.html', context)


@login_required
def admin_permission_edit(request, permission_id):
    """Edit an existing permission"""
    permission = get_object_or_404(Permission, id=permission_id)
    
    if request.method == 'POST':
        permission.name = request.POST.get('name')
        permission.codename = request.POST.get('codename')
        permission.description = request.POST.get('description', '')
        
        try:
            permission.save()
            messages.success(request, f'Permission "{permission.name}" updated successfully.')
            return redirect('admin_permissions')
        except Exception as e:
            messages.error(request, f'Error updating permission: {str(e)}')
    
    context = {
        'permission': permission,
        'page_title': 'Edit Permission',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin/permission_edit.html', context)


@login_required
def admin_permission_delete(request, permission_id):
    """Delete a permission"""
    permission = get_object_or_404(Permission, id=permission_id)
    
    if request.method == 'POST':
        permission_name = permission.name
        permission.delete()
        messages.success(request, f'Permission "{permission_name}" deleted successfully.')
        return redirect('admin_permissions')
    
    context = {
        'permission': permission,
        'page_title': 'Delete Permission',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin/permission_delete.html', context)


@login_required
def admin_roles(request):
    """List all roles with search and filtering"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    roles = Role.objects.prefetch_related('permissions').all()
    
    if search_query:
        roles = roles.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if status_filter:
        is_active = status_filter == 'active'
        roles = roles.filter(is_active=is_active)
    
    # Pagination
    paginator = Paginator(roles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'roles': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'page_title': 'Role Manager',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin/roles.html', context)


@login_required
def admin_role_create(request):
    """Create a new role"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        permission_ids = request.POST.getlist('permissions')
        
        try:
            role = Role.objects.create(
                name=name,
                description=description,
                is_active=is_active
            )
            
            # Add permissions to role
            if permission_ids:
                permissions = Permission.objects.filter(id__in=permission_ids)
                role.permissions.set(permissions)
            
            messages.success(request, f'Role "{role.name}" created successfully.')
            return redirect('admin_roles')
            
        except Exception as e:
            messages.error(request, f'Error creating role: {str(e)}')
    
    # Get all permissions grouped by content type
    permissions = Permission.objects.select_related('content_type').order_by('content_type__model', 'permission_type')
    
    context = {
        'permissions': permissions,
        'page_title': 'Create Role',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin/role_create.html', context)


@login_required
def admin_role_edit(request, role_id):
    """Edit an existing role"""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        role.name = request.POST.get('name')
        role.description = request.POST.get('description', '')
        role.is_active = request.POST.get('is_active') == 'on'
        permission_ids = request.POST.getlist('permissions')
        
        try:
            role.save()
            
            # Update permissions
            if permission_ids:
                permissions = Permission.objects.filter(id__in=permission_ids)
                role.permissions.set(permissions)
            else:
                role.permissions.clear()
            
            messages.success(request, f'Role "{role.name}" updated successfully.')
            return redirect('admin_roles')
        except Exception as e:
            messages.error(request, f'Error updating role: {str(e)}')
    
    # Get all permissions grouped by content type
    permissions = Permission.objects.select_related('content_type').order_by('content_type__model', 'permission_type')
    role_permission_ids = list(role.permissions.values_list('id', flat=True))
    
    context = {
        'role': role,
        'permissions': permissions,
        'role_permission_ids': role_permission_ids,
        'page_title': 'Edit Role',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin/role_edit.html', context)


@login_required
def admin_role_delete(request, role_id):
    """Delete a role"""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        role_name = role.name
        role.delete()
        messages.success(request, f'Role "{role_name}" deleted successfully.')
        return redirect('admin_roles')
    
    context = {
        'role': role,
        'page_title': 'Delete Role',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin/role_delete.html', context)


@login_required
def admin_role_view(request, role_id):
    """View role details"""
    role = get_object_or_404(Role, id=role_id)
    
    # Get users with this role
    user_roles = UserRole.objects.filter(role=role).select_related('user', 'assigned_by')
    
    context = {
        'role': role,
        'user_roles': user_roles,
        'page_title': f'Role: {role.name}',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin/role_view.html', context)


@login_required
def admin_user_roles(request):
    """Manage user role assignments"""
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    
    user_roles = UserRole.objects.select_related('user', 'role', 'assigned_by').all()
    
    if search_query:
        user_roles = user_roles.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    if role_filter:
        user_roles = user_roles.filter(role_id=role_filter)
    
    # Pagination
    paginator = Paginator(user_roles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all roles for filter dropdown
    roles = Role.objects.filter(is_active=True).order_by('name')
    
    context = {
        'user_roles': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'roles': roles,
        'page_title': 'User Role Assignments',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin/user_roles.html', context)


@login_required
def admin_user_role_assign(request):
    """Assign role to user"""
    if request.method == 'POST':
        user_id = request.POST.get('user')
        role_id = request.POST.get('role')
        
        try:
            user = User.objects.get(id=user_id)
            role = Role.objects.get(id=role_id)
            
            # Check if assignment already exists
            if UserRole.objects.filter(user=user, role=role).exists():
                messages.error(request, f'User "{user.username}" already has role "{role.name}".')
                return redirect('admin_user_roles')
            
            UserRole.objects.create(
                user=user,
                role=role,
                assigned_by=request.user
            )
            
            messages.success(request, f'Role "{role.name}" assigned to user "{user.username}" successfully.')
            return redirect('admin_user_roles')
            
        except Exception as e:
            messages.error(request, f'Error assigning role: {str(e)}')
    
    # Get all users and active roles
    users = User.objects.filter(is_active=True).order_by('username')
    roles = Role.objects.filter(is_active=True).order_by('name')
    
    context = {
        'users': users,
        'roles': roles,
        'page_title': 'Assign Role to User',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin/user_role_assign.html', context)


@login_required
def admin_user_role_remove(request, user_role_id):
    """Remove role from user"""
    user_role = get_object_or_404(UserRole, id=user_role_id)
    
    if request.method == 'POST':
        user_name = user_role.user.username
        role_name = user_role.role.name
        user_role.delete()
        messages.success(request, f'Role "{role_name}" removed from user "{user_name}" successfully.')
        return redirect('admin_user_roles')
    
    context = {
        'user_role': user_role,
        'page_title': 'Remove User Role',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin/user_role_remove.html', context)


@login_required
@require_http_methods(["POST"])
def create_default_permissions(request):
    """Create default permissions for all models"""
    try:
        models = [
            ('hotel', Hotel),
            ('room', Room),
            ('roomtype', RoomType),
            ('roomamenity', RoomAmenity),
            ('hotelamenity', HotelAmenity),
            ('booking', Booking),
            ('guest', Guest),
            ('contactform', ContactForm),
        ]
        
        created_count = 0
        
        for model_name, model_class in models:
            content_type = ContentType.objects.get_for_model(model_class)
            
            for perm_type, perm_display in Permission.PERMISSION_TYPES:
                permission, created = Permission.objects.get_or_create(
                    content_type=content_type,
                    permission_type=perm_type,
                    defaults={
                        'name': f'Can {perm_display.lower()} {model_name}',
                        'codename': f'{perm_type}_{model_name}',
                        'description': f'Permission to {perm_display.lower()} {model_name} records'
                    }
                )
                if created:
                    created_count += 1
        
        if created_count > 0:
            messages.success(request, f'Created {created_count} default permissions successfully.')
        else:
            messages.info(request, 'All default permissions already exist.')
            
    except Exception as e:
        messages.error(request, f'Error creating default permissions: {str(e)}')
    
    return redirect('admin_permissions')