from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from hotel.models import HotelAmenity
from hotel.forms import HotelAmenityForm
from ..permission_decorators import PermissionMixin

class AdminHotelAmenityListView(PermissionMixin, ListView):
    model = HotelAmenity
    template_name = 'admin_panel/hotel_amenities.html'
    context_object_name = 'amenities'
    required_section = 'hotel_amenities'
    model_permission_type = 'view'
    redirect_url = 'admin_panel:dashboard'

class AdminHotelAmenityCreateView(PermissionMixin, CreateView):
    model = HotelAmenity
    form_class = HotelAmenityForm
    template_name = 'admin_panel/add_hotel_amenity.html'
    success_url = reverse_lazy('admin_hotel_amenities')
    required_section = 'hotel_amenities'
    model_permission_type = 'add'
    redirect_url = 'admin_panel:dashboard'

class AdminHotelAmenityEditView(PermissionMixin, UpdateView):
    model = HotelAmenity
    form_class = HotelAmenityForm
    template_name = 'admin_panel/edit_hotel_amenity.html'
    success_url = reverse_lazy('admin_hotel_amenities')
    context_object_name = 'amenity'
    required_section = 'hotel_amenities'
    model_permission_type = 'edit'
    redirect_url = 'admin_panel:dashboard'

class AdminHotelAmenityDeleteView(PermissionMixin, DeleteView):
    model = HotelAmenity
    template_name = 'admin_panel/delete_hotel_amenity.html'
    success_url = reverse_lazy('admin_hotel_amenities')
    context_object_name = 'amenity'
    required_section = 'hotel_amenities'
    model_permission_type = 'delete'
    redirect_url = 'admin_panel:dashboard'
