from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    description = models.TextField(blank=True)
    hotel_logo = models.ImageField(upload_to='hotel/', blank=True, null=True)

    def __str__(self):
        return self.name

class HotelAmenity(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon_name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

class RoomAmenity(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name

class RoomType(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=20, decimal_places=2)
    display_price = models.CharField(max_length=300, null=True, blank=True)
    capacity = models.PositiveIntegerField()
    amenities = models.ManyToManyField(RoomAmenity)
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)

    def clean(self):
        # Skip validation for unsaved instances
        if self.pk is None:
            return
        
        # Only validate amenities for saved instances
        if not self.amenities.exists():
            raise ValidationError('A room type must have at least one amenity')

    def __str__(self):
        return self.name

class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True)
    room_number = models.CharField(max_length=10, unique=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.room_type} - {self.room_number}'

class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    checkin = models.DateField()
    checkout = models.DateField()
    guests = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    special_request = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=[('pending', 'Pending'),
                                                      ('confirmed', 'Confirmed'),
                                                      ('cancelled', 'Cancelled')],
                              default='pending')

    def clean(self):
        # Ensure check-in is before check-out
        if self.checkin >= self.checkout:
            raise ValidationError("Check-in must be before check-out.")
        # Check guest count against room capacity
        if self.guests > self.room.room_type.capacity:
            raise ValidationError(
                f"Number of guests ({self.guests}) exceeds the maximum capacity "
                f"({self.room.room_type.capacity}) for this room type.")
        if self.guests <= 0:
            raise ValidationError("Number of guests must be at least 1.")
        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            room=self.room,
            checkin__lt=self.checkout,
            checkout__gt=self.checkin,
            status='confirmed'
        ).exclude(id=self.id)
        if overlapping_bookings.exists():
            raise ValidationError("The room is not available for the selected dates.")

    def save(self, *args, **kwargs):
        # Calculate total price based on number of nights
        number_of_nights = (self.checkout.date() - self.checkin.date()).days
        if number_of_nights < 1:
            raise ValidationError("Checkout must be at least one day after checkin.")
        self.total_price = self.room.room_type.base_price * number_of_nights
        # Run validation before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking for {self.room} - {self.checkin} to {self.checkout}"

class Guest(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class ContactForm(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=400)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.subject}'
