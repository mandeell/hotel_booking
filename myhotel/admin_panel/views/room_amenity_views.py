from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from hotel.models import RoomAmenity
from hotel.forms import RoomAmenityForm

class AdminRoomAmenityListView(ListView):
    model = RoomAmenity
    template_name = 'admin_panel/room_amenities.html'
    context_object_name = 'amenities'

class AdminRoomAmenityCreateView(CreateView):
    model = RoomAmenity
    form_class = RoomAmenityForm
    template_name = 'admin_panel/add_room_amenity.html'
    success_url = reverse_lazy('admin_room_amenities')

class AdminRoomAmenityEditView(UpdateView):
    model = RoomAmenity
    form_class = RoomAmenityForm
    template_name = 'admin_panel/edit_room_amenity.html'
    success_url = reverse_lazy('admin_room_amenities')
    context_object_name = 'amenity'

class AdminRoomAmenityDeleteView(DeleteView):
    model = RoomAmenity
    template_name = 'admin_panel/delete_room_amenity.html'
    success_url = reverse_lazy('admin_room_amenities')
    context_object_name = 'amenity'
