from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Booking, Guest, Room
from .forms import BookingForm
from datetime import datetime

# List all bookings
def admin_bookings(request):
    bookings = Booking.objects.select_related('room').all().order_by('-created_at')
    return render(request, 'custom_admin/bookings.html', {'bookings': bookings})

# View a single booking
def admin_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    guests = Guest.objects.filter(booking=booking)
    return render(request, 'custom_admin/booking_view.html', {'booking': booking, 'guests': guests})

# Edit a booking
def admin_booking_edit(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    # Only show available rooms of the same type for the selected dates
    checkin = booking.checkin
    checkout = booking.checkout
    # Validate and parse dates from POST or fallback to booking's dates
    if request.method == 'POST':
        checkin_str = request.POST.get('checkin')
        checkout_str = request.POST.get('checkout')
        try:
            checkin = datetime.strptime(checkin_str, '%Y-%m-%d').date()
            checkout = datetime.strptime(checkout_str, '%Y-%m-%d').date()
        except Exception:
            checkin = booking.checkin
            checkout = booking.checkout
    # Get all rooms of the same type
    all_rooms = Room.objects.filter(room_type=booking.room.room_type)
    # Exclude rooms with overlapping bookings (except this booking)
    available_rooms = []
    for room in all_rooms:
        if checkin and checkout and checkin < checkout:
            overlapping = Booking.objects.filter(
                room=room,
                checkin__lt=checkout,
                checkout__gt=checkin,
            ).exclude(id=booking.id)
            if not overlapping.exists():
                available_rooms.append(room)
        else:
            # If dates are invalid, show all rooms of the type
            available_rooms.append(room)
    if request.method == 'POST':
        room_id = request.POST.get('room')
        booking.room = get_object_or_404(Room, id=room_id)
        booking.checkin = checkin
        booking.checkout = checkout
        booking.save()
        messages.success(request, 'Booking updated successfully.')
        return redirect(reverse('custom_admin_bookings'))
    return render(request, 'custom_admin/booking_edit.html', {
        'booking': booking,
        'available_rooms': available_rooms,
    })

# Delete a booking
@require_POST
def admin_booking_delete(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    messages.success(request, 'Booking deleted successfully.')
    return redirect(reverse('custom_admin_bookings'))

# AJAX endpoint for room availability
from django.views.decorators.csrf import csrf_exempt

def is_room_available(room, checkin, checkout, exclude_booking_id=None):
    overlapping = Booking.objects.filter(
        room=room,
        checkin__lt=checkout,
        checkout__gt=checkin,
    )
    if exclude_booking_id:
        overlapping = overlapping.exclude(id=exclude_booking_id)
    return not overlapping.exists()

@csrf_exempt
def api_check_room_availability(request):
    room_id = request.GET.get('room_id')
    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')
    booking_id = request.GET.get('booking_id')  # Optional, for edit
    if not (room_id and checkin and checkout):
        return JsonResponse({'available': False, 'error': 'Missing parameters.'})
    try:
        room = Room.objects.get(id=room_id)
        checkin = datetime.strptime(checkin, '%Y-%m-%d').date()
        checkout = datetime.strptime(checkout, '%Y-%m-%d').date()
        if checkin >= checkout:
            return JsonResponse({'available': False, 'error': 'Check-out must be after check-in.'})
        available = is_room_available(room, checkin, checkout, exclude_booking_id=booking_id)
        return JsonResponse({'available': available})
    except Exception as e:
        return JsonResponse({'available': False, 'error': str(e)})
