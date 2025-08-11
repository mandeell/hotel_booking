import os
import time
from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe

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


@register.simple_tag
def optimized_image(image_path, alt_text="", css_class="", width=None, height=None, lazy=True):
    """
    Generate optimized image tag with lazy loading and WebP support
    
    Usage:
        {% optimized_image "rooms/1.jpg" "Hotel Room" "img-fluid" 800 600 %}
    """
    if not image_path:
        return ""
    
    # Build media URL with versioning
    media_url = media_with_version(image_path)
    
    # Check for WebP version
    webp_path = os.path.splitext(image_path)[0] + '.webp'
    webp_full_path = os.path.join(settings.MEDIA_ROOT, webp_path)
    
    # Build attributes
    attributes = []
    if css_class:
        attributes.append(f'class="{css_class}"')
    if alt_text:
        attributes.append(f'alt="{alt_text}"')
    if width:
        attributes.append(f'width="{width}"')
    if height:
        attributes.append(f'height="{height}"')
    
    # Add lazy loading
    if lazy:
        attributes.append('loading="lazy"')
        attributes.append('decoding="async"')
    
    attrs_str = ' '.join(attributes)
    
    # Generate picture element with WebP support if WebP exists
    if os.path.exists(webp_full_path):
        webp_url = media_with_version(webp_path)
        html = f'''
        <picture>
            <source srcset="{webp_url}" type="image/webp">
            <img src="{media_url}" {attrs_str}>
        </picture>
        '''
    else:
        html = f'<img src="{media_url}" {attrs_str}>'
    
    return mark_safe(html.strip())


@register.simple_tag
def responsive_image(image_path, alt_text="", css_class="", lazy=True):
    """
    Generate responsive image with lazy loading
    
    Usage:
        {% responsive_image "rooms/1.jpg" "Hotel Room" "img-fluid" %}
    """
    if not image_path:
        return ""
    
    # Build media URL with versioning
    media_url = media_with_version(image_path)
    
    # Build attributes
    attributes = []
    if css_class:
        attributes.append(f'class="{css_class}"')
    if alt_text:
        attributes.append(f'alt="{alt_text}"')
    
    # Add lazy loading
    if lazy:
        attributes.append('loading="lazy"')
        attributes.append('decoding="async"')
    
    attrs_str = ' '.join(attributes)
    
    html = f'<img src="{media_url}" {attrs_str}>'
    
    return mark_safe(html)


@register.filter
def file_size(file_path):
    """
    Get human-readable file size
    """
    try:
        if hasattr(file_path, 'size'):
            size = file_path.size
        else:
            full_path = os.path.join(settings.MEDIA_ROOT, str(file_path))
            size = os.path.getsize(full_path)
        
        # Convert to human readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except:
        return "Unknown"


@register.inclusion_tag('hotel/lazy_loading_script.html', takes_context=True)
def lazy_loading_script(context):
    """
    Include lazy loading JavaScript for background images
    """
    return {'request': context.get('request')}