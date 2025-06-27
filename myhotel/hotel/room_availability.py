from django.utils.dateparse import parse_date
from .models import RoomType, Room
from decimal import Decimal

class RoomAvailabilityChecker:
    def __init__(self):
        self.errors = []
        self.form_data = {}

    def check_availability(self, checkin_str, checkout_str, room_type_id, requested_rooms, guest):
        self.errors = []
        self.form_data= {
            'checkin': checkin_str,
            'checkout': checkout_str,
            'room': requested_rooms,
            'room_type': room_type_id,
            'guest': guest,
        }

        # Validate dates
        if not checkin_str or not checkout_str:
            self.errors.append("Please provide both check-in and check-out dates.")
            return {'errors': self.errors, 'form_data': self.form_data}

        checkin = parse_date(checkin_str)
        checkout = parse_date(checkout_str)
        if not checkin or not checkout:
            self.errors.append("Invalid date format.")
            return {'errors': self.errors, 'form_data': self.form_data}
        if checkin >= checkout:
            self.errors.append("Check-in must be before check-out.")
            return {'errors': self.errors, 'form_data': self.form_data}

        # Validate room type
        if not room_type_id:
            self.errors.append("Please select a room type.")
            return {'errors': self.errors, 'form_data': self.form_data}

        try:
            room_type = RoomType.objects.get(id=room_type_id)
            requested_rooms = int(requested_rooms)
            expected_guests = room_type.capacity * requested_rooms

            # Validate guest count
            if int(guest) != expected_guests:
                self.errors.append("Guest count does not match room type capacity and number of rooms.")
                return {'errors': self.errors, 'form_data': self.form_data}

            # Find available rooms
            available_rooms = Room.objects.filter(
                room_type=room_type,
                is_available=True
            ).exclude(
                booking__checkin__lt=checkout,
                booking__checkout__gt=checkin,
                booking__status='confirmed'
            )

            available_count = available_rooms.count()

            if available_count >= requested_rooms:
                # Calculate price details
                base_price = room_type.base_price
                number_of_nights = (checkout - checkin).days
                total_cost = base_price * number_of_nights * requested_rooms
                availability_message = "Room available"
                return {
                    'availability_message': availability_message,
                    'base_price': str(base_price),  # Convert to string for JSON
                    'total_cost': str(total_cost),
                    'number_of_nights': number_of_nights,
                    'form_data': self.form_data
                }
            else:
                availability_message = "No Room available"
                return {
                    'availability_message': availability_message,
                    'form_data': self.form_data
                }

        except RoomType.DoesNotExist:
            self.errors.append("Selected room type does not exist.")
            return {'errors': self.errors, 'form_data': self.form_data}