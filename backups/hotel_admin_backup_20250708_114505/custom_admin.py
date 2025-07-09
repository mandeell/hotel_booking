from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.template.loader import select_template
from myhotel.hotel.models import Booking, Room, Hotel, RoomType, Guest, RoomAmenity, HotelAmenity

class HotelAdminSite(admin.AdminSite):
    site_title = "Hotel Admin Portal"
    index_title = "Welcome to the Hotel Admin"
    index_template = "custom_admin/index.html"
    app_index_template = "custom_admin/index.html"
    login_template = "custom_admin/login.html"
    logout_template = "custom_admin/logout.html"
    password_change_template = "custom_admin/password_change_form.html"
    password_change_done_template = "custom_admin/password_change_done.html"

    @property
    def site_header(self):
        hotel = Hotel.objects.first()
        return hotel.name + " Admin" if hotel else "Hotel Name Admin"

    def get_template(self, template_name):
        # Look in custom_admin/ first, then default admin/
        return select_template([
            f"custom_admin/{template_name}",
            f"admin/{template_name}",
        ])

admin_site = HotelAdminSite(name='hotel_admin')

# Register your models here with the custom admin site.
admin_site.register(Hotel)
admin_site.register(RoomType)
admin_site.register(Room)
admin_site.register(Booking)
admin_site.register(Guest)
admin_site.register(RoomAmenity)
admin_site.register(HotelAmenity)
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
