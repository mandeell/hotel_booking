import os
import gzip
import hashlib
from io import BytesIO
from django.conf import settings
from django.http import Http404, HttpResponse
from django.utils._os import safe_join
from django.core.exceptions import SuspiciousOperation
from django.utils.cache import get_conditional_response
from django.utils.http import http_date
from django.views.static import was_modified_since


class MediaFilesMiddleware:
    """
    Enhanced middleware to serve optimized media files in production
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
        Serve optimized media files with compression and caching
        """
        try:
            # Get the file path relative to MEDIA_URL
            relative_path = request.path[len(settings.MEDIA_URL):]
            
            # Build the full file path
            file_path = safe_join(settings.MEDIA_ROOT, relative_path)
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise Http404("Media file not found")
            
            # Get file stats
            stat = os.stat(file_path)
            
            # Check if client has cached version
            if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                                    stat.st_mtime, stat.st_size):
                return HttpResponse(status=304)
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Determine content type
            content_type = self.get_content_type(file_path)
            
            # Create response
            response = HttpResponse(file_content, content_type=content_type)
            
            # Add optimization headers
            self.add_optimization_headers(response, stat, file_path)
            
            # Apply compression for suitable files
            if self.should_compress(file_path, request):
                response = self.compress_response(response, request)
            
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
    
    def add_optimization_headers(self, response, stat, file_path):
        """
        Add performance optimization headers
        """
        # Cache headers
        response['Cache-Control'] = 'public, max-age=31536000, immutable'  # 1 year
        response['Last-Modified'] = http_date(stat.st_mtime)
        
        # ETag for better caching
        etag = hashlib.md5(f"{stat.st_mtime}-{stat.st_size}".encode()).hexdigest()
        response['ETag'] = f'"{etag}"'
        
        # Add Vary header for compression
        response['Vary'] = 'Accept-Encoding'
        
        # Security headers for images
        if self.is_image(file_path):
            response['X-Content-Type-Options'] = 'nosniff'
    
    def should_compress(self, file_path, request):
        """
        Determine if file should be compressed
        """
        # Don't compress already compressed formats
        compressed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.zip', '.gz'}
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Check if client accepts gzip
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        
        return (file_ext not in compressed_extensions and 
                'gzip' in accept_encoding and
                os.path.getsize(file_path) > 1024)  # Only compress files > 1KB
    
    def compress_response(self, response, request):
        """
        Apply gzip compression to response
        """
        try:
            # Compress content
            compressed_content = BytesIO()
            with gzip.GzipFile(fileobj=compressed_content, mode='wb') as gz_file:
                gz_file.write(response.content)
            
            # Create new response with compressed content
            compressed_response = HttpResponse(
                compressed_content.getvalue(),
                content_type=response['Content-Type']
            )
            
            # Copy headers
            for header, value in response.items():
                compressed_response[header] = value
            
            # Add compression headers
            compressed_response['Content-Encoding'] = 'gzip'
            compressed_response['Content-Length'] = len(compressed_response.content)
            
            return compressed_response
        except Exception:
            # Return original response if compression fails
            return response
    
    def is_image(self, file_path):
        """
        Check if file is an image
        """
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.tiff'}
        return os.path.splitext(file_path)[1].lower() in image_extensions