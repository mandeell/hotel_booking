from django.urls import path
from django.contrib.auth.decorators import login_required
from .views.booking_views import (
    admin_bookings,
    admin_booking_view,
    admin_booking_edit,
    admin_booking_delete,
    api_check_room_availability,
)
from .views.dashboard import DashboardView
from .views.hotel_views import (
    hotel_detail_view,
    hotel_detail_edit_view,
    hotel_create_view,
    hotel_list_view,
    hotel_delete_view,
)

from .views.room_views import AdminRoomListView, AdminRoomCreateView, AdminRoomDeleteView, AdminRoomEditView
from .views.guest_views import AdminGuestListView, AdminGuestCreateView, AdminGuestDeleteView, AdminGuestEditView
from .views.room_amenity_views import AdminRoomAmenityListView, AdminRoomAmenityCreateView, AdminRoomAmenityDeleteView, \
    AdminRoomAmenityEditView
from .views.hotel_amenity_views import AdminHotelAmenityListView, AdminHotelAmenityCreateView, AdminHotelAmenityDeleteView, \
    AdminHotelAmenityEditView
from .views.room_type_views import AdminRoomTypeListView, AdminRoomTypeCreateView, AdminRoomTypeDeleteView, \
    AdminRoomTypeEditView
from .views.permission_views import (
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
from .views.soft_delete_views import (
    soft_delete_booking,
    soft_delete_room,
    soft_delete_room_type,
    soft_delete_room_amenity,
    soft_delete_hotel_amenity,
    soft_delete_guest,
    soft_delete_hotel,
)
from .views.user_manager_views import (
    user_manager_list,
    user_manager_create,
    user_manager_detail,
    user_manager_edit,
    user_manager_delete,
    user_manager_toggle_status,
    user_manager_assign_role,
    user_manager_remove_role,
    user_manager_search_ajax,
    user_manager_stats,
    user_manager_reset_password,
    user_manager_generate_password,
)
from .views.auth_views import (
    admin_login,
    admin_logout,
    admin_profile,
    admin_change_password,
)
from .views.admin_redirect import admin_redirect

app_name = 'admin_panel'

urlpatterns = [
    # Authentication
    path('login/', admin_login, name='login'),
    path('logout/', admin_logout, name='logout'),
    path('profile/', admin_profile, name='profile'),
    path('change-password/', admin_change_password, name='change_password'),
    
    # Dashboard
    path('', admin_redirect, name='admin_redirect'),
    path('dashboard/', login_required(DashboardView.as_view()), name='dashboard'),

    # Bookings
    path('bookings/', admin_bookings, name='admin_bookings'),
    path('bookings/<int:booking_id>/', admin_booking_view, name='admin_booking_view'),
    path('bookings/<int:booking_id>/edit/', admin_booking_edit, name='admin_booking_edit'),
    path('bookings/<int:booking_id>/delete/', admin_booking_delete, name='admin_booking_delete'),
    path('api/check-room-availability/', api_check_room_availability, name='api_check_room_availability'),
    
    # Hotel Management
    path('hotels/', hotel_list_view, name='hotel_list'),
    path('hotels/add/', hotel_create_view, name='hotel_create'),
    path('hotels/<int:hotel_id>/', hotel_detail_view, name='hotel_detail'),
    path('hotels/<int:hotel_id>/edit/', hotel_detail_edit_view, name='hotel_edit'),
    path('hotels/<int:hotel_id>/delete/', hotel_delete_view, name='hotel_delete'),
    
    # Legacy URL for backward compatibility
    path('hotel/<int:hotel_id>/', hotel_detail_edit_view, name='hotel_detail_legacy'),

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

    # User Manager
    path('users/', user_manager_list, name='user_manager_list'),
    path('users/create/', user_manager_create, name='user_manager_create'),
    path('users/<int:user_id>/', user_manager_detail, name='user_manager_detail'),
    path('users/<int:user_id>/edit/', user_manager_edit, name='user_manager_edit'),
    path('users/<int:user_id>/delete/', user_manager_delete, name='user_manager_delete'),
    path('users/<int:user_id>/toggle-status/', user_manager_toggle_status, name='user_manager_toggle_status'),
    path('users/<int:user_id>/assign-role/', user_manager_assign_role, name='user_manager_assign_role'),
    path('users/<int:user_id>/remove-role/<int:role_id>/', user_manager_remove_role, name='user_manager_remove_role'),
    path('users/<int:user_id>/reset-password/', user_manager_reset_password, name='user_manager_reset_password'),
    path('users/<int:user_id>/generate-password/', user_manager_generate_password, name='user_manager_generate_password'),
    path('users/search/', user_manager_search_ajax, name='user_manager_search_ajax'),
    path('users/stats/', user_manager_stats, name='user_manager_stats'),

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

    # Soft Delete URLs
    path('bookings/<int:booking_id>/soft-delete/', soft_delete_booking, name='soft_delete_booking'),
    path('rooms/<int:room_id>/soft-delete/', soft_delete_room, name='soft_delete_room'),
    path('room-types/<int:room_type_id>/soft-delete/', soft_delete_room_type, name='soft_delete_room_type'),
    path('room-amenities/<int:room_amenity_id>/soft-delete/', soft_delete_room_amenity, name='soft_delete_room_amenity'),
    path('hotel-amenities/<int:hotel_amenity_id>/soft-delete/', soft_delete_hotel_amenity, name='soft_delete_hotel_amenity'),
    path('guests/<int:guest_id>/soft-delete/', soft_delete_guest, name='soft_delete_guest'),
    path('hotels/<int:hotel_id>/soft-delete/', soft_delete_hotel, name='soft_delete_hotel'),
]