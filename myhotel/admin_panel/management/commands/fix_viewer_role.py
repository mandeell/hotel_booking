from django.core.management.base import BaseCommand
from hotel.models import Role, Permission


class Command(BaseCommand):
    help = 'Fix the Viewer role to only have view permissions'

    def handle(self, *args, **options):
        try:
            viewer_role = Role.objects.get(name='Viewer')
            self.stdout.write(f"Found Viewer role with {viewer_role.permissions.count()} permissions")
            
            # Get only view permissions
            view_permissions = Permission.objects.filter(permission_type='view')
            self.stdout.write(f"Found {view_permissions.count()} view permissions")
            
            # Update the role to only have view permissions
            viewer_role.permissions.set(view_permissions)
            viewer_role.description = 'Read-only access to view all data'
            viewer_role.save()
            
            self.stdout.write(f"Updated Viewer role. Now has {viewer_role.permissions.count()} permissions:")
            for perm in viewer_role.permissions.all():
                self.stdout.write(f"  - {perm.codename}: {perm.name}")
                
        except Role.DoesNotExist:
            self.stdout.write("Viewer role not found")