from django.urls import path
from . import views
from .views import check_availability_ajax, home, contact_submit

urlpatterns = [
    path('', views.home, name='home'),
    path('check-availability', check_availability_ajax, name='check_availability_ajax'),
    path('contact-submit', contact_submit, name='contact_submit'),
]