from django import forms
from .models import Booking

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
