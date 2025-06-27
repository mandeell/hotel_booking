from django.shortcuts import render
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from .contact_form import ContactFormHandler
from .models import RoomType, Hotel, HotelAmenity, Room
from .room_availability import RoomAvailabilityChecker

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
        requested_rooms = request.POST.get('room')
        room_type_id = request.POST.get('room_type')
        guest = request.POST.get('guest')

        checker = RoomAvailabilityChecker()
        result = checker.check_availability(checkin_str, checkout_str, room_type_id, requested_rooms, guest)
        context.update(result)
    return render(request, 'hotel/home.html', context)

def check_availability_ajax(request):
    if request.method == 'POST':
        checkin_str = request.POST.get('checkin')
        checkout_str = request.POST.get('checkout')
        requested_rooms = request.POST.get('room')
        room_type_id = request.POST.get('room_type')
        guest = request.POST.get('guest')

        checker = RoomAvailabilityChecker()
        result = checker.check_availability(checkin_str, checkout_str, room_type_id, requested_rooms, guest)

        # Return JSON response
        return JsonResponse({
            'availability_message': result.get('availability_message', ''),
            'errors': result.get('errors', []),
        })

    return JsonResponse({'errors': ['Invalid request method']}, status=400)

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