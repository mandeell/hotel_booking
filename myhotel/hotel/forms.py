from django import forms
from .models import Room, Guest, RoomAmenity, HotelAmenity, RoomType, Booking

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['hotel', 'room_type', 'room_number', 'is_available']

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['first_name', 'last_name', 'email', 'phone']

class RoomAmenityForm(forms.ModelForm):
    class Meta:
        model = RoomAmenity
        fields = ['name', 'description', 'icon_name']

class HotelAmenityForm(forms.ModelForm):
    class Meta:
        model = HotelAmenity
        fields = ['name', 'description', 'icon_name']

class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = ['name', 'description', 'base_price', 'display_price', 'capacity', 'amenities', 'image']

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'room',
            'checkin',
            'checkout',
            'guests',
            'total_price',
            'special_request',
            'status',
        ]
        widgets = {
            'checkin': forms.DateInput(attrs={'type': 'date'}),
            'checkout': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')]),
        }