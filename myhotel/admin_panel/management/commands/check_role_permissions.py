from django.core.management.base import BaseCommand
from hotel.models import Role


class Command(BaseCommand):
    help = 'Check permissions for a specific role'

    def add_arguments(self, parser):
        parser.add_argument('role_name', type=str, help='Role name to check')

    def handle(self, *args, **options):
        role_name = options['role_name']
        
        try:
            role = Role.objects.get(name=role_name)
            self.stdout.write(f"Role: {role.name}")
            self.stdout.write(f"Description: {role.description}")
            self.stdout.write(f"Is active: {role.is_active}")
            self.stdout.write(f"Total permissions: {role.permissions.count()}")
            
            self.stdout.write(f"\nPermissions:")
            for perm in role.permissions.all():
                self.stdout.write(f"  - {perm.codename}: {perm.name}")
                
        except Role.DoesNotExist:
            self.stdout.write(f"Role '{role_name}' not found")