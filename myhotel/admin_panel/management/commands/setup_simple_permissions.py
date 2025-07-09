from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from hotel.models import (
    Permission, Role, UserRole, Hotel, Room, RoomType, RoomAmenity, 
    HotelAmenity, Booking, Guest, ContactForm
)


class Command(BaseCommand):
    help = 'Setup simple model-based permissions without conflicts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-all',
            action='store_true',
            help='Clear all existing permissions and roles',
        )

    def handle(self, *args, **options):
        if options['clear_all']:
            self.stdout.write('🗑️  Clearing existing permissions and roles...')
            UserRole.objects.all().delete()
            Role.objects.all().delete()
            Permission.objects.all().delete()
            self.stdout.write('✅ Cleared all existing data')
        
        self.stdout.write('🔧 Setting up model-based permissions...')
        
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
            self.stdout.write(f'\n📂 Creating permissions for {data["description"]}...')
            
            for model_name, model_class in data['models']:
                content_type = ContentType.objects.get_for_model(model_class)
                
                for perm_type, perm_display in Permission.PERMISSION_TYPES:
                    codename = f'{perm_type}_{model_name}'
                    
                    if not Permission.objects.filter(codename=codename).exists():
                        permission = Permission.objects.create(
                            name=f'Can {perm_display.lower()} {model_name}',
                            codename=codename,
                            content_type=content_type,
                            permission_type=perm_type,
                            description=f'Permission to {perm_display.lower()} {model_name} records'
                        )
                        created_permissions += 1
                        self.stdout.write(f'  ✓ Created: {permission.name}')
                    else:
                        self.stdout.write(f'  - Already exists: Can {perm_display.lower()} {model_name}')
        
        # Create section access permissions using unique content types
        self.stdout.write(f'\n🔐 Creating section access permissions...')
        
        section_permissions = [
            ('access_booking', 'Can access booking section', 'booking_access'),
            ('access_guest', 'Can access guest section', 'guest_access'),
            ('access_room_setup', 'Can access room setup section', 'room_setup_access'),
            ('access_hotel_setup', 'Can access hotel setup section', 'hotel_setup_access'),
            ('access_contact', 'Can access contact section', 'contact_access'),
            ('access_account', 'Can access account section', 'account_access'),
        ]
        
        for codename, name, model_suffix in section_permissions:
            if not Permission.objects.filter(codename=codename).exists():
                # Create unique content type for each section
                section_ct, _ = ContentType.objects.get_or_create(
                    app_label='admin_panel',
                    model=model_suffix
                )
                
                permission = Permission.objects.create(
                    name=name,
                    codename=codename,
                    content_type=section_ct,
                    permission_type='view',
                    description=f'Access to {name.lower()}'
                )
                created_permissions += 1
                self.stdout.write(f'  ✓ Created: {permission.name}')
            else:
                self.stdout.write(f'  - Already exists: {name}')
        
        # Create custom permissions using unique content types
        custom_permissions = [
            ('manage_system', 'Can manage system settings', 'system_management'),
            ('view_reports', 'Can view reports', 'reports_access'),
            ('export_data', 'Can export data', 'data_export'),
            ('import_data', 'Can import data', 'data_import'),
            ('backup_system', 'Can backup system', 'system_backup'),
            ('restore_system', 'Can restore system', 'system_restore'),
        ]
        
        self.stdout.write(f'\n⚙️  Creating custom permissions...')
        for codename, name, model_suffix in custom_permissions:
            if not Permission.objects.filter(codename=codename).exists():
                # Create unique content type for each custom permission
                custom_ct, _ = ContentType.objects.get_or_create(
                    app_label='admin_panel',
                    model=model_suffix
                )
                
                permission = Permission.objects.create(
                    name=name,
                    codename=codename,
                    content_type=custom_ct,
                    permission_type='add',
                    description=f'Custom permission: {name.lower()}'
                )
                created_permissions += 1
                self.stdout.write(f'  ✓ Created: {permission.name}')
            else:
                self.stdout.write(f'  - Already exists: {name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Successfully created {created_permissions} new permissions!'
            )
        )
        
        # Summary
        total_permissions = Permission.objects.count()
        self.stdout.write(f'\n📊 PERMISSION SUMMARY')
        self.stdout.write(f'Total permissions in system: {total_permissions}')
        
        self.stdout.write('\n📋 Model Permissions:')
        for category, data in model_categories.items():
            model_count = len(data['models'])
            perm_count = model_count * 4  # 4 permission types per model
            self.stdout.write(f'  • {data["description"]}: {perm_count} permissions')
        
        self.stdout.write('\n🔐 Section Access Permissions:')
        for codename, name, _ in section_permissions:
            self.stdout.write(f'  • {name} ({codename})')
        
        self.stdout.write('\n⚙️  Custom Permissions:')
        for codename, name, _ in custom_permissions:
            self.stdout.write(f'  • {name} ({codename})')
        
        self.stdout.write('\n🚀 NEXT STEPS:')
        self.stdout.write('  1. Create roles using admin panel or management commands')
        self.stdout.write('  2. Assign permissions to roles')
        self.stdout.write('  3. Assign roles to users')
        self.stdout.write('  4. Test access: python manage.py test_user_access <username>')
        
        self.stdout.write('\n💡 USEFUL COMMANDS:')
        self.stdout.write('  • python manage.py create_custom_permission <codename> <name> <description>')
        self.stdout.write('  • python manage.py list_permissions [--category=<category>]')
        self.stdout.write('  • python manage.py test_user_access <username>')
        
        self.stdout.write('\n✨ Permission system is ready for use!')