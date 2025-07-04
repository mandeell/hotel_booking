from django.urls import path, include
from . import views, booking
from .booking import submit_booking
from .views import check_availability_ajax, contact_submit

urlpatterns = [
    path('', views.home, name='home'),
    path('check-availability', check_availability_ajax, name='check_availability_ajax'),
    # Reusable admin module
    path('hotel/admin/', include('hotel.admin.admin_urls')),
    path('contact-submit', contact_submit, name='contact_submit'),
    path('submit-booking', submit_booking, name='submit_booking'),
    path('verify-payment', booking.verify_payment, name='verify_payment'),
    path('store-expected-amount', booking.store_expected_amount, name='store_expected_amount'),
    path('webhook', booking.webhook, name='webhook'),
]