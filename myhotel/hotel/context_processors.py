from django.conf import settings

def settings_context(request):
    """
    Makes Django settings available to templates.
    """
    return {'settings': settings}