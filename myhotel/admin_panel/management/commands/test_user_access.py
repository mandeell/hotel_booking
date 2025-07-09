from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from admin_panel.permission_decorators import has_permission


class Command(BaseCommand):
    help = 'Test user access to different sections and models'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to test')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            
            self.stdout.write(f'🔍 Testing access for user: {user.username}')
            self.stdout.write(f'Superuser: {user.is_superuser}')
            self.stdout.write('=' * 50)
            
            # Test category access permissions
            category_tests = [
                ('access_booking', 'Booking Section'),
                ('access_guest', 'Guest Section'),
                ('access_room_setup', 'Room Setup Section'),
                ('access_hotel_setup', 'Hotel Setup Section'),
                ('access_contact', 'Contact Section'),
                ('access_account', 'Account Section'),
            ]
            
            self.stdout.write('\n📂 SECTION ACCESS TESTS')
            self.stdout.write('-' * 30)
            
            accessible_sections = []
            for perm_code, section_name in category_tests:
                has_access = has_permission(user, perm_code)
                status = '✅ ALLOWED' if has_access else '❌ DENIED'
                self.stdout.write(f'{section_name:<25} {status}')
                if has_access:
                    accessible_sections.append(perm_code.replace('access_', ''))
            
            # Test model-level permissions for accessible sections
            model_tests = {
                'booking': [
                    ('view_booking', 'View Bookings'),
                    ('add_booking', 'Add Bookings'),
                    ('edit_booking', 'Edit Bookings'),
                    ('delete_booking', 'Delete Bookings'),
                ],
                'guest': [
                    ('view_guest', 'View Guests'),
                    ('add_guest', 'Add Guests'),
                    ('edit_guest', 'Edit Guests'),
                    ('delete_guest', 'Delete Guests'),
                ],
                'room_setup': [
                    ('view_room', 'View Rooms'),
                    ('add_room', 'Add Rooms'),
                    ('edit_room', 'Edit Rooms'),
                    ('delete_room', 'Delete Rooms'),
                    ('view_roomtype', 'View Room Types'),
                    ('add_roomtype', 'Add Room Types'),
                    ('edit_roomtype', 'Edit Room Types'),
                    ('delete_roomtype', 'Delete Room Types'),
                    ('view_roomamenity', 'View Room Amenities'),
                    ('add_roomamenity', 'Add Room Amenities'),
                    ('edit_roomamenity', 'Edit Room Amenities'),
                    ('delete_roomamenity', 'Delete Room Amenities'),
                ],
                'hotel_setup': [
                    ('view_hotel', 'View Hotel'),
                    ('add_hotel', 'Add Hotel'),
                    ('edit_hotel', 'Edit Hotel'),
                    ('delete_hotel', 'Delete Hotel'),
                    ('view_hotelamenity', 'View Hotel Amenities'),
                    ('add_hotelamenity', 'Add Hotel Amenities'),
                    ('edit_hotelamenity', 'Edit Hotel Amenities'),
                    ('delete_hotelamenity', 'Delete Hotel Amenities'),
                ],
                'contact': [
                    ('view_contactform', 'View Contact Forms'),
                    ('add_contactform', 'Add Contact Forms'),
                    ('edit_contactform', 'Edit Contact Forms'),
                    ('delete_contactform', 'Delete Contact Forms'),
                ],
                'account': [
                    ('view_permission', 'View Permissions'),
                    ('add_permission', 'Add Permissions'),
                    ('edit_permission', 'Edit Permissions'),
                    ('delete_permission', 'Delete Permissions'),
                    ('view_role', 'View Roles'),
                    ('add_role', 'Add Roles'),
                    ('edit_role', 'Edit Roles'),
                    ('delete_role', 'Delete Roles'),
                ],
            }
            
            for section in accessible_sections:
                if section in model_tests:
                    self.stdout.write(f'\n📋 {section.upper().replace("_", " ")} MODEL PERMISSIONS')
                    self.stdout.write('-' * 40)
                    
                    for perm_code, perm_name in model_tests[section]:
                        has_access = has_permission(user, perm_code)
                        status = '✅ ALLOWED' if has_access else '❌ DENIED'
                        self.stdout.write(f'{perm_name:<30} {status}')
            
            # Test custom permissions
            custom_permissions = [
                ('manage_system', 'Manage System'),
                ('view_reports', 'View Reports'),
                ('export_data', 'Export Data'),
                ('import_data', 'Import Data'),
                ('backup_system', 'Backup System'),
                ('restore_system', 'Restore System'),
            ]
            
            self.stdout.write(f'\n🔧 CUSTOM PERMISSIONS')
            self.stdout.write('-' * 25)
            
            for perm_code, perm_name in custom_permissions:
                has_access = has_permission(user, perm_code)
                status = '✅ ALLOWED' if has_access else '❌ DENIED'
                self.stdout.write(f'{perm_name:<20} {status}')
            
            # Summary
            total_sections = len(category_tests)
            accessible_count = len(accessible_sections)
            
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write('📊 ACCESS SUMMARY')
            self.stdout.write(f'Accessible Sections: {accessible_count}/{total_sections}')
            
            if accessible_count == 0:
                self.stdout.write('⚠️  User has no access to any sections')
            elif accessible_count == total_sections:
                self.stdout.write('✅ User has full access to all sections')
            else:
                self.stdout.write('ℹ️  User has limited access')
            
            # Recommendations
            self.stdout.write('\n💡 RECOMMENDATIONS')
            if user.is_superuser:
                self.stdout.write('• User is a superuser - has all permissions automatically')
            elif accessible_count == 0:
                self.stdout.write('• Assign appropriate roles to this user')
                self.stdout.write('• Check if user roles are active')
            else:
                self.stdout.write('• Access levels look appropriate for assigned roles')
                
        except User.DoesNotExist:
            self.stdout.write(f'❌ User "{username}" not found')