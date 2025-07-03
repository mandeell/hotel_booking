from django.contrib import admin
from .models import Booking, Room, Hotel, RoomType, Guest, RoomAmenity, HotelAmenity

# Register your models here with the default custom_admin site.
admin.site.register(Hotel)
admin.site.register(RoomType)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(Guest)
admin.site.register(RoomAmenity)
admin.site.register(HotelAmenity)
