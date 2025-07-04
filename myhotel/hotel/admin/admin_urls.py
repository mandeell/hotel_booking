from django.urls import path
from .admin_booking import (
    admin_bookings,
    admin_booking_view,
    admin_booking_edit,
    admin_booking_delete,
    api_check_room_availability,
)
from .dashboard import dashboard_view as custom_admin_dashboard
from .views_hotel import hotel_detail_edit_view

from .admin_rooms import AdminRoomListView, AdminRoomCreateView, AdminRoomDeleteView, AdminRoomEditView
from .admin_guests import AdminGuestListView, AdminGuestCreateView, AdminGuestDeleteView, AdminGuestEditView
from .admin_room_amenities import AdminRoomAmenityListView, AdminRoomAmenityCreateView, AdminRoomAmenityDeleteView, \
    AdminRoomAmenityEditView
from .admin_hotel_amenities import AdminHotelAmenityListView, AdminHotelAmenityCreateView, AdminHotelAmenityDeleteView, \
    AdminHotelAmenityEditView
from .admin_room_types import AdminRoomTypeListView, AdminRoomTypeCreateView, AdminRoomTypeDeleteView, \
    AdminRoomTypeEditView

urlpatterns = [
    # Bookings (existing)
    path('bookings/', admin_bookings, name='admin_bookings'),
    path('bookings/<int:booking_id>/', admin_booking_view, name='admin_booking_view'),
    path('bookings/<int:booking_id>/edit/', admin_booking_edit, name='admin_booking_edit'),
    path('bookings/<int:booking_id>/delete/', admin_booking_delete, name='admin_booking_delete'),
    path('api/check-room-availability/', api_check_room_availability, name='api_check_room_availability'),
    path('hotel/<int:hotel_id>/', hotel_detail_edit_view, name='hotel_detail'),
    path('', custom_admin_dashboard, name='dashboard'),
    path('dashboard/', custom_admin_dashboard, name='dashboard'),

    # Rooms
    path('rooms/', AdminRoomListView.as_view(), name='admin_rooms'),
    path('rooms/add/', AdminRoomCreateView.as_view(), name='admin_add_room'),
    path('rooms/<int:pk>/edit/', AdminRoomEditView.as_view(), name='admin_edit_room'),
    path('rooms/<int:pk>/delete/', AdminRoomDeleteView.as_view(), name='admin_delete_room'),

    # Guests
    path('guests/', AdminGuestListView.as_view(), name='admin_guests'),
    path('guests/add/', AdminGuestCreateView.as_view(), name='admin_add_guest'),
    path('guests/<int:pk>/edit/', AdminGuestEditView.as_view(), name='admin_edit_guest'),
    path('guests/<int:pk>/delete/', AdminGuestDeleteView.as_view(), name='admin_delete_guest'),

    # Room Amenities
    path('room-amenities/', AdminRoomAmenityListView.as_view(), name='admin_room_amenities'),
    path('room-amenities/add/', AdminRoomAmenityCreateView.as_view(), name='admin_add_room_amenity'),
    path('room-amenities/<int:pk>/edit/', AdminRoomAmenityEditView.as_view(), name='admin_edit_room_amenity'),
    path('room-amenities/<int:pk>/delete/', AdminRoomAmenityDeleteView.as_view(), name='admin_delete_room_amenity'),

    # Hotel Amenities
    path('hotel-amenities/', AdminHotelAmenityListView.as_view(), name='admin_hotel_amenities'),
    path('hotel-amenities/add/', AdminHotelAmenityCreateView.as_view(), name='admin_add_hotel_amenity'),
    path('hotel-amenities/<int:pk>/edit/', AdminHotelAmenityEditView.as_view(), name='admin_edit_hotel_amenity'),
    path('hotel-amenities/<int:pk>/delete/', AdminHotelAmenityDeleteView.as_view(), name='admin_delete_hotel_amenity'),

    # Room Types
    path('room-types/', AdminRoomTypeListView.as_view(), name='admin_room_types'),
    path('room-types/add/', AdminRoomTypeCreateView.as_view(), name='admin_add_room_type'),
    path('room-types/<int:pk>/edit/', AdminRoomTypeEditView.as_view(), name='admin_edit_room_type'),
    path('room-types/<int:pk>/delete/', AdminRoomTypeDeleteView.as_view(), name='admin_delete_room_type'),
]
