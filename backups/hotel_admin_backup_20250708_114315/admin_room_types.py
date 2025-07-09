from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from ..models import RoomType
from ..forms import RoomTypeForm

class AdminRoomTypeListView(ListView):
    model = RoomType
    template_name = 'admin/room_types.html'
    context_object_name = 'room_types'

class AdminRoomTypeCreateView(CreateView):
    model = RoomType
    form_class = RoomTypeForm
    template_name = 'admin/add_room_type.html'
    success_url = reverse_lazy('admin_room_types')

class AdminRoomTypeEditView(UpdateView):
    model = RoomType
    form_class = RoomTypeForm
    template_name = 'admin/edit_room_type.html'
    success_url = reverse_lazy('admin_room_types')
    context_object_name = 'room_type'

class AdminRoomTypeDeleteView(DeleteView):
    model = RoomType
    template_name = 'admin/delete_room_type.html'
    success_url = reverse_lazy('admin_room_types')
    context_object_name = 'room_type'
