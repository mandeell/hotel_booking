from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from hotel.models import (
    Permission, Role, Hotel, Room, RoomType, RoomAmenity, 
    HotelAmenity, Booking, Guest, ContactForm
)


class Command(BaseCommand):
    help = 'Create default permissions for all models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-roles',
            action='store_true',
            help='Also create default roles',
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating default permissions...')
        
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
        
        created_count = 0
        
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
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created permission: {permission.name}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} permissions')
        )
        
        if options['create_roles']:
            self.create_default_roles()
    
    def create_default_roles(self):
        self.stdout.write('Creating default roles...')
        
        # Admin role with all permissions
        admin_role, created = Role.objects.get_or_create(
            name='Administrator',
            defaults={
                'description': 'Full access to all system features',
                'is_active': True
            }
        )
        
        if created:
            admin_role.permissions.set(Permission.objects.all())
            self.stdout.write(
                self.style.SUCCESS('Created Administrator role with all permissions')
            )
        
        # Manager role with most permissions except delete
        manager_role, created = Role.objects.get_or_create(
            name='Manager',
            defaults={
                'description': 'Can manage most features except deletions',
                'is_active': True
            }
        )
        
        if created:
            manager_permissions = Permission.objects.exclude(permission_type='delete')
            manager_role.permissions.set(manager_permissions)
            self.stdout.write(
                self.style.SUCCESS('Created Manager role')
            )
        
        # Staff role with view and edit permissions
        staff_role, created = Role.objects.get_or_create(
            name='Staff',
            defaults={
                'description': 'Can view and edit basic records',
                'is_active': True
            }
        )
        
        if created:
            staff_permissions = Permission.objects.filter(
                permission_type__in=['view', 'edit']
            )
            staff_role.permissions.set(staff_permissions)
            self.stdout.write(
                self.style.SUCCESS('Created Staff role')
            )
        
        # Viewer role with only view permissions
        viewer_role, created = Role.objects.get_or_create(
            name='Viewer',
            defaults={
                'description': 'Read-only access to system data',
                'is_active': True
            }
        )
        
        if created:
            viewer_permissions = Permission.objects.filter(permission_type='view')
            viewer_role.permissions.set(viewer_permissions)
            self.stdout.write(
                self.style.SUCCESS('Created Viewer role')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created default roles')
        )