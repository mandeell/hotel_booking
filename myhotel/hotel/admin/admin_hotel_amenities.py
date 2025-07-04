from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from ..models import HotelAmenity
from ..forms import HotelAmenityForm

class AdminHotelAmenityListView(ListView):
    model = HotelAmenity
    template_name = 'admin/hotel_amenities.html'
    context_object_name = 'amenities'

class AdminHotelAmenityCreateView(CreateView):
    model = HotelAmenity
    form_class = HotelAmenityForm
    template_name = 'admin/add_hotel_amenity.html'
    success_url = reverse_lazy('admin_hotel_amenities')

class AdminHotelAmenityEditView(UpdateView):
    model = HotelAmenity
    form_class = HotelAmenityForm
    template_name = 'admin/edit_hotel_amenity.html'
    success_url = reverse_lazy('admin_hotel_amenities')
    context_object_name = 'amenity'

class AdminHotelAmenityDeleteView(DeleteView):
    model = HotelAmenity
    template_name = 'admin/delete_hotel_amenity.html'
    success_url = reverse_lazy('admin_hotel_amenities')
    context_object_name = 'amenity'
