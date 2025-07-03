from django.urls import path
from . import views, booking
from .booking import submit_booking
from .views import check_availability_ajax, home, contact_submit
from .admin_booking import (
    admin_bookings,
    admin_booking_view,
    admin_booking_edit,
    admin_booking_delete,
    api_check_room_availability,
)
from .dashboard import dashboard_view
from .custom_admin import admin_site as custom_admin_site
from .views_hotel import hotel_detail_edit_view

urlpatterns = [
    path('', views.home, name='home'),
    path('check-availability', check_availability_ajax, name='check_availability_ajax'),
    # Custom admin bookings management (under /hotel/admin/)
    path('hotel/admin/bookings/', admin_bookings, name='custom_admin_bookings'),
    path('hotel/admin/bookings/<int:booking_id>/', admin_booking_view, name='custom_admin_booking_view'),
    path('hotel/admin/bookings/<int:booking_id>/edit/', admin_booking_edit, name='custom_admin_booking_edit'),
    path('hotel/admin/bookings/<int:booking_id>/delete/', admin_booking_delete, name='custom_admin_booking_delete'),
    path('api/check-room-availability/', api_check_room_availability, name='api_check_room_availability'),
    path('contact-submit', contact_submit, name='contact_submit'),
    path('submit-booking', submit_booking, name='submit_booking'),
    path('verify-payment', booking.verify_payment, name='verify_payment'),
    path('store-expected-amount', booking.store_expected_amount, name='store_expected_amount'),
    path('webhook', booking.webhook, name='webhook'),
    path('hotel/admin/hotel/<int:hotel_id>/', hotel_detail_edit_view, name='hotel_detail'),
    path('hotel/admin/', dashboard_view, name='dashboard'),
    path('hotel/admin/dashboard/', dashboard_view, name='dashboard'),
]