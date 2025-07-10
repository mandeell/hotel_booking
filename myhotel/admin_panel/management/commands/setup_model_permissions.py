from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from hotel.models import (
    Permission, Role, Hotel, Room, RoomType, RoomAmenity, 
    HotelAmenity, Booking, Guest, ContactForm
)


class Command(BaseCommand):
    help = 'Setup model-based permissions for the admin panel'

    def handle(self, *args, **options):
        self.stdout.write('Setting up model-based permissions...')
        
        # Define models and their categories
        model_categories = {
            'booking': {
                'models': [('booking', Booking)],
                'description': 'Booking Management'
            },
            'guest': {
                'models': [('guest', Guest)],
                'description': 'Guest Management'
            },
            'room_setup': {
                'models': [
                    ('room', Room),
                    ('roomtype', RoomType),
                    ('roomamenity', RoomAmenity)
                ],
                'description': 'Room Setup and Management'
            },
            'hotel_setup': {
                'models': [
                    ('hotel', Hotel),
                    ('hotelamenity', HotelAmenity)
                ],
                'description': 'Hotel Setup and Management'
            },
            'contact': {
                'models': [('contactform', ContactForm)],
                'description': 'Contact Form Management'
            },
            'account': {
                'models': [('permission', Permission), ('role', Role)],
                'description': 'Account and Permission Management'
            }
        }
        
        created_permissions = 0
        
        # Create permissions for each model
        for category, data in model_categories.items():
            self.stdout.write(f'\nCreating permissions for {data["description"]}...')
            
            for model_name, model_class in data['models']:
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
                        self.stdout.write(f'  ✓ Created: {permission.name}')
        
        # Create category-level permissions for sidebar access
        self.stdout.write(f'\nCreating category-level permissions...')
        
        category_permissions = [
            ('access_booking', 'Can access booking section', 'Access to booking management'),
            ('access_guest', 'Can access guest section', 'Access to guest management'),
            ('access_room_setup', 'Can access room setup section', 'Access to room setup and management'),
            ('access_hotel_setup', 'Can access hotel setup section', 'Access to hotel setup and management'),
            ('access_room_amenities', 'Can access room amenities section', 'Access to room amenities management'),
            ('access_hotel_amenities', 'Can access hotel amenities section', 'Access to hotel amenities management'),
            ('access_contact', 'Can access contact section', 'Access to contact form management'),
            ('access_account', 'Can access account section', 'Access to account and permission management'),
        ]
        
        # Create a generic content type for category permissions
        generic_ct, _ = ContentType.objects.get_or_create(
            app_label='admin_panel',
            model='category'
        )
        
        for codename, name, description in category_permissions:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={
                    'name': name,
                    'content_type': generic_ct,
                    'permission_type': 'view',
                    'description': description
                }
            )
            if created:
                created_permissions += 1
                self.stdout.write(f'  ✓ Created: {permission.name}')
        
        # Create custom permission types for flexibility
        custom_permissions = [
            ('manage_system', 'Can manage system settings', 'Full system management access'),
            ('view_reports', 'Can view reports', 'Access to system reports'),
            ('export_data', 'Can export data', 'Permission to export system data'),
            ('import_data', 'Can import data', 'Permission to import system data'),
            ('backup_system', 'Can backup system', 'Permission to create system backups'),
            ('restore_system', 'Can restore system', 'Permission to restore system from backups'),
        ]
        
        self.stdout.write(f'\nCreating custom permissions...')
        for codename, name, description in custom_permissions:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={
                    'name': name,
                    'content_type': generic_ct,
                    'permission_type': 'add',  # Using 'add' as a generic type
                    'description': description
                }
            )
            if created:
                created_permissions += 1
                self.stdout.write(f'  ✓ Created: {permission.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully created {created_permissions} permissions!'
            )
        )
        
        self.stdout.write('\n📋 Permission Categories Created:')
        for category, data in model_categories.items():
            model_count = len(data['models'])
            perm_count = model_count * 4  # 4 permission types per model
            self.stdout.write(f'  • {data["description"]}: {perm_count} permissions')
        
        self.stdout.write('\n📋 Category Access Permissions:')
        for codename, name, _ in category_permissions:
            self.stdout.write(f'  • {name} ({codename})')
        
        self.stdout.write('\n📋 Custom Permissions:')
        for codename, name, _ in custom_permissions:
            self.stdout.write(f'  • {name} ({codename})')
        
        self.stdout.write('\n🔧 Next Steps:')
        self.stdout.write('  1. Create roles using the admin panel')
        self.stdout.write('  2. Assign permissions to roles')
        self.stdout.write('  3. Assign roles to users')
        self.stdout.write('  4. Test the permission system')
        
        self.stdout.write('\n💡 Available Management Commands:')
        self.stdout.write('  • python manage.py create_custom_permission <codename> <name> <description>')
        self.stdout.write('  • python manage.py test_user_access <username>')
        self.stdout.write('  • python manage.py list_permissions [--category=<category>]')