from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from hotel.models import RoomType
from hotel.forms import RoomTypeForm
from ..permission_decorators import PermissionMixin

class AdminRoomTypeListView(PermissionMixin, ListView):
    model = RoomType
    template_name = 'admin_panel/room_types.html'
    context_object_name = 'room_types'
    required_section = 'room_types'
    model_permission_type = 'view'
    redirect_url = 'admin_panel:dashboard'

class AdminRoomTypeCreateView(PermissionMixin, CreateView):
    model = RoomType
    form_class = RoomTypeForm
    template_name = 'admin_panel/add_room_type.html'
    success_url = reverse_lazy('admin_panel:admin_room_types')
    required_section = 'room_types'
    model_permission_type = 'add'
    redirect_url = 'admin_panel:dashboard'

class AdminRoomTypeEditView(PermissionMixin, UpdateView):
    model = RoomType
    form_class = RoomTypeForm
    template_name = 'admin_panel/edit_room_type.html'
    success_url = reverse_lazy('admin_panel:admin_room_types')
    context_object_name = 'room_type'
    required_section = 'room_types'
    model_permission_type = 'edit'
    redirect_url = 'admin_panel:dashboard'

class AdminRoomTypeDeleteView(PermissionMixin, DeleteView):
    model = RoomType
    template_name = 'admin_panel/delete_room_type.html'
    success_url = reverse_lazy('admin_panel:admin_room_types')
    context_object_name = 'room_type'
    required_section = 'room_types'
    model_permission_type = 'delete'
    redirect_url = 'admin_panel:dashboard'
