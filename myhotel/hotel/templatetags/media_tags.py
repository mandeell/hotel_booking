import os
import time
from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def media_with_version(path):
    """
    Template tag to add version parameter to media files to prevent caching issues
    """
    if not path:
        return ''
    
    # Build the full media URL
    media_url = settings.MEDIA_URL + path
    
    # Get the full file path
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    
    # Add version parameter based on file modification time
    if os.path.exists(full_path):
        mtime = os.path.getmtime(full_path)
        version = str(int(mtime))
        return f"{media_url}?v={version}"
    
    return media_url


@register.simple_tag
def static_with_version(path):
    """
    Template tag to add version parameter to static files to prevent caching issues
    """
    if not path:
        return ''
    
    # Get the static URL
    static_url = static(path)
    
    # Add version parameter based on current time (for development)
    # In production, WhiteNoise handles versioning
    if settings.DEBUG:
        version = str(int(time.time()))
        separator = '&' if '?' in static_url else '?'
        return f"{static_url}{separator}v={version}"
    
    return static_url