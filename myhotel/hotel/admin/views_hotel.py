from django.shortcuts import render, get_object_or_404, redirect
from hotel.models import Hotel
from django import forms

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'address', 'contact_email', 'contact_phone', 'description', 'hotel_logo']


def hotel_detail_edit_view(request, hotel_id=1):
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            return redirect('hotel_detail', hotel_id=hotel.id)
    else:
        form = HotelForm(instance=hotel)
    return render(request, 'admin/hotel_detail.html', {'hotel': hotel, 'form': form})
