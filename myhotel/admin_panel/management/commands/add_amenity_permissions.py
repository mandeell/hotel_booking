from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from hotel.models import Permission
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Add hotel amenities and room amenities section access permissions'

    def handle(self, *args, **options):
        self.stdout.write('Adding hotel amenities and room amenities section access permissions...')
        
        # Create a generic content type for category permissions
        # Use a different content type to avoid unique constraint issues
        generic_ct, _ = ContentType.objects.get_or_create(
            app_label='admin_panel',
            model='section_access'
        )
        
        # Define the new permissions
        new_permissions = [
            ('access_room_amenities', 'Can access room amenities section', 'Access to room amenities management'),
            ('access_hotel_amenities', 'Can access hotel amenities section', 'Access to hotel amenities management'),
        ]
        
        created_count = 0
        for codename, name, description in new_permissions:
            # Check if permission already exists
            if Permission.objects.filter(codename=codename).exists():
                self.stdout.write(f'  ⚠️ Permission {codename} already exists, skipping...')
                continue
            
            try:
                # Try to create the permission with a unique permission_type for each
                permission = Permission.objects.create(
                    name=name,
                    codename=codename,
                    content_type=generic_ct,
                    permission_type='view',  # Using 'view' as a convention for section access
                    description=description
                )
                created_count += 1
                self.stdout.write(f'  ✓ Created: {permission.name}')
            except IntegrityError:
                # If we hit a unique constraint error, try with a different permission_type
                try:
                    permission = Permission.objects.create(
                        name=name,
                        codename=codename,
                        content_type=generic_ct,
                        permission_type='add',  # Try with 'add' instead
                        description=description
                    )
                    created_count += 1
                    self.stdout.write(f'  ✓ Created: {permission.name} (with add permission_type)')
                except IntegrityError:
                    self.stdout.write(self.style.ERROR(f'  ❌ Could not create permission {codename} due to integrity constraints'))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully created {created_count} permissions!'
            )
        )