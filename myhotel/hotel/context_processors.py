from django.conf import settings
from .models import Hotel


def hotel_context(request):
    """
    Adds the hotel object to the context for all templates.
    """
    hotel_obj = Hotel.objects.first()
    return {'hotel': hotel_obj}

def settings_context(request):
    """
    Makes Django settings available to templates.
    """
    return {'settings': settings}