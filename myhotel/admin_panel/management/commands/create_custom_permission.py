from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from hotel.models import Permission


class Command(BaseCommand):
    help = 'Create a custom permission'

    def add_arguments(self, parser):
        parser.add_argument('codename', type=str, help='Permission codename (e.g., manage_reports)')
        parser.add_argument('name', type=str, help='Permission name (e.g., "Can manage reports")')
        parser.add_argument('description', type=str, help='Permission description')
        parser.add_argument(
            '--type',
            type=str,
            default='add',
            choices=['add', 'view', 'edit', 'delete'],
            help='Permission type (default: add)'
        )

    def handle(self, *args, **options):
        codename = options['codename']
        name = options['name']
        description = options['description']
        perm_type = options['type']
        
        # Get or create generic content type for custom permissions
        generic_ct, created = ContentType.objects.get_or_create(
            app_label='admin_panel',
            model='custom'
        )
        
        if created:
            self.stdout.write('Created generic content type for custom permissions')
        
        # Create the permission
        try:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={
                    'name': name,
                    'content_type': generic_ct,
                    'permission_type': perm_type,
                    'description': description
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Successfully created permission: {permission.name} ({permission.codename})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Permission already exists: {permission.name} ({permission.codename})'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating permission: {str(e)}')
            )