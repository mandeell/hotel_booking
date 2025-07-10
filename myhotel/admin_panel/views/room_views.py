from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from hotel.models import Room, Booking
from hotel.forms import RoomForm
from ..permission_decorators import PermissionMixin

class AdminRoomListView(PermissionMixin, ListView):
    model = Room
    template_name = 'admin_panel/rooms.html'
    context_object_name = 'rooms'
    required_section = 'room_setup'
    model_permission_type = 'view'
    redirect_url = 'admin_panel:dashboard'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Add current booking status for each room
        rooms_with_status = []
        for room in context['rooms']:
            # Check if room has any active bookings (confirmed or pending)
            current_booking = Booking.objects.filter(
                room=room,
                checkin__lte=today,
                checkout__gt=today,
                status__in=['confirmed', 'pending']
            ).first()
            
            # Check for upcoming bookings in the next 7 days
            upcoming_booking = Booking.objects.filter(
                room=room,
                checkin__gt=today,
                checkin__lte=today + timedelta(days=7),
                status__in=['confirmed', 'pending']
            ).order_by('checkin').first()
            
            room_data = {
                'room': room,
                'is_currently_occupied': current_booking is not None,
                'current_booking': current_booking,
                'upcoming_booking': upcoming_booking,
                'actual_availability': room.is_available and current_booking is None
            }
            rooms_with_status.append(room_data)
        
        context['rooms_with_status'] = rooms_with_status
        context['today'] = today
        return context

class AdminRoomCreateView(PermissionMixin, CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'admin_panel/add_room.html'
    success_url = reverse_lazy('admin_panel:admin_rooms')
    required_section = 'room_setup'
    model_permission_type = 'add'
    redirect_url = 'admin_panel:dashboard'

class AdminRoomEditView(PermissionMixin, UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'admin_panel/edit_room.html'
    success_url = reverse_lazy('admin_panel:admin_rooms')
    context_object_name = 'room'
    required_section = 'room_setup'
    model_permission_type = 'edit'
    redirect_url = 'admin_panel:dashboard'

class AdminRoomDeleteView(PermissionMixin, DeleteView):
    model = Room
    template_name = 'admin_panel/delete_room.html'
    success_url = reverse_lazy('admin_panel:admin_rooms')
    context_object_name = 'room'
    required_section = 'room_setup'
    model_permission_type = 'delete'
    redirect_url = 'admin_panel:dashboard'