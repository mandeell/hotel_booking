from django.core.management.base import BaseCommand
from hotel.models import Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'List all permissions, optionally filtered by category'

    def add_arguments(self, parser):
        parser.add_argument(
            '--category',
            type=str,
            help='Filter by category (booking, guest, room_setup, hotel_setup, contact, account, custom)'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['add', 'view', 'edit', 'delete'],
            help='Filter by permission type'
        )

    def handle(self, *args, **options):
        category = options.get('category')
        perm_type = options.get('type')
        
        permissions = Permission.objects.select_related('content_type').all()
        
        if perm_type:
            permissions = permissions.filter(permission_type=perm_type)
        
        # Group permissions by category
        categories = {
            'booking': ['booking'],
            'guest': ['guest'],
            'room_setup': ['room', 'roomtype', 'roomamenity'],
            'hotel_setup': ['hotel', 'hotelamenity'],
            'contact': ['contactform'],
            'account': ['permission', 'role'],
            'category_access': [],  # Special category for access permissions
            'custom': []  # Custom permissions
        }
        
        # Organize permissions by category
        categorized_permissions = {cat: [] for cat in categories.keys()}
        
        for perm in permissions:
            model_name = perm.content_type.model
            
            # Check if it's a category access permission
            if perm.codename.startswith('access_'):
                categorized_permissions['category_access'].append(perm)
                continue
            
            # Check if it's a custom permission
            if model_name in ['category', 'custom']:
                categorized_permissions['custom'].append(perm)
                continue
            
            # Find which category this model belongs to
            found_category = None
            for cat, models in categories.items():
                if model_name in models:
                    found_category = cat
                    break
            
            if found_category:
                categorized_permissions[found_category].append(perm)
        
        # Display permissions
        if category:
            if category in categorized_permissions:
                self.display_category(category, categorized_permissions[category])
            else:
                self.stdout.write(f'Category "{category}" not found')
        else:
            for cat, perms in categorized_permissions.items():
                if perms:  # Only show categories that have permissions
                    self.display_category(cat, perms)
    
    def display_category(self, category_name, permissions):
        category_titles = {
            'booking': 'Booking Management',
            'guest': 'Guest Management', 
            'room_setup': 'Room Setup & Management',
            'hotel_setup': 'Hotel Setup & Management',
            'contact': 'Contact Form Management',
            'account': 'Account & Permission Management',
            'category_access': 'Category Access Permissions',
            'custom': 'Custom Permissions'
        }
        
        title = category_titles.get(category_name, category_name.title())
        self.stdout.write(f'\n📂 {title}')
        self.stdout.write('=' * (len(title) + 3))
        
        if not permissions:
            self.stdout.write('  No permissions found')
            return
        
        # Group by permission type
        by_type = {}
        for perm in permissions:
            perm_type = perm.permission_type
            if perm_type not in by_type:
                by_type[perm_type] = []
            by_type[perm_type].append(perm)
        
        for perm_type in ['view', 'add', 'edit', 'delete']:
            if perm_type in by_type:
                type_icon = {
                    'view': '👁️',
                    'add': '➕',
                    'edit': '✏️',
                    'delete': '🗑️'
                }.get(perm_type, '📋')
                
                self.stdout.write(f'\n  {type_icon} {perm_type.upper()} Permissions:')
                for perm in by_type[perm_type]:
                    self.stdout.write(f'    • {perm.name} ({perm.codename})')
                    if perm.description:
                        self.stdout.write(f'      {perm.description}')
        
        self.stdout.write(f'\n  Total: {len(permissions)} permissions')