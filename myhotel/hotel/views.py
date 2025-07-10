from django.shortcuts import render
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .contact_form import ContactFormHandler
from .models import RoomType, Hotel, HotelAmenity, Room, Booking
from .room_availability import RoomAvailabilityChecker
import logging

logger = logging.getLogger(__name__)

def home(request):
    room_types = RoomType.objects.all()
    hotel = Hotel.objects.first()
    hotel_amenities = HotelAmenity.objects.all()
    context = {
        'room_types': room_types,
        'hotel': hotel,
        'hotel_amenities': hotel_amenities,
    }

    if request.method == 'POST' and 'form1_submit' in request.POST:
        checkin_str = request.POST.get('checkin')
        checkout_str = request.POST.get('checkout')
        requested_rooms = request.POST.get('rooms')  # Changed from 'room' to 'rooms'
        room_type_id = request.POST.get('room_type')
        guest = request.POST.get('guest')

        checker = RoomAvailabilityChecker()
        result = checker.check_availability(checkin_str, checkout_str, room_type_id, requested_rooms, guest)
        context.update(result)
    return render(request, 'hotel/home.html', context)

@require_http_methods(["POST"])
def check_availability_ajax(request):
    """
    AJAX endpoint for checking room availability.
    Handles both hero section form and booking modal requests.
    """
    try:
        logger.info(f"Availability check request: {dict(request.POST)}")
        
        checkin_str = request.POST.get('checkin')
        checkout_str = request.POST.get('checkout')
        # Handle both 'rooms' and 'modalRooms' parameter names
        requested_rooms = request.POST.get('rooms') or request.POST.get('modalRooms')
        room_type_id = request.POST.get('room_type') or request.POST.get('roomType')
        # Handle both 'guest' and 'modalGuests' parameter names
        guest = request.POST.get('guest') or request.POST.get('modalGuests')

        logger.info(f"Parsed parameters: checkin={checkin_str}, checkout={checkout_str}, "
                   f"rooms={requested_rooms}, room_type={room_type_id}, guests={guest}")

        checker = RoomAvailabilityChecker()
        result = checker.check_availability(checkin_str, checkout_str, room_type_id, requested_rooms, guest)

        logger.info(f"Availability check result: {result}")

        return JsonResponse({
            'availability_message': result.get('availability_message', ''),
            'base_price': result.get('base_price', ''),
            'total_cost': result.get('total_cost', ''),
            'number_of_nights': result.get('number_of_nights', 0),
            'errors': result.get('errors', []),
            'form_data': result.get('form_data', {}),
            'success': 'errors' not in result or len(result.get('errors', [])) == 0
        })

    except Exception as e:
        logger.error(f"Error in check_availability_ajax: {str(e)}", exc_info=True)
        return JsonResponse({
            'errors': [f'Server error: {str(e)}'],
            'success': False
        }, status=500)


def contact_submit(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        handler = ContactFormHandler()
        result = handler.process(name, email, subject, message)
        return JsonResponse(result)
    return JsonResponse({'errors': ['Invalid request method']}, status=400)