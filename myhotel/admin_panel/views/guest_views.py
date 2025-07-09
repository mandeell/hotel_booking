from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from hotel.models import Guest
from hotel.forms import GuestForm
from ..permission_decorators import PermissionMixin

class AdminGuestListView(PermissionMixin, ListView):
    model = Guest
    template_name = 'admin_panel/guests.html'
    context_object_name = 'guests'
    required_section = 'guest'
    model_permission_type = 'view'
    redirect_url = 'admin_panel:dashboard'

class AdminGuestCreateView(PermissionMixin, CreateView):
    model = Guest
    form_class = GuestForm
    template_name = 'admin_panel/add_guest.html'
    success_url = reverse_lazy('admin_panel:admin_guests')
    required_section = 'guest'
    model_permission_type = 'add'
    redirect_url = 'admin_panel:dashboard'
    
    def form_valid(self, form):
        """Override to handle duplicate guests more gracefully"""
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        
        # Check for existing guest by email first
        existing_guest = Guest.objects.filter(email=email).first()
        
        if existing_guest:
            messages.warning(
                self.request,
                f"A guest with email '{email}' already exists. "
                f"Redirecting to edit the existing guest record."
            )
            return redirect('admin_panel:admin_edit_guest', pk=existing_guest.pk)
        
        # Check for existing guest by phone as secondary check
        existing_guest_by_phone = Guest.objects.filter(phone=phone).first()
        
        if existing_guest_by_phone:
            messages.warning(
                self.request,
                f"A guest with phone number '{phone}' already exists. "
                f"Redirecting to edit the existing guest record."
            )
            return redirect('admin_panel:admin_edit_guest', pk=existing_guest_by_phone.pk)
        
        # No duplicate found, proceed with creation
        messages.success(self.request, "Guest created successfully.")
        return super().form_valid(form)

class AdminGuestEditView(PermissionMixin, UpdateView):
    model = Guest
    form_class = GuestForm
    template_name = 'admin_panel/edit_guest.html'
    success_url = reverse_lazy('admin_panel:admin_guests')
    context_object_name = 'guest'
    required_section = 'guest'
    model_permission_type = 'edit'
    redirect_url = 'admin_panel:dashboard'

class AdminGuestDeleteView(PermissionMixin, DeleteView):
    model = Guest
    template_name = 'admin_panel/delete_guest.html'
    success_url = reverse_lazy('admin_panel:admin_guests')
    context_object_name = 'guest'
    required_section = 'guest'
    model_permission_type = 'delete'
    redirect_url = 'admin_panel:dashboard'