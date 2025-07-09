from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from hotel.models import (
    Permission, Role, Hotel, Room, RoomType, RoomAmenity, 
    HotelAmenity, Booking, Guest, ContactForm
)


class Command(BaseCommand):
    help = 'Create default permissions and roles for the admin panel'

    def handle(self, *args, **options):
        self.stdout.write('Setting up admin panel permissions...')
        
        # Define models and their names
        models = [
            ('hotel', Hotel),
            ('room', Room),
            ('roomtype', RoomType),
            ('roomamenity', RoomAmenity),
            ('hotelamenity', HotelAmenity),
            ('booking', Booking),
            ('guest', Guest),
            ('contactform', ContactForm),
        ]
        
        created_permissions = 0
        
        # Create permissions for each model
        for model_name, model_class in models:
            content_type = ContentType.objects.get_for_model(model_class)
            
            for perm_type, perm_display in Permission.PERMISSION_TYPES:
                permission, created = Permission.objects.get_or_create(
                    content_type=content_type,
                    permission_type=perm_type,
                    defaults={
                        'name': f'Can {perm_display.lower()} {model_name}',
                        'codename': f'{perm_type}_{model_name}',
                        'description': f'Permission to {perm_display.lower()} {model_name} records'
                    }
                )
                if created:
                    created_permissions += 1
                    self.stdout.write(f'Created permission: {permission.name}')
        
        # Create default roles
        self.stdout.write('\nCreating default roles...')
        
        # 1. Booking Manager Role
        booking_manager_role, created = Role.objects.get_or_create(
            name='Booking Manager',
            defaults={
                'description': 'Can view and edit bookings, view contact forms',
                'is_active': True
            }
        )
        
        if created:
            # Add permissions for booking manager
            booking_permissions = Permission.objects.filter(
                codename__in=[
                    'view_booking', 'edit_booking',
                    'view_contactform'
                ]
            )
            booking_manager_role.permissions.set(booking_permissions)
            self.stdout.write(f'Created role: {booking_manager_role.name}')
        
        # 2. Room Manager Role
        room_manager_role, created = Role.objects.get_or_create(
            name='Room Manager',
            defaults={
                'description': 'Can manage rooms, room types, and amenities',
                'is_active': True
            }
        )
        
        if created:
            # Add permissions for room manager
            room_permissions = Permission.objects.filter(
                codename__in=[
                    'view_room', 'add_room', 'edit_room', 'delete_room',
                    'view_roomtype', 'add_roomtype', 'edit_roomtype', 'delete_roomtype',
                    'view_roomamenity', 'add_roomamenity', 'edit_roomamenity', 'delete_roomamenity',
                    'view_hotelamenity', 'add_hotelamenity', 'edit_hotelamenity', 'delete_hotelamenity'
                ]
            )
            room_manager_role.permissions.set(room_permissions)
            self.stdout.write(f'Created role: {room_manager_role.name}')
        
        # 3. Guest Manager Role
        guest_manager_role, created = Role.objects.get_or_create(
            name='Guest Manager',
            defaults={
                'description': 'Can manage guest information',
                'is_active': True
            }
        )
        
        if created:
            # Add permissions for guest manager
            guest_permissions = Permission.objects.filter(
                codename__in=[
                    'view_guest', 'add_guest', 'edit_guest', 'delete_guest'
                ]
            )
            guest_manager_role.permissions.set(guest_permissions)
            self.stdout.write(f'Created role: {guest_manager_role.name}')
        
        # 4. Hotel Administrator Role (full access)
        hotel_admin_role, created = Role.objects.get_or_create(
            name='Hotel Administrator',
            defaults={
                'description': 'Full access to all hotel management features',
                'is_active': True
            }
        )
        
        if created:
            # Add all permissions to hotel administrator
            all_permissions = Permission.objects.all()
            hotel_admin_role.permissions.set(all_permissions)
            self.stdout.write(f'Created role: {hotel_admin_role.name}')
        
        # 5. Read-Only Role
        readonly_role, created = Role.objects.get_or_create(
            name='Read-Only User',
            defaults={
                'description': 'Can only view data, no editing permissions',
                'is_active': True
            }
        )
        
        if created:
            # Add only view permissions
            view_permissions = Permission.objects.filter(permission_type='view')
            readonly_role.permissions.set(view_permissions)
            self.stdout.write(f'Created role: {readonly_role.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_permissions} permissions and set up default roles!'
            )
        )
        
        self.stdout.write('\nAvailable roles:')
        for role in Role.objects.filter(is_active=True):
            self.stdout.write(f'  - {role.name}: {role.permissions.count()} permissions')