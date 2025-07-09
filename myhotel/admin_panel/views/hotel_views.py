from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from hotel.models import Hotel
from django import forms
from ..permission_decorators import require_section_access, require_model_permission, require_superuser


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'address', 'contact_email', 'contact_phone', 'description', 'hotel_logo']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter hotel name'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter hotel address'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact email'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact phone number'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter hotel description'
            }),
            'hotel_logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

@require_section_access('hotel_setup')
@require_model_permission(Hotel, 'view', redirect_url='admin_panel:dashboard')
def hotel_detail_view(request, hotel_id):
    """View hotel details without editing capability"""
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    return render(request, 'admin_panel/hotel_detail_view.html', {'hotel': hotel})

@require_section_access('hotel_setup')
@require_model_permission(Hotel, 'edit', redirect_url='admin_panel:dashboard')
def hotel_detail_edit_view(request, hotel_id):
    """Edit hotel details"""
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hotel details updated successfully.')
            return redirect('admin_panel:hotel_detail', hotel_id=hotel.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HotelForm(instance=hotel)
    
    return render(request, 'admin_panel/hotel_detail.html', {'hotel': hotel, 'form': form})

@require_section_access('hotel_setup')
@require_superuser
def hotel_create_view(request):
    """Create a new hotel"""
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save()
            messages.success(request, 'Hotel created successfully.')
            return redirect('admin_panel:hotel_detail', hotel_id=hotel.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HotelForm()
    
    return render(request, 'admin_panel/hotel_create.html', {'form': form})

@require_section_access('hotel_setup')
@require_model_permission(Hotel, 'view', redirect_url='admin_panel:dashboard')
def hotel_list_view(request):
    """List all hotels"""
    hotels = Hotel.objects.all().order_by('name')
    return render(request, 'admin_panel/hotel_list.html', {'hotels': hotels})

@require_section_access('hotel_setup')
@require_superuser
def hotel_delete_view(request, hotel_id):
    """Delete a hotel (soft delete)"""
    hotel = get_object_or_404(Hotel, pk=hotel_id)

    if request.method == 'POST':
        hotel_name = hotel.name
        hotel.delete()
        messages.success(request, f'Hotel "{hotel_name}" has been deleted successfully.')
        return redirect('admin_panel:hotel_list')
    
    return render(request, 'admin_panel/hotel_delete.html', {'hotel': hotel})
