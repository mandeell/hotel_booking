from django.urls import path
from .admin_booking import (
    admin_bookings,
    admin_booking_view,
    admin_booking_edit,
    admin_booking_delete,
    api_check_room_availability,
)
from .dashboard import DashboardView
from .views_hotel import hotel_detail_edit_view

from .admin_rooms import AdminRoomListView, AdminRoomCreateView, AdminRoomDeleteView, AdminRoomEditView
from .admin_guests import AdminGuestListView, AdminGuestCreateView, AdminGuestDeleteView, AdminGuestEditView
from .admin_room_amenities import AdminRoomAmenityListView, AdminRoomAmenityCreateView, AdminRoomAmenityDeleteView, \
    AdminRoomAmenityEditView
from .admin_hotel_amenities import AdminHotelAmenityListView, AdminHotelAmenityCreateView, AdminHotelAmenityDeleteView, \
    AdminHotelAmenityEditView
from .admin_room_types import AdminRoomTypeListView, AdminRoomTypeCreateView, AdminRoomTypeDeleteView, \
    AdminRoomTypeEditView
from .admin_permissions import (
    admin_permissions,
    admin_permission_create,
    admin_permission_edit,
    admin_permission_delete,
    admin_roles,
    admin_role_create,
    admin_role_edit,
    admin_role_delete,
    admin_role_view,
    admin_user_roles,
    admin_user_role_assign,
    admin_user_role_remove,
    create_default_permissions,
)

urlpatterns = [
    # Bookings (existing)
    path('bookings/', admin_bookings, name='admin_bookings'),
    path('bookings/<int:booking_id>/', admin_booking_view, name='admin_booking_view'),
    path('bookings/<int:booking_id>/edit/', admin_booking_edit, name='admin_booking_edit'),
    path('bookings/<int:booking_id>/delete/', admin_booking_delete, name='admin_booking_delete'),
    path('api/check-room-availability/', api_check_room_availability, name='api_check_room_availability'),
    path('hotel/<int:hotel_id>/', hotel_detail_edit_view, name='hotel_detail'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

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

    # Permissions
    path('permissions/', admin_permissions, name='admin_permissions'),
    path('permissions/add/', admin_permission_create, name='admin_permission_create'),
    path('permissions/<int:permission_id>/edit/', admin_permission_edit, name='admin_permission_edit'),
    path('permissions/<int:permission_id>/delete/', admin_permission_delete, name='admin_permission_delete'),
    path('permissions/create-defaults/', create_default_permissions, name='create_default_permissions'),

    # Roles
    path('roles/', admin_roles, name='admin_roles'),
    path('roles/add/', admin_role_create, name='admin_role_create'),
    path('roles/<int:role_id>/edit/', admin_role_edit, name='admin_role_edit'),
    path('roles/<int:role_id>/delete/', admin_role_delete, name='admin_role_delete'),
    path('roles/<int:role_id>/view/', admin_role_view, name='admin_role_view'),

    # User Role Assignments
    path('user-roles/', admin_user_roles, name='admin_user_roles'),
    path('user-roles/assign/', admin_user_role_assign, name='admin_user_role_assign'),
    path('user-roles/<int:user_role_id>/remove/', admin_user_role_remove, name='admin_user_role_remove'),
]
