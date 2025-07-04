from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from ..models import Room
from ..forms import RoomForm

class AdminRoomListView(ListView):
    model = Room
    template_name = 'admin/rooms.html'
    context_object_name = 'rooms'

class AdminRoomCreateView(CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'admin/add_room.html'
    success_url = reverse_lazy('admin_rooms')

class AdminRoomEditView(UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'admin/edit_room.html'
    success_url = reverse_lazy('admin_rooms')
    context_object_name = 'room'

class AdminRoomDeleteView(DeleteView):
    model = Room
    template_name = 'admin/delete_room.html'
    success_url = reverse_lazy('admin_rooms')
    context_object_name = 'room'
