from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
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
    success_url = reverse_lazy('admin_guests')
    required_section = 'guest'
    model_permission_type = 'add'
    redirect_url = 'admin_panel:dashboard'

class AdminGuestEditView(PermissionMixin, UpdateView):
    model = Guest
    form_class = GuestForm
    template_name = 'admin_panel/edit_guest.html'
    success_url = reverse_lazy('admin_guests')
    context_object_name = 'guest'
    required_section = 'guest'
    model_permission_type = 'edit'
    redirect_url = 'admin_panel:dashboard'

class AdminGuestDeleteView(PermissionMixin, DeleteView):
    model = Guest
    template_name = 'admin_panel/delete_guest.html'
    success_url = reverse_lazy('admin_guests')
    context_object_name = 'guest'
    required_section = 'guest'
    model_permission_type = 'delete'
    redirect_url = 'admin_panel:dashboard'