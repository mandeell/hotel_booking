from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from ..forms import AdminLoginForm


@never_cache
@csrf_protect
def admin_login(request):
    """Admin panel login view"""
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('admin_panel:dashboard')
    
    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    
                    # Redirect to next page or dashboard
                    next_page = request.GET.get('next')
                    if next_page:
                        return redirect(next_page)
                    return redirect('admin_panel:dashboard')
                else:
                    messages.error(request, 'Your account has been deactivated. Please contact an administrator.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AdminLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Admin Login',
        'next': request.GET.get('next', ''),
    }
    
    return render(request, 'admin_panel/auth/login.html', context)


@login_required
def admin_logout(request):
    """Admin panel logout view"""
    user_name = request.user.get_full_name() or request.user.username
    logout(request)
    messages.success(request, f'You have been logged out successfully. Goodbye, {user_name}!')
    return redirect('admin_panel:login')


@login_required
def admin_profile(request):
    """User profile view"""
    from hotel.models import UserRole, UserProfile
    from ..forms import UserProfileForm
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_roles = UserRole.objects.filter(user=request.user).select_related('role', 'assigned_by')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('admin_panel:profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    context = {
        'user': request.user,
        'profile': profile,
        'user_roles': user_roles,
        'form': form,
        'page_title': 'My Profile',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin_panel/auth/profile.html', context)


@login_required
def admin_change_password(request):
    """Change password view for current user"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep user logged in
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('admin_panel:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'page_title': 'Change Password',
        'breadcrumb_parent': 'Account',
    }
    
    return render(request, 'admin_panel/auth/change_password.html', context)