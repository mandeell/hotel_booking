from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from ..models import Room, Booking
from ..forms import RoomForm

class AdminRoomListView(ListView):
    model = Room
    template_name = 'admin/rooms.html'
    context_object_name = 'rooms'
    
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
