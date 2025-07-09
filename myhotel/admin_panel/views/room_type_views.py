from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from hotel.models import RoomType
from hotel.forms import RoomTypeForm

class AdminRoomTypeListView(ListView):
    model = RoomType
    template_name = 'admin_panel/room_types.html'
    context_object_name = 'room_types'

class AdminRoomTypeCreateView(CreateView):
    model = RoomType
    form_class = RoomTypeForm
    template_name = 'admin_panel/add_room_type.html'
    success_url = reverse_lazy('admin_room_types')

class AdminRoomTypeEditView(UpdateView):
    model = RoomType
    form_class = RoomTypeForm
    template_name = 'admin_panel/edit_room_type.html'
    success_url = reverse_lazy('admin_room_types')
    context_object_name = 'room_type'

class AdminRoomTypeDeleteView(DeleteView):
    model = RoomType
    template_name = 'admin_panel/delete_room_type.html'
    success_url = reverse_lazy('admin_room_types')
    context_object_name = 'room_type'
