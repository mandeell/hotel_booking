from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from hotel.models import RoomAmenity
from hotel.forms import RoomAmenityForm
from ..permission_decorators import PermissionMixin

class AdminRoomAmenityListView(PermissionMixin, ListView):
    model = RoomAmenity
    template_name = 'admin_panel/room_amenities.html'
    context_object_name = 'amenities'
    required_section = 'room_amenities'
    model_permission_type = 'view'
    redirect_url = 'admin_panel:dashboard'

class AdminRoomAmenityCreateView(PermissionMixin, CreateView):
    model = RoomAmenity
    form_class = RoomAmenityForm
    template_name = 'admin_panel/add_room_amenity.html'
    success_url = reverse_lazy('admin_room_amenities')
    required_section = 'room_amenities'
    model_permission_type = 'add'
    redirect_url = 'admin_panel:dashboard'

class AdminRoomAmenityEditView(PermissionMixin, UpdateView):
    model = RoomAmenity
    form_class = RoomAmenityForm
    template_name = 'admin_panel/edit_room_amenity.html'
    success_url = reverse_lazy('admin_room_amenities')
    context_object_name = 'amenity'
    required_section = 'room_amenities'
    model_permission_type = 'edit'
    redirect_url = 'admin_panel:dashboard'

class AdminRoomAmenityDeleteView(PermissionMixin, DeleteView):
    model = RoomAmenity
    template_name = 'admin_panel/delete_room_amenity.html'
    success_url = reverse_lazy('admin_room_amenities')
    context_object_name = 'amenity'
    required_section = 'room_amenities'
    model_permission_type = 'delete'
    redirect_url = 'admin_panel:dashboard'
