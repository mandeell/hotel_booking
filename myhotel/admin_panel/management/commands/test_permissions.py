from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.test import RequestFactory
from admin_panel.permission_decorators import has_permission
from admin_panel.context_processors import user_permissions_context


class Command(BaseCommand):
    help = 'Test the permission system functionality'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to test')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            
            # Test permission checking function
            self.stdout.write(f"Testing permission system for user: {user.username}")
            self.stdout.write(f"Is superuser: {user.is_superuser}")
            
            # Test various permissions
            permissions_to_test = [
                'view_booking', 'edit_booking', 'add_booking', 'delete_booking',
                'view_room', 'edit_room', 'add_room', 'delete_room',
                'view_guest', 'edit_guest', 'add_guest', 'delete_guest',
                'view_contactform'
            ]
            
            self.stdout.write("\nPermission Test Results:")
            self.stdout.write("-" * 40)
            
            for perm in permissions_to_test:
                result = has_permission(user, perm)
                status = "✓ ALLOWED" if result else "✗ DENIED"
                self.stdout.write(f"{perm:<20} {status}")
            
            # Test context processor
            self.stdout.write("\nContext Processor Test:")
            self.stdout.write("-" * 40)
            
            # Create a mock request
            factory = RequestFactory()
            request = factory.get('/')
            request.user = user
            
            context = user_permissions_context(request)
            
            self.stdout.write(f"User roles: {context['user_role_names']}")
            self.stdout.write(f"Is admin user: {context['is_admin_user']}")
            self.stdout.write(f"Total permissions: {len(context['user_permission_codenames'])}")
            self.stdout.write(f"Permission codenames: {context['user_permission_codenames']}")
            
            # Test specific scenarios
            self.stdout.write("\nScenario Tests:")
            self.stdout.write("-" * 40)
            
            if user.is_superuser:
                self.stdout.write("✓ Superuser has all permissions")
            else:
                can_view_bookings = has_permission(user, 'view_booking')
                can_edit_bookings = has_permission(user, 'edit_booking')
                can_view_rooms = has_permission(user, 'view_room')
                can_edit_rooms = has_permission(user, 'edit_room')
                
                if can_view_bookings and not can_edit_bookings:
                    self.stdout.write("✓ Read-only access to bookings working correctly")
                elif can_view_bookings and can_edit_bookings:
                    self.stdout.write("✓ Full access to bookings")
                else:
                    self.stdout.write("✗ No access to bookings")
                
                if can_view_rooms and not can_edit_rooms:
                    self.stdout.write("✓ Read-only access to rooms working correctly")
                elif can_view_rooms and can_edit_rooms:
                    self.stdout.write("✓ Full access to rooms")
                else:
                    self.stdout.write("✗ No access to rooms")
            
            self.stdout.write("\n" + "="*50)
            self.stdout.write("Permission system test completed successfully!")
            
        except User.DoesNotExist:
            self.stdout.write(f"User '{username}' not found")