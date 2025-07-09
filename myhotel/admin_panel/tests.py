from django.test import TestCase
from django.contrib.auth.models import User
from django.template import Context, Template
from .templatetags.admin_extras import user_initial, safe_first_char


class TemplateFilterTests(TestCase):
    def setUp(self):
        # Create test users
        self.user_with_first_name = User.objects.create_user(
            username='testuser1',
            first_name='John',
            last_name='Doe'
        )
        
        self.user_without_first_name = User.objects.create_user(
            username='testuser2',
            first_name='',
            last_name='Smith'
        )
        
        self.user_empty_username = User.objects.create_user(
            username='u',
            first_name='',
            last_name=''
        )

    def test_user_initial_with_first_name(self):
        """Test user_initial filter with user having first name"""
        result = user_initial(self.user_with_first_name)
        self.assertEqual(result, 'J')

    def test_user_initial_without_first_name(self):
        """Test user_initial filter with user having no first name"""
        result = user_initial(self.user_without_first_name)
        self.assertEqual(result, 'T')  # First letter of 'testuser2'

    def test_user_initial_fallback(self):
        """Test user_initial filter fallback"""
        result = user_initial(self.user_empty_username)
        self.assertEqual(result, 'U')  # First letter of 'u'

    def test_safe_first_char_with_string(self):
        """Test safe_first_char filter with valid string"""
        result = safe_first_char('Hello')
        self.assertEqual(result, 'H')

    def test_safe_first_char_with_empty_string(self):
        """Test safe_first_char filter with empty string"""
        result = safe_first_char('')
        self.assertEqual(result, '')

    def test_safe_first_char_with_none(self):
        """Test safe_first_char filter with None"""
        result = safe_first_char(None)
        self.assertEqual(result, '')

    def test_template_rendering(self):
        """Test that the template filter works in actual template rendering"""
        template = Template("{% load admin_extras %}{{ user|user_initial }}")
        context = Context({'user': self.user_with_first_name})
        result = template.render(context)
        self.assertEqual(result, 'J')