# 🏨 Hotel Booking Management System

A comprehensive, full-featured hotel booking and management system built with Django. This application provides both a customer-facing booking interface and a powerful administrative panel for hotel management.

![Django](https://img.shields.io/badge/Django-5.2.4-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)

## 📋 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Admin Panel](#-admin-panel)
- [Database Schema](#-database-schema)
- [Payment Integration](#-payment-integration)
- [Security Features](#-security-features)
- [Mobile Responsiveness](#-mobile-responsiveness)
- [Contributing](#-contributing)

## ✨ Features

### 🎯 Core Functionality

#### Customer-Facing Features
- **🏠 Hotel Showcase**: Beautiful, responsive hotel presentation with image galleries
- **🔍 Room Search & Filtering**: Advanced search with date range, guest count, and room type filters
- **📅 Real-time Availability**: Live room availability checking with conflict prevention
- **💳 Secure Booking**: Complete booking workflow with payment integration
- **📱 Mobile-First Design**: Fully responsive design optimized for all devices
- **📧 Contact System**: Integrated contact forms with email notifications
- **🎨 Modern UI/UX**: Clean, professional interface with smooth animations

#### Administrative Features
- **📊 Comprehensive Dashboard**: Real-time analytics and booking insights
- **🏨 Hotel Management**: Multi-hotel support with detailed property management
- **🛏️ Room Management**: Complete room inventory with types, amenities, and pricing
- **📋 Booking Management**: Full booking lifecycle management with status tracking
- **👥 Guest Management**: Customer database with booking history
- **💰 Financial Tracking**: Revenue analytics and payment monitoring
- **🔐 User Management**: Role-based access control with custom permissions
- **📈 Reporting**: Detailed reports and analytics

### 🛡️ Advanced Features

#### Security & Authentication
- **🔒 Role-Based Access Control (RBAC)**: Granular permission system
- **👤 User Profile Management**: Extended user profiles with avatars
- **🔐 Secure Authentication**: Django's built-in authentication with custom enhancements
- **🛡️ CSRF Protection**: Complete protection against cross-site request forgery
- **🔑 Permission Management**: Custom permission system for fine-grained control

#### Data Management
- **🗑️ Soft Delete System**: Data preservation with soft delete functionality
- **📝 Audit Trail**: Complete tracking of data changes and user actions
- **💾 Data Validation**: Comprehensive validation at model and form levels
- **🔄 Data Integrity**: Foreign key constraints and business rule enforcement

#### Integration & APIs
- **💳 Paystack Integration**: Secure payment processing with Paystack
- **📧 Email System**: SMTP integration for notifications and confirmations
- **🌐 RESTful APIs**: AJAX endpoints for dynamic functionality
- **📱 Responsive Design**: Bootstrap-based responsive framework

## 🏗️ System Architecture

### Application Structure
```
hotel_booking/
├── myhotel/                    # Main Django project
│   ├── hotel/                  # Customer-facing application
│   │   ├── models.py          # Core business models
│   │   ├── views.py           # Customer views and booking logic
│   │   ├── forms.py           # Customer forms and validation
│   │   ├── templates/         # Customer-facing templates
│   │   ├── static/            # CSS, JS, images for customer site
│   │   ├── booking.py         # Booking business logic
│   │   ├── room_availability.py # Availability checking system
│   │   └── context_processors.py # Template context processors
│   │
│   ├── admin_panel/           # Administrative application
│   │   ├── views/             # Admin views (modular structure)
│   │   │   ├── dashboard.py   # Dashboard and analytics
│   │   │   ├── booking_views.py # Booking management
│   │   │   ├── room_views.py  # Room management
│   │   │   ├── guest_views.py # Guest management
│   │   │   ├── hotel_views.py # Hotel management
│   │   │   ├── user_manager_views.py # User management
│   │   │   └── permission_views.py # Permission management
│   │   ├── templates/         # Admin panel templates
│   │   ├── static/            # Admin panel assets
│   │   └── forms.py           # Admin forms
│   │
│   ├── myhotel/               # Project settings
│   │   ├── settings.py        # Django configuration
│   │   ├── urls.py            # URL routing
│   │   └── wsgi.py            # WSGI configuration
│   │
│   ├── media/                 # User-uploaded files
│   ├── manage.py              # Django management script
│   └── db.sqlite3             # SQLite database
│
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

### Technology Stack
- **Backend**: Django 5.2.4 (Python web framework)
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5.3.0 with custom styling
- **Icons**: Font Awesome 6.0.0
- **Fonts**: Google Fonts (Playfair Display, Inter)
- **Payment**: Paystack API integration
- **Email**: SMTP with Django's email framework

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd hotel_booking
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the `myhotel/` directory:
   ```env
   SECRET_KEY=your-secret-key-here
   PAYSTACK_SECRET_KEY=your-paystack-secret-key
   PAYSTACK_PUBLIC_KEY=your-paystack-public-key
   EMAIL_HOST=your-smtp-host
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@example.com
   EMAIL_HOST_PASSWORD=your-email-password
   DEFAULT_FROM_EMAIL=your-email@example.com
   ```

5. **Database Setup**
   ```bash
   cd myhotel
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

8. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

9. **Access the Application**
   - Customer Site: http://127.0.0.1:8000/hotel/
   - Admin Panel: http://127.0.0.1:8000/hotel/admin/
   - Django Admin: http://127.0.0.1:8000/admin/

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key for cryptographic signing | Yes |
| `PAYSTACK_SECRET_KEY` | Paystack secret key for payment processing | Yes |
| `PAYSTACK_PUBLIC_KEY` | Paystack public key for frontend integration | Yes |
| `EMAIL_HOST` | SMTP server hostname | Yes |
| `EMAIL_PORT` | SMTP server port | Yes |
| `EMAIL_HOST_USER` | SMTP username | Yes |
| `EMAIL_HOST_PASSWORD` | SMTP password | Yes |
| `DEFAULT_FROM_EMAIL` | Default sender email address | Yes |

### Database Configuration

The application uses SQLite by default for development. For production, configure PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hotel_booking_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📖 Usage

### Customer Workflow

1. **Browse Hotels**: View hotel information, amenities, and room types
2. **Search Availability**: Use the booking form to check room availability
3. **Select Rooms**: Choose from available room types with detailed information
4. **Make Booking**: Complete the booking form with guest details
5. **Payment**: Secure payment processing through Paystack
6. **Confirmation**: Receive booking confirmation and receipt

### Administrator Workflow

1. **Dashboard Access**: Login to the admin panel for overview analytics
2. **Hotel Setup**: Configure hotel information, amenities, and room types
3. **Room Management**: Add rooms, set pricing, and manage availability
4. **Booking Management**: View, edit, and manage customer bookings
5. **Guest Management**: Access customer database and booking history
6. **User Management**: Create staff accounts with appropriate permissions
7. **Reports**: Generate and view various business reports

## 🔌 API Documentation

### Availability Check API

**Endpoint**: `/hotel/admin/api/check-room-availability/`
**Method**: POST
**Purpose**: Check room availability for specific dates

**Request Body**:
```json
{
    "checkin": "2024-01-15",
    "checkout": "2024-01-20",
    "room_type": 1,
    "guests": 2
}
```

**Response**:
```json
{
    "available": true,
    "available_rooms": 3,
    "total_price": 500.00,
    "nights": 5
}
```

### Contact Form API

**Endpoint**: `/hotel/contact/submit/`
**Method**: POST
**Purpose**: Submit contact form

**Request Body**:
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Inquiry",
    "message": "Hello, I have a question..."
}
```

## 🛠️ Admin Panel

### Dashboard Features
- **📊 Booking Analytics**: Real-time booking statistics and trends
- **💰 Revenue Tracking**: Financial performance metrics
- **📈 Occupancy Rates**: Room utilization analytics
- **🎯 Quick Actions**: Fast access to common administrative tasks

### Management Modules

#### 🏨 Hotel Management
- Hotel information and branding
- Contact details and descriptions
- Logo and image management
- Amenity configuration

#### 🛏️ Room Management
- Room type creation and editing
- Pricing and capacity management
- Amenity assignment
- Image gallery management
- Individual room tracking

#### 📋 Booking Management
- Booking status tracking (Pending, Confirmed, Cancelled)
- Payment status monitoring
- Guest information management
- Special request handling
- Booking modification and cancellation

#### 👥 User Management
- Staff account creation
- Role and permission assignment
- User profile management
- Activity monitoring

#### 🔐 Permission System
- Custom permission creation
- Role-based access control
- Granular permission assignment
- Permission auditing

## 🗄️ Database Schema

### Core Models

#### Hotel
- Basic hotel information
- Contact details
- Branding assets

#### RoomType
- Room categories and descriptions
- Pricing and capacity
- Amenity relationships
- Image management

#### Room
- Individual room instances
- Room number tracking
- Availability status
- Hotel association

#### Booking
- Reservation details
- Guest information
- Payment tracking
- Status management

#### Guest
- Customer information
- Contact details
- Booking history

### Security Models

#### Permission
- Custom permission definitions
- Content type associations
- Permission type categorization

#### Role
- Permission groupings
- Role descriptions
- Active status tracking

#### UserRole
- User-role assignments
- Assignment tracking
- Audit trail

## 💳 Payment Integration

### Paystack Integration
- **Secure Processing**: PCI-compliant payment handling
- **Multiple Payment Methods**: Card payments, bank transfers
- **Transaction Tracking**: Complete payment audit trail
- **Webhook Support**: Real-time payment status updates
- **Refund Management**: Automated refund processing

### Payment Workflow
1. Customer completes booking form
2. Payment amount calculated automatically
3. Secure redirect to Paystack payment page
4. Payment processing and verification
5. Booking confirmation and receipt generation
6. Email notifications sent to customer and admin

## 🛡️ Security Features

### Authentication & Authorization
- **Django Authentication**: Built-in user authentication system
- **Custom Permissions**: Granular access control
- **Role-Based Access**: Hierarchical permission system
- **Session Management**: Secure session handling
- **Password Validation**: Strong password requirements

### Data Protection
- **CSRF Protection**: Cross-site request forgery prevention
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Output escaping and sanitization
- **Soft Delete**: Data preservation and recovery
- **Audit Logging**: Complete action tracking

### Infrastructure Security
- **Environment Variables**: Sensitive data protection
- **HTTPS Ready**: SSL/TLS configuration support
- **Security Headers**: Comprehensive security headers
- **Input Validation**: Server-side validation for all inputs

## 📱 Mobile Responsiveness

### Design Features
- **Mobile-First Approach**: Optimized for mobile devices
- **Responsive Grid**: Bootstrap-based responsive layout
- **Touch-Friendly**: Large touch targets and intuitive navigation
- **Fast Loading**: Optimized images and minimal JavaScript
- **Cross-Browser**: Compatible with all modern browsers

### Mobile-Specific Enhancements
- **Hamburger Menu**: Collapsible navigation for mobile
- **Touch Gestures**: Swipe and touch interactions
- **Optimized Forms**: Mobile-friendly form layouts
- **Image Optimization**: Responsive images with proper sizing
- **Performance**: Minimal load times on mobile networks

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test hotel
python manage.py test admin_panel

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Coverage
- Model validation tests
- View functionality tests
- Form validation tests
- API endpoint tests
- Authentication tests
- Permission system tests

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure production database
- [ ] Set up static file serving
- [ ] Configure email backend
- [ ] Set up SSL/HTTPS
- [ ] Configure allowed hosts
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

### Deployment Options
- **Traditional Hosting**: Apache/Nginx + Gunicorn
- **Cloud Platforms**: AWS, Google Cloud, Azure
- **Platform as a Service**: Heroku, PythonAnywhere
- **Containerization**: Docker deployment ready

## 🤝 Contributing

We welcome contributions to improve the Hotel Booking Management System!

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for any changes
- Ensure backward compatibility
- Add appropriate error handling

### Code Style
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Follow Django best practices
- Maintain consistent indentation (4 spaces)


## 📞 Support

For support, questions, or feature requests:

- **Documentation**: Check this README and inline code documentation
- **Issues**: Open an issue on the GitHub repository
- **Email**: Contact the development team
- **Community**: Join our developer community discussions

## 🙏 Acknowledgments

- Django framework and community
- Bootstrap for responsive design
- Font Awesome for icons
- Paystack for payment processing
- All contributors and testers

---

**Built with ❤️ using Django**

*This project demonstrates modern web development practices with Django, including responsive design, secure payment processing, comprehensive admin functionality, and production-ready architecture.*
