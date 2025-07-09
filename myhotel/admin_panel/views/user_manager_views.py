from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib.auth.forms import SetPasswordForm
from django.utils.crypto import get_random_string

from hotel.models import UserRole, Role
from ..forms import AdminUserRegistrationForm, AdminUserEditForm, UserSearchForm
from ..permission_decorators import require_section_access, require_permission, require_model_permission


@login_required
@require_model_permission(User, 'view', redirect_url='admin_panel:user_list')
def user_manager_list(request):
    """List all users with search and filtering"""
    form = UserSearchForm(request.GET)
    users = User.objects.all().order_by('-date_joined')
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        role = form.cleaned_data.get('role')
        status = form.cleaned_data.get('status')
        
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        if role:
            user_ids = UserRole.objects.filter(role=role).values_list('user_id', flat=True)
            users = users.filter(id__in=user_ids)
        
        if status == 'active':
            users = users.filter(is_active=True)
        elif status == 'inactive':
            users = users.filter(is_active=False)
    
    # Add role information to users
    users_with_roles = []
    for user in users:
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        users_with_roles.append({
            'user': user,
            'roles': [ur.role for ur in user_roles],
            'role_count': user_roles.count()
        })
    
    # Pagination
    paginator = Paginator(users_with_roles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'form': form,
        'total_users': users.count(),
        'active_users': users.filter(is_active=True).count(),
        'inactive_users': users.filter(is_active=False).count(),
        'page_title': 'User Manager',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin_panel/user_manager/user_list.html', context)


@login_required
@require_model_permission(User, 'add', redirect_url='admin_panel:dashboard')
def user_manager_create(request):
    """Create a new user"""
    if request.method == 'POST':
        form = AdminUserRegistrationForm(request.POST)
        if form.is_valid():
            form.assigned_by = request.user
            user = form.save()
            messages.success(request, f'User "{user.username}" created successfully.')
            return redirect('admin_panel:user_manager_list')
    else:
        form = AdminUserRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Create User',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin_panel/user_manager/user_create.html', context)


