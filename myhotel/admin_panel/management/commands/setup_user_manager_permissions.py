from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from hotel.models import Permission


class Command(BaseCommand):
    help = 'Setup user manager permissions'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Setting up user manager permissions...')
        
        # Create content type for user management
        user_ct = ContentType.objects.get_for_model(User)
        
        # Create user management permissions
        user_permissions = [
            ('view_user', 'Can view users', 'Permission to view user accounts'),
            ('add_user', 'Can add users', 'Permission to create new user accounts'),
            ('edit_user', 'Can edit users', 'Permission to edit existing user accounts'),
            ('delete_user', 'Can delete users', 'Permission to delete user accounts'),
            ('assign_roles', 'Can assign roles to users', 'Permission to assign and manage user roles'),
            ('manage_user_status', 'Can manage user status', 'Permission to activate/deactivate users'),
        ]
        
        created_permissions = 0
        
        for codename, name, description in user_permissions:
            if not Permission.objects.filter(codename=codename).exists():
                # Determine permission type based on codename
                if codename.startswith('view'):
                    perm_type = 'view'
                elif codename.startswith('add'):
                    perm_type = 'add'
                elif codename.startswith('edit'):
                    perm_type = 'edit'
                elif codename.startswith('delete'):
                    perm_type = 'delete'
                else:
                    perm_type = 'add'  # Default for custom permissions
                
                permission = Permission.objects.create(
                    name=name,
                    codename=codename,
                    content_type=user_ct,
                    permission_type=perm_type,
                    description=description
                )
                created_permissions += 1
                self.stdout.write(f'  ✓ Created: {permission.name}')
            else:
                self.stdout.write(f'  - Already exists: {name}')
        
        # Create user manager section access permission
        user_manager_ct, _ = ContentType.objects.get_or_create(
            app_label='admin_panel',
            model='user_manager'
        )
        
        if not Permission.objects.filter(codename='access_user_manager').exists():
            permission = Permission.objects.create(
                name='Can access user manager section',
                codename='access_user_manager',
                content_type=user_manager_ct,
                permission_type='view',
                description='Access to user manager section'
            )
            created_permissions += 1
            self.stdout.write(f'  ✓ Created: {permission.name}')
        else:
            self.stdout.write(f'  - Already exists: Can access user manager section')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully created {created_permissions} user manager permissions!'
            )
        )
        
        self.stdout.write('\n📋 User Manager Permissions Created:')
        self.stdout.write('  • Can view users (view_user)')
        self.stdout.write('  • Can add users (add_user)')
        self.stdout.write('  • Can edit users (edit_user)')
        self.stdout.write('  • Can delete users (delete_user)')
        self.stdout.write('  • Can assign roles to users (assign_roles)')
        self.stdout.write('  • Can manage user status (manage_user_status)')
        self.stdout.write('  • Can access user manager section (access_user_manager)')
        
        self.stdout.write('\n🚀 Next Steps:')
        self.stdout.write('  1. Assign user manager permissions to appropriate roles')
        self.stdout.write('  2. Test user manager functionality')
        self.stdout.write('  3. Create user manager views and templates')