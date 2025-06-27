from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from .models import Hotel, ContactForm
from django.conf import settings


class ContactFormHandler:
    def __init__(self):
        self.errors = []

    def process(self, name, email, subject, message):
        self.errors = self.validate(name, email, subject, message)
        if self.errors:
            return {'success': False, 'errors': self.errors}

        # Save to database
        self.save_to_db(name, email, subject, message)

        # Send email
        email_body = self.render_email_template(name, email, subject, message)
        self.send_email(email_body)

        return {'success': True, 'message': 'Message sent successfully'}

    def validate(self, name, email, subject, message):
        errors = []
        if not name:
            errors.append("Name is required")
        if not email:
            errors.append("Email is required")
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append("Invalid email format")
        if not subject:
            errors.append("Subject is required")
        if not message:
            errors.append("Message is required")
        return errors

    def save_to_db(self, name, email, subject, message):
        ContactForm.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

    def render_email_template(self, name, email, subject, message):
        hotel = Hotel.objects.first()
        logo_url = f'{settings.MEDIA_URL}hotel/logo.png'
        context = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
            'hotel_name': hotel.name if hotel else 'Your Hotel',
            'hotel_logo': f'{settings.SITE_URL}{logo_url}',
            'hotel_address': hotel.address,
            'hotel_contact_email': hotel.contact_email,
            'hotel_contact_phone': hotel.contact_phone,
        }
        return render_to_string('emails/contact_message.html', context)

    def send_email(self, email_body):
        hotel = Hotel.objects.first()
        recipient = hotel.contact_email if hotel and hotel.contact_email else 'contact@yourhotel.com'
        send_mail(
            subject='New Contact Message',
            message='A new contact message has been received.',
            from_email='noreply@yourhotel.com',
            recipient_list=[recipient],
            html_message=email_body,
        )