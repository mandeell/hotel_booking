import logging
from datetime import datetime
from django.utils import timezone
from .models import RoomType, Booking, Room

logger = logging.getLogger(__name__)

class RoomAvailabilityChecker:
    def __init__(self):
        self.errors = []
        self.form_data = {}

    def check_availability(self, checkin_str, checkout_str, room_type_id, requested_rooms, guest):
        self.form_data = {
            'checkin': checkin_str,
            'checkout': checkout_str,
            'room_type_id': room_type_id,
            'requested_rooms': requested_rooms,
            'guest': guest
        }

        # Validate inputs
        if not all([checkin_str, checkout_str, room_type_id, requested_rooms]):
            self.errors.append("All fields (check-in, check-out, room type, number of rooms) are required.")
            logger.warning(f"Missing required fields: {self.errors}")
            return {'errors': self.errors, 'form_data': self.form_data}

        try:
            checkin = datetime.strptime(checkin_str, '%Y-%m-%d').date()
            checkout = datetime.strptime(checkout_str, '%Y-%m-%d').date()
            if checkin >= checkout:
                self.errors.append("Check-out date must be after check-in date.")
                logger.warning(f"Invalid dates: {self.errors}")
                return {'errors': self.errors, 'form_data': self.form_data}
            if checkin < timezone.now().date():
                self.errors.append("Check-in date cannot be in the past.")
                logger.warning(f"Past check-in date: {self.errors}")
                return {'errors': self.errors, 'form_data': self.form_data}
        except ValueError:
            self.errors.append("Invalid date format. Use YYYY-MM-DD.")
            logger.warning(f"Date format error: {self.errors}")
            return {'errors': self.errors, 'form_data': self.form_data}

        try:
            room_type = RoomType.objects.get(id=room_type_id)
            requested_rooms = int(requested_rooms) if requested_rooms else 0
            if requested_rooms <= 0:
                self.errors.append("Number of rooms must be greater than 0.")
                logger.warning(f"Invalid room count: {self.errors}")
                return {'errors': self.errors, 'form_data': self.form_data}

            # Validate guest count only if provided
            if guest:
                expected_guests = room_type.capacity * requested_rooms
                guest = int(guest) if guest else 0
                if guest != expected_guests:
                    self.errors.append("Guest count does not match room type capacity and number of rooms.")
                    logger.warning(f"Guest count mismatch: {self.errors}")
                    return {'errors': self.errors, 'form_data': self.form_data}

            # Check availability logic
            # Get all rooms of the specified room type
            rooms = Room.objects.filter(
                room_type=room_type,
                is_available=True
            )
            # Count booked rooms for these rooms during the requested period
            booked_rooms = Booking.objects.filter(
                room__in=rooms,
                room__isnull=False,
                checkin__lt=checkout,
                checkout__gt=checkin,
                status__in=['confirmed', 'pending']
            ).count()
            available_rooms = rooms.count() - booked_rooms
            if available_rooms >= requested_rooms:
                number_of_nights = (checkout - checkin).days
                base_price = room_type.base_price
                total_cost = base_price * requested_rooms * number_of_nights
                return {
                    'availability_message': 'Room available',
                    'base_price': f'₦{base_price}',
                    'total_cost': f'₦{total_cost}',
                    'number_of_nights': number_of_nights,
                    'form_data': self.form_data
                }
            else:
                self.errors.append(f"Only {available_rooms} rooms available for the selected type and dates.")
                logger.warning(f"Insufficient rooms: {self.errors}")
                return {'errors': self.errors, 'form_data': self.form_data}
        except RoomType.DoesNotExist:
            self.errors.append("Selected room type does not exist.")
            logger.warning(f"Room type not found: {self.errors}")
            return {'errors': self.errors, 'form_data': self.form_data}
        except ValueError:
            self.errors.append("Invalid number of rooms or guests.")
            logger.warning(f"Invalid number format: {self.errors}")
            return {'errors': self.errors, 'form_data': self.form_data}
        except Exception as e:
            self.errors.append(f"Unexpected error checking availability: {str(e)}")
            logger.error(f"Unexpected error in check_availability: {str(e)}")
            return {'errors': self.errors, 'form_data': self.form_data}