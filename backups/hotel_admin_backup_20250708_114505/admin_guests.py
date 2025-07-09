from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from ..models import Guest
from ..forms import GuestForm

class AdminGuestListView(ListView):
    model = Guest
    template_name = 'admin/guests.html'
    context_object_name = 'guests'

class AdminGuestCreateView(CreateView):
    model = Guest
    form_class = GuestForm
    template_name = 'admin/add_guest.html'
    success_url = reverse_lazy('admin_guests')

class AdminGuestEditView(UpdateView):
    model = Guest
    form_class = GuestForm
    template_name = 'admin/edit_guest.html'
    success_url = reverse_lazy('admin_guests')
    context_object_name = 'guest'

class AdminGuestDeleteView(DeleteView):
    model = Guest
    template_name = 'admin/delete_guest.html'
    success_url = reverse_lazy('admin_guests')
    context_object_name = 'guest'