@login_required
@require_model_permission(User, 'view', redirect_url='admin_panel:dashboard')
def user_manager_detail(request, user_id):
    """View user details"""
    user = get_object_or_404(User, id=user_id)
    user_roles = UserRole.objects.filter(user=user).select_related('role', 'assigned_by')
    
    # Get available roles for assignment (roles not already assigned to user)
    assigned_role_ids = user_roles.values_list('role_id', flat=True)
    available_roles = Role.objects.filter(is_active=True).exclude(id__in=assigned_role_ids)
    
    context = {
        'user': user,
        'user_roles': user_roles,
        'available_roles': available_roles,
        'page_title': f'User: {user.username}',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin_panel/user_manager/user_detail.html', context)


@login_required
@require_model_permission(User, 'edit', redirect_url='admin_panel:dashboard')
def user_manager_edit(request, user_id):
    """Edit an existing user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.assigned_by = request.user
            form.save()
            messages.success(request, f'User "{user.username}" updated successfully.')
            return redirect('admin_panel:user_manager_detail', user_id=user.id)
    else:
        form = AdminUserEditForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'page_title': f'Edit User: {user.username}',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin_panel/user_manager/user_edit.html', context)


@login_required
@require_model_permission(User, 'delete', redirect_url='admin_panel:dashboard')
def user_manager_delete(request, user_id):
    """Delete a user"""
    user = get_object_or_404(User, id=user_id)
    
    # Prevent deletion of superusers and self
    if user.is_superuser:
        messages.error(request, 'Cannot delete superuser accounts.')
        return redirect('admin_panel:user_manager_detail', user_id=user.id)
    
    if user == request.user:
        messages.error(request, 'Cannot delete your own account.')
        return redirect('admin_panel:user_manager_detail', user_id=user.id)

    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" deleted successfully.')
        return redirect('admin_panel:user_manager_list')
    
    context = {
        'user': user,
        'page_title': f'Delete User: {user.username}',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin_panel/user_manager/user_delete.html', context)


@require_POST
@login_required
@require_model_permission(User, 'edit', redirect_url='admin_panel:user_list')
def user_manager_toggle_status(request, user_id):
    """Toggle user active status"""
    user = get_object_or_404(User, id=user_id)
    
    # Prevent deactivating superusers and self
    if user.is_superuser:
        messages.error(request, 'Cannot modify superuser status.')
        return redirect('admin_panel:user_manager_detail', user_id=user.id)
    
    if user == request.user:
        messages.error(request, 'Cannot modify your own status.')
        return redirect('admin_panel:user_manager_detail', user_id=user.id)
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User "{user.username}" {status} successfully.')
    
    return redirect('admin_panel:user_manager_detail', user_id=user.id)


@login_required
@require_model_permission(Role, 'edit', redirect_url='admin_panel:user_list')
def user_manager_assign_role(request, user_id):
    """Assign role to user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        role_id = request.POST.get('role')
        if role_id:
            try:
                role = Role.objects.get(id=role_id, is_active=True)
                
                # Check if user already has this role
                if UserRole.objects.filter(user=user, role=role).exists():
                    messages.warning(request, f'User "{user.username}" already has role "{role.name}".')
                else:
                    UserRole.objects.create(
                        user=user,
                        role=role,
                        assigned_by=request.user
                    )
                    messages.success(request, f'Role "{role.name}" assigned to user "{user.username}" successfully.')
                
            except Role.DoesNotExist:
                messages.error(request, 'Invalid role selected.')
        else:
            messages.error(request, 'Please select a role.')
    
    return redirect('admin_panel:user_manager_detail', user_id=user.id)


@require_POST
@login_required
@require_model_permission(Role, 'edit', redirect_url='admin_panel:user_list')
def user_manager_remove_role(request, user_id, role_id):
    """Remove role from user"""
    user = get_object_or_404(User, id=user_id)
    role = get_object_or_404(Role, id=role_id)
    
    try:
        user_role = UserRole.objects.get(user=user, role=role)
        user_role.delete()
        messages.success(request, f'Role "{role.name}" removed from user "{user.username}" successfully.')
    except UserRole.DoesNotExist:
        messages.error(request, 'User does not have this role.')
    
    return redirect('admin_panel:user_manager_detail', user_id=user.id)


# AJAX endpoints
@login_required
def user_manager_search_ajax(request):
    """AJAX endpoint for user search"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'users': []})
    
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    )[:10]
    
    user_data = []
    for user in users:
        user_data.append({
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name() or user.username,
            'email': user.email,
            'is_active': user.is_active
        })
    
    return JsonResponse({'users': user_data})


@login_required
def user_manager_stats(request):
    """Get user statistics"""
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()
    superusers = User.objects.filter(is_superuser=True).count()
    
    # Role distribution
    role_stats = []
    for role in Role.objects.filter(is_active=True):
        user_count = UserRole.objects.filter(role=role).count()
        role_stats.append({
            'role': role.name,
            'user_count': user_count
        })
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'superusers': superusers,
        'role_stats': role_stats,
        'page_title': 'User Statistics',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin_panel/user_manager/user_stats.html', context)


@login_required
def user_manager_reset_password(request, user_id):
    """Reset user password"""
    user = get_object_or_404(User, id=user_id)
    
    # Prevent resetting superuser passwords unless current user is also superuser
    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, 'Cannot reset superuser password.')
        return redirect('admin_panel:user_manager_detail', user_id=user.id)
    
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Password for user "{user.username}" has been reset successfully.')
            return redirect('admin_panel:user_manager_detail', user_id=user.id)
    else:
        form = SetPasswordForm(user)
    
    context = {
        'form': form,
        'user': user,
        'page_title': f'Reset Password: {user.username}',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin_panel/user_manager/user_reset_password.html', context)


@require_POST
@login_required
def user_manager_generate_password(request, user_id):
    """Generate a random password for user"""
    user = get_object_or_404(User, id=user_id)
    
    # Prevent generating passwords for superusers unless current user is also superuser
    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, 'Cannot generate password for superuser.')
        return redirect('admin_panel:user_manager_detail', user_id=user.id)
    
    # Generate random password
    new_password = get_random_string(12)
    user.set_password(new_password)
    user.save()
    
    messages.success(request, f'New password generated for user "{user.username}": {new_password}')
    messages.warning(request, 'Please share this password securely with the user and ask them to change it on first login.')
    
    return redirect('admin_panel:user_manager_detail', user_id=user.id)