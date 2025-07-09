from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from hotel.models import UserRole, Role


class Command(BaseCommand):
    help = 'Check user permissions and role assignments'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to check')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"User: {user.username}")
            self.stdout.write(f"Is superuser: {user.is_superuser}")
            self.stdout.write(f"Is staff: {user.is_staff}")
            self.stdout.write(f"Is active: {user.is_active}")
            
            # Check assigned roles
            user_roles = UserRole.objects.filter(user=user)
            self.stdout.write(f"\nAssigned roles ({user_roles.count()}):")
            for ur in user_roles:
                self.stdout.write(f"  - {ur.role.name} (Active: {ur.role.is_active})")
                self.stdout.write(f"    Permissions: {ur.role.permissions.count()}")
            
            # Check all available roles
            self.stdout.write(f"\nAll available roles:")
            for role in Role.objects.all():
                self.stdout.write(f"  - {role.name}: {role.permissions.count()} permissions (Active: {role.is_active})")
            
            # Test permission checking
            from admin_panel.permission_decorators import has_permission
            test_permissions = ['view_booking', 'edit_booking', 'view_room', 'add_room']
            self.stdout.write(f"\nPermission tests:")
            for perm in test_permissions:
                result = has_permission(user, perm)
                self.stdout.write(f"  - {perm}: {result}")
                
        except User.DoesNotExist:
            self.stdout.write(f"User '{username}' not found")