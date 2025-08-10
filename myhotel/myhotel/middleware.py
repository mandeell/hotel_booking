import os
from django.conf import settings
from django.http import Http404, HttpResponse
from django.utils._os import safe_join
from django.core.exceptions import SuspiciousOperation


class MediaFilesMiddleware:
    """
    Middleware to serve media files in production when DEBUG=False
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if this is a media file request
        if request.path.startswith(settings.MEDIA_URL):
            return self.serve_media(request)
        
        response = self.get_response(request)
        return response

    def serve_media(self, request):
        """
        Serve media files in production
        """
        try:
            # Get the file path relative to MEDIA_URL
            relative_path = request.path[len(settings.MEDIA_URL):]
            
            # Build the full file path
            file_path = safe_join(settings.MEDIA_ROOT, relative_path)
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise Http404("Media file not found")
            
            # Read and serve the file
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Determine content type based on file extension
            content_type = self.get_content_type(file_path)
            
            response = HttpResponse(file_content, content_type=content_type)
            
            # Add cache headers for better performance
            response['Cache-Control'] = 'public, max-age=31536000'  # 1 year
            
            return response
            
        except (ValueError, SuspiciousOperation, Http404):
            raise Http404("Media file not found")

    def get_content_type(self, file_path):
        """
        Determine content type based on file extension
        """
        import mimetypes
        content_type, _ = mimetypes.guess_type(file_path)
        return content_type or 'application/octet-stream'