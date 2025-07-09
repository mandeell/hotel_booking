# MyHotel - Hotel Management System

A comprehensive Django-based hotel management system with advanced admin panel functionality, user management, and role-based access control.

## 🏨 Project Overview

MyHotel is a full-featured hotel management application built with Django that provides:
- Advanced user management with role-based permissions
- Comprehensive admin panel with granular access controls
- Hotel operations management
- Search and filtering capabilities
- Responsive web interface

## 🚀 Features

### Admin Panel
- **User Management**: Complete CRUD operations for user accounts
- **Role-Based Access Control**: Granular permissions system with custom decorators
- **Advanced Search & Filtering**: Multi-criteria search across users and roles
- **Pagination**: Efficient data handling for large datasets
- **Permission Management**: Model-level and section-level access controls

### User Management
- User registration and authentication
- Role assignment and management
- User status tracking (active/inactive)
- Profile management
- Password management with secure forms

### Security Features
- Custom permission decorators (`@require_model_permission`, `@require_section_access`)
- Login required decorators
- Superuser access controls
- Secure password handling

## 🛠️ Technology Stack

- **Backend**: Django (Python)
- **Database**: Django ORM (supports PostgreSQL, MySQL, SQLite)
- **Frontend**: HTML, CSS, JavaScript with Tailwind CSS styling
- **Authentication**: Django's built-in authentication system
- **Permissions**: Custom role-based permission system

## 📁 Project Structure


Copy

Insert

myhotel/ ├── admin_panel/ │ ├── views/ │ │ └── user_manager_views.py # User management views │ ├── forms.py # Admin panel forms │ ├── permission_decorators.py # Custom permission decorators │ └── templates/ │ └── admin_panel/ │ └── user_manager/ ├── hotel/ │ └── models.py # Core models (User, Role, UserRole) ├── static/ # Static files (CSS, JS, images) ├── templates/ # HTML templates ├── manage.py # Django management script └── requirements.txt # Python dependencies


## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd myhotel

Copy

Insert

Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Copy

Insert

Install dependencies
pip install -r requirements.txt

Copy

Insert

Configure database settings
# Update settings.py with your database configuration

Copy

Insert

Run migrations
python manage.py makemigrations
python manage.py migrate

Copy

Insert

Create superuser
python manage.py createsuperuser

Copy

Insert

Collect static files
python manage.py collectstatic

Copy

Insert

Run development server
python manage.py runserver

Copy

Insert

🔐 Permission System
The application uses a sophisticated permission system with custom decorators:

Permission Decorators
@require_model_permission(model, permission_type): Checks model-level permissions
@require_section_access(section): Controls access to admin sections
@require_permission(permission): General permission checking
@require_superuser: Restricts access to superusers only
Usage Example
@require_model_permission(User, 'view', redirect_url='admin_panel:user_list')
def user_manager_list(request):
    # View implementation

Copy

Insert

📊 User Management Features
User List View
Search: Multi-field search across username, email, and names
Filtering: Filter by role and user status
Pagination: 20 users per page with navigation
Role Display: Shows all roles assigned to each user
Statistics: Active/inactive user counts
Search Capabilities
The system supports advanced search with the following criteria:

Username (partial match)
First name (partial match)
Last name (partial match)
Email address (partial match)
Role-based filtering
Status filtering (active/inactive)
🎨 Frontend Styling
The application uses Tailwind CSS for responsive and modern UI components:

Form styling with focus states
Responsive design patterns
Consistent color scheme
Accessible form controls
🔧 Configuration
Key Settings
Pagination: 20 items per page (configurable)
Search: Case-insensitive partial matching
Permissions: Model-based with fallback redirects
Authentication: Django's built-in system
Environment Variables
Create a .env file for sensitive configurations:

SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=your-database-url

Copy

Insert

🧪 Testing
Run the test suite:

python manage.py test

Copy

Insert

📝 API Documentation
The admin panel provides RESTful endpoints for:

User CRUD operations
Role management
Permission checking
Search and filtering
🤝 Contributing
Fork the repository
Create a feature branch (git checkout -b feature/new-feature)
Commit your changes (git commit -am 'Add new feature')
Push to the branch (git push origin feature/new-feature)
Create a Pull Request
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🆘 Support
For support and questions:

Create an issue in the repository
Check the documentation
Review the code comments for implementation details
🔄 Version History
v1.0.0: Initial release with user management and admin panel
v1.1.0: Added advanced search and filtering
v1.2.0: Enhanced permission system with custom decorators
Note: This is a hotel management system designed for administrative use. Ensure proper security measures are in place before deploying to production.
