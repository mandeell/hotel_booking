from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Q
from ..models import Booking, Guest, Room
from ..forms import BookingForm
from datetime import datetime, date, timedelta

# List all bookings
def admin_bookings(request):
    bookings = Booking.objects.select_related('room').all()
    
    # Apply filters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            bookings = bookings.filter(checkin__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            bookings = bookings.filter(checkout__lte=date_to)
        except ValueError:
            pass
    
    if status:
        bookings = bookings.filter(status=status)
    
    if search:
        # Search in guest names and room numbers
        bookings = bookings.filter(
            Q(room__room_number__icontains=search) |
            Q(room__room_type__name__icontains=search)
        )
        # Also search in guest names
        guest_bookings = Guest.objects.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        ).values_list('booking_id', flat=True)
        bookings = bookings.filter(Q(id__in=guest_bookings) | Q(room__room_number__icontains=search))
    
    bookings = bookings.order_by('-created_at')
    
    # Get stats for the filtered bookings
    total_bookings = bookings.count()
    confirmed_count = bookings.filter(status='confirmed').count()
    pending_count = bookings.filter(status='pending').count()
    cancelled_count = bookings.filter(status='cancelled').count()
    
    context = {
        'bookings': bookings,
        'total_bookings': total_bookings,
        'confirmed_count': confirmed_count,
        'pending_count': pending_count,
        'cancelled_count': cancelled_count,
    }
    
    return render(request, 'admin/bookings.html', context)

# View a single booking
def admin_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    guests = Guest.objects.filter(booking=booking)
    return render(request, 'admin/booking_view.html', {'booking': booking, 'guests': guests})

# Edit a booking
def admin_booking_edit(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Calculate original number of days paid for
    original_days = (booking.checkout - booking.checkin).days
    
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
            
            # Validate that new booking duration doesn't exceed paid days
            new_days = (checkout - checkin).days
            if new_days > original_days:
                messages.error(request, f'Cannot extend booking beyond {original_days} days already paid for. New booking duration is {new_days} days.')
                return redirect(reverse('admin_booking_edit', args=[booking_id]))
                
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
        return redirect(reverse('admin_bookings'))
    
    context = {
        'booking': booking,
        'available_rooms': available_rooms,
        'original_days': original_days,
    }
    
    return render(request, 'admin/booking_edit.html', context)

# Delete a booking
@require_POST
def admin_booking_delete(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    messages.success(request, 'Booking deleted successfully.')
    return redirect(reverse('admin_bookings'))

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
        checkin_date = datetime.strptime(checkin, '%Y-%m-%d').date()
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d').date()
        
        if checkin_date >= checkout_date:
            return JsonResponse({'available': False, 'error': 'Check-out must be after check-in.'})
        
        # If editing a booking, check the days limit
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                original_days = (booking.checkout - booking.checkin).days
                new_days = (checkout_date - checkin_date).days
                
                if new_days > original_days:
                    return JsonResponse({
                        'available': False, 
                        'error': f'Cannot extend booking beyond {original_days} days already paid for. Selected duration is {new_days} days.'
                    })
            except Booking.DoesNotExist:
                pass
        
        available = is_room_available(room, checkin_date, checkout_date, exclude_booking_id=booking_id)
        
        if available:
            return JsonResponse({'available': True})
        else:
            return JsonResponse({'available': False, 'error': 'Room is not available for the selected dates.'})
        
    except Room.DoesNotExist:
        return JsonResponse({'available': False, 'error': 'Room not found.'})
    except ValueError:
        return JsonResponse({'available': False, 'error': 'Invalid date format.'})
    except Exception as e:
        return JsonResponse({'available': False, 'error': str(e)})