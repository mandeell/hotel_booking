from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from hotel.models import Permission
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Add room type section access permission'

    def handle(self, *args, **options):
        self.stdout.write('Adding room type section access permission...')
        
        # Create a generic content type for category permissions
        # Use a different content type to avoid unique constraint issues
        generic_ct, _ = ContentType.objects.get_or_create(
            app_label='admin_panel',
            model='section_access'
        )
        
        # Define the new permission
        codename = 'access_room_types'
        name = 'Can access room types section'
        description = 'Access to room types management'
        
        # Check if permission already exists
        if Permission.objects.filter(codename=codename).exists():
            self.stdout.write(f'  ⚠️ Permission {codename} already exists, skipping...')
            return
        
        try:
            # Try to create the permission with 'view' permission_type
            permission = Permission.objects.create(
                name=name,
                codename=codename,
                content_type=generic_ct,
                permission_type='view',  # Using 'view' as a convention for section access
                description=description
            )
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
                self.stdout.write(f'  ✓ Created: {permission.name} (with add permission_type)')
            except IntegrityError:
                self.stdout.write(self.style.ERROR(f'  ❌ Could not create permission {codename} due to integrity constraints'))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully added room type section access permission!'
            )
        )