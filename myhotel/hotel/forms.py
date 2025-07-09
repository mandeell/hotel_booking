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
    
    def clean_email(self):
        """Validate email and check for duplicates"""
        email = self.cleaned_data.get('email')
        if email:
            # Check if guest with this email already exists (excluding current instance if editing)
            existing_guest = Guest.objects.filter(email=email)
            if self.instance.pk:
                existing_guest = existing_guest.exclude(pk=self.instance.pk)
            
            if existing_guest.exists():
                raise forms.ValidationError(
                    f"A guest with email '{email}' already exists. "
                    "Please use a different email or update the existing guest record."
                )
        return email
    
    def clean_phone(self):
        """Validate phone and check for duplicates"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Check if guest with this phone already exists (excluding current instance if editing)
            existing_guest = Guest.objects.filter(phone=phone)
            if self.instance.pk:
                existing_guest = existing_guest.exclude(pk=self.instance.pk)
            
            if existing_guest.exists():
                raise forms.ValidationError(
                    f"A guest with phone number '{phone}' already exists. "
                    "Please use a different phone number or update the existing guest record."
                )
        return phone

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