from django.urls import resolve

def breadcrumb_context(request):
    """
    Context processor to add breadcrumb information based on the current URL
    """
    try:
        url_name = resolve(request.path_info).url_name
        
        # Define breadcrumb mappings
        breadcrumb_map = {
            'dashboard': {
                'page_title': 'Overview',
                'breadcrumb_parent': None,
                'breadcrumb_parent_url': None,
            },
            'admin_bookings': {
                'page_title': 'Bookings',
                'breadcrumb_parent': None,
                'breadcrumb_parent_url': None,
            },
            'admin_booking_view': {
                'page_title': 'Booking Details',
                'breadcrumb_parent': 'Bookings',
                'breadcrumb_parent_url': '/admin/bookings/',
            },
            'admin_booking_edit': {
                'page_title': 'Edit Booking',
                'breadcrumb_parent': 'Bookings',
                'breadcrumb_parent_url': '/admin/bookings/',
            },
            'admin_guests': {
                'page_title': 'Guests',
                'breadcrumb_parent': None,
                'breadcrumb_parent_url': None,
            },
            'admin_edit_guest': {
                'page_title': 'Edit Guest',
                'breadcrumb_parent': 'Guests',
                'breadcrumb_parent_url': '/admin/guests/',
            },
            'admin_rooms': {
                'page_title': 'Rooms',
                'breadcrumb_parent': 'Setup',
                'breadcrumb_parent_url': None,
            },
            'admin_edit_room': {
                'page_title': 'Edit Room',
                'breadcrumb_parent': 'Rooms',
                'breadcrumb_parent_url': '/admin/rooms/',
            },
            'admin_room_types': {
                'page_title': 'Room Types',
                'breadcrumb_parent': 'Setup',
                'breadcrumb_parent_url': None,
            },
            'admin_edit_room_type': {
                'page_title': 'Edit Room Type',
                'breadcrumb_parent': 'Room Types',
                'breadcrumb_parent_url': '/admin/room-types/',
            },
            'admin_room_amenities': {
                'page_title': 'Room Amenities',
                'breadcrumb_parent': 'Setup',
                'breadcrumb_parent_url': None,
            },
            'admin_edit_room_amenity': {
                'page_title': 'Edit Room Amenity',
                'breadcrumb_parent': 'Room Amenities',
                'breadcrumb_parent_url': '/admin/room-amenities/',
            },
            'admin_hotel_amenities': {
                'page_title': 'Hotel Amenities',
                'breadcrumb_parent': 'Setup',
                'breadcrumb_parent_url': None,
            },
            'admin_edit_hotel_amenity': {
                'page_title': 'Edit Hotel Amenity',
                'breadcrumb_parent': 'Hotel Amenities',
                'breadcrumb_parent_url': '/admin/hotel-amenities/',
            },
            'hotel_detail': {
                'page_title': 'Hotel Management',
                'breadcrumb_parent': 'Setup',
                'breadcrumb_parent_url': None,
            },
        }
        
        # Get breadcrumb info for current URL
        breadcrumb_info = breadcrumb_map.get(url_name, {
            'page_title': 'Overview',
            'breadcrumb_parent': None,
            'breadcrumb_parent_url': None,
        })
        
        return breadcrumb_info
        
    except:
        return {
            'page_title': 'Overview',
            'breadcrumb_parent': None,
            'breadcrumb_parent_url': None,
        }