from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from hotel.models import Booking, Room, RoomType, RoomAmenity, HotelAmenity, Guest, Hotel


@login_required
@require_POST
def soft_delete_booking(request, booking_id):
    """Soft delete a booking"""
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Perform soft delete
            booking.soft_delete(user=request.user)
            
            return JsonResponse({
                'success': True,
                'message': f'Booking for {booking.room} has been deleted successfully.'
            })
        else:
            # Fallback for non-AJAX requests
            booking.soft_delete(user=request.user)
            messages.success(request, f'Booking for {booking.room} has been deleted successfully.')
            return redirect('admin_panel:admin_bookings')
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error deleting booking: {str(e)}'
            }, status=400)
        else:
            messages.error(request, f'Error deleting booking: {str(e)}')
            return redirect('admin_panel:admin_bookings')


@login_required
@require_POST
def soft_delete_room(request, room_id):
    """Soft delete a room"""
    try:
        room = get_object_or_404(Room, id=room_id)
        
        # Check if room has active bookings
        active_bookings = Booking.objects.filter(
            room=room,
            status__in=['confirmed', 'pending']
        ).count()
        
        if active_bookings > 0:
            error_msg = f'Cannot delete room {room.room_number}. It has {active_bookings} active booking(s).'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_msg
                }, status=400)
            else:
                messages.error(request, error_msg)
                return redirect('admin_panel:admin_rooms')
        
        # Perform soft delete
        room.soft_delete(user=request.user)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Room {room.room_number} has been deleted successfully.'
            })
        else:
            messages.success(request, f'Room {room.room_number} has been deleted successfully.')
            return redirect('admin_panel:admin_rooms')
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error deleting room: {str(e)}'
            }, status=400)
        else:
            messages.error(request, f'Error deleting room: {str(e)}')
            return redirect('admin_panel:admin_rooms')


@login_required
@require_POST
def soft_delete_room_type(request, room_type_id):
    """Soft delete a room type"""
    try:
        room_type = get_object_or_404(RoomType, id=room_type_id)
        
        # Check if room type has associated rooms
        associated_rooms = Room.objects.filter(room_type=room_type).count()
        
        if associated_rooms > 0:
            error_msg = f'Cannot delete room type "{room_type.name}". It has {associated_rooms} associated room(s).'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_msg
                }, status=400)
            else:
                messages.error(request, error_msg)
                return redirect('admin_panel:admin_room_types')
        
        # Perform soft delete
        room_type.soft_delete(user=request.user)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Room type "{room_type.name}" has been deleted successfully.'
            })
        else:
            messages.success(request, f'Room type "{room_type.name}" has been deleted successfully.')
            return redirect('admin_panel:admin_room_types')
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error deleting room type: {str(e)}'
            }, status=400)
        else:
            messages.error(request, f'Error deleting room type: {str(e)}')
            return redirect('admin_panel:admin_room_types')


@login_required
@require_POST
def soft_delete_room_amenity(request, room_amenity_id):
    """Soft delete a room amenity"""
    try:
        amenity = get_object_or_404(RoomAmenity, id=room_amenity_id)
        
        # Check if amenity is used by any room types
        associated_room_types = RoomType.objects.filter(amenities=amenity).count()
        
        if associated_room_types > 0:
            error_msg = f'Cannot delete amenity "{amenity.name}". It is used by {associated_room_types} room type(s).'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_msg
                }, status=400)
            else:
                messages.error(request, error_msg)
                return redirect('admin_panel:admin_room_amenities')
        
        # Perform soft delete
        amenity.soft_delete(user=request.user)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Room amenity "{amenity.name}" has been deleted successfully.'
            })
        else:
            messages.success(request, f'Room amenity "{amenity.name}" has been deleted successfully.')
            return redirect('admin_panel:admin_room_amenities')
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error deleting room amenity: {str(e)}'
            }, status=400)
        else:
            messages.error(request, f'Error deleting room amenity: {str(e)}')
            return redirect('admin_panel:admin_room_amenities')


@login_required
@require_POST
def soft_delete_hotel_amenity(request, hotel_amenity_id):
    """Soft delete a hotel amenity"""
    try:
        amenity = get_object_or_404(HotelAmenity, id=hotel_amenity_id)
        
        # Perform soft delete
        amenity.soft_delete(user=request.user)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Hotel amenity "{amenity.name}" has been deleted successfully.'
            })
        else:
            messages.success(request, f'Hotel amenity "{amenity.name}" has been deleted successfully.')
            return redirect('admin_panel:admin_hotel_amenities')
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error deleting hotel amenity: {str(e)}'
            }, status=400)
        else:
            messages.error(request, f'Error deleting hotel amenity: {str(e)}')
            return redirect('admin_panel:admin_hotel_amenities')


@login_required
@require_POST
def soft_delete_guest(request, guest_id):
    """Soft delete a guest"""
    try:
        guest = get_object_or_404(Guest, id=guest_id)
        
        # Perform soft delete
        guest.soft_delete(user=request.user)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Guest "{guest.first_name} {guest.last_name}" has been deleted successfully.'
            })
        else:
            messages.success(request, f'Guest "{guest.first_name} {guest.last_name}" has been deleted successfully.')
            return redirect('admin_panel:admin_guests')
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error deleting guest: {str(e)}'
            }, status=400)
        else:
            messages.error(request, f'Error deleting guest: {str(e)}')
            return redirect('admin_panel:admin_guests')


@login_required
@require_POST
def soft_delete_hotel(request, hotel_id):
    """Soft delete a hotel"""
    try:
        hotel = get_object_or_404(Hotel, id=hotel_id)
        
        # Check if hotel has associated rooms
        associated_rooms = Room.objects.filter(hotel=hotel).count()
        
        if associated_rooms > 0:
            error_msg = f'Cannot delete hotel "{hotel.name}". It has {associated_rooms} associated room(s).'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_msg
                }, status=400)
            else:
                messages.error(request, error_msg)
                return redirect('admin_panel:hotel_list')
        
        # Perform soft delete
        hotel.soft_delete(user=request.user)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Hotel "{hotel.name}" has been deleted successfully.'
            })
        else:
            messages.success(request, f'Hotel "{hotel.name}" has been deleted successfully.')
            return redirect('admin_panel:hotel_list')
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error deleting hotel: {str(e)}'
            }, status=400)
        else:
            messages.error(request, f'Error deleting hotel: {str(e)}')
            return redirect('admin_panel:hotel_list')