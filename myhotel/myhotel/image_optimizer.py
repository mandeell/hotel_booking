"""
Image optimization utilities for better website performance
"""
import os
import io
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings


class ImageOptimizer:
    """
    Utility class for optimizing images
    """
    
    # Default optimization settings
    DEFAULT_QUALITY = 85
    DEFAULT_MAX_WIDTH = 1920
    DEFAULT_MAX_HEIGHT = 1080
    THUMBNAIL_SIZE = (300, 300)
    
    # WebP quality settings
    WEBP_QUALITY = 80
    
    @classmethod
    def optimize_image(cls, image_file, max_width=None, max_height=None, quality=None):
        """
        Optimize an image file by resizing and compressing
        
        Args:
            image_file: Django file object or PIL Image
            max_width: Maximum width (default: 1920)
            max_height: Maximum height (default: 1080)
            quality: JPEG quality (default: 85)
            
        Returns:
            Optimized image as ContentFile
        """
        max_width = max_width or cls.DEFAULT_MAX_WIDTH
        max_height = max_height or cls.DEFAULT_MAX_HEIGHT
        quality = quality or cls.DEFAULT_QUALITY
        
        try:
            # Open image
            if hasattr(image_file, 'read'):
                image = Image.open(image_file)
            else:
                image = image_file
            
            # Convert RGBA to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Auto-orient image based on EXIF data
            image = ImageOps.exif_transpose(image)
            
            # Resize if necessary
            original_width, original_height = image.size
            if original_width > max_width or original_height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            output = io.BytesIO()
            
            # Determine format
            format_type = 'JPEG'
            if hasattr(image_file, 'name'):
                ext = os.path.splitext(image_file.name)[1].lower()
                if ext == '.png':
                    format_type = 'PNG'
            
            # Save with optimization
            save_kwargs = {'format': format_type, 'optimize': True}
            if format_type == 'JPEG':
                save_kwargs['quality'] = quality
                save_kwargs['progressive'] = True
            
            image.save(output, **save_kwargs)
            output.seek(0)
            
            return ContentFile(output.getvalue())
            
        except Exception as e:
            print(f"Error optimizing image: {e}")
            return image_file
    
    @classmethod
    def create_webp_version(cls, image_file, quality=None):
        """
        Create WebP version of an image
        
        Args:
            image_file: Django file object or PIL Image
            quality: WebP quality (default: 80)
            
        Returns:
            WebP image as ContentFile
        """
        quality = quality or cls.WEBP_QUALITY
        
        try:
            # Open image
            if hasattr(image_file, 'read'):
                image = Image.open(image_file)
            else:
                image = image_file
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                if image.mode == 'P':
                    image = image.convert('RGBA')
                # For WebP, we can keep transparency
                if image.mode != 'RGBA':
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1] if len(image.split()) > 3 else None)
                    image = background
            
            # Auto-orient image
            image = ImageOps.exif_transpose(image)
            
            # Save as WebP
            output = io.BytesIO()
            image.save(output, format='WebP', quality=quality, optimize=True)
            output.seek(0)
            
            return ContentFile(output.getvalue())
            
        except Exception as e:
            print(f"Error creating WebP version: {e}")
            return None
    
    @classmethod
    def create_thumbnail(cls, image_file, size=None):
        """
        Create thumbnail version of an image
        
        Args:
            image_file: Django file object or PIL Image
            size: Tuple of (width, height) for thumbnail
            
        Returns:
            Thumbnail image as ContentFile
        """
        size = size or cls.THUMBNAIL_SIZE
        
        try:
            # Open image
            if hasattr(image_file, 'read'):
                image = Image.open(image_file)
            else:
                image = image_file
            
            # Convert RGBA to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Auto-orient image
            image = ImageOps.exif_transpose(image)
            
            # Create thumbnail
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=cls.DEFAULT_QUALITY, optimize=True)
            output.seek(0)
            
            return ContentFile(output.getvalue())
            
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None
    
    @classmethod
    def get_image_dimensions(cls, image_file):
        """
        Get dimensions of an image file
        
        Args:
            image_file: Django file object or file path
            
        Returns:
            Tuple of (width, height) or None if error
        """
        try:
            if hasattr(image_file, 'read'):
                image = Image.open(image_file)
            else:
                image = Image.open(image_file)
            return image.size
        except Exception:
            return None
    
    @classmethod
    def optimize_existing_media(cls, media_root=None):
        """
        Optimize all existing images in media directory
        
        Args:
            media_root: Path to media directory (default: settings.MEDIA_ROOT)
        """
        media_root = media_root or settings.MEDIA_ROOT
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        optimized_count = 0
        
        for root, dirs, files in os.walk(media_root):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in image_extensions:
                    try:
                        # Get original size
                        original_size = os.path.getsize(file_path)
                        
                        # Optimize image
                        with open(file_path, 'rb') as f:
                            optimized = cls.optimize_image(f)
                        
                        # Save optimized version
                        with open(file_path, 'wb') as f:
                            f.write(optimized.read())
                        
                        # Get new size
                        new_size = os.path.getsize(file_path)
                        
                        if new_size < original_size:
                            optimized_count += 1
                            reduction = ((original_size - new_size) / original_size) * 100
                            print(f"Optimized {file}: {reduction:.1f}% reduction")
                        
                    except Exception as e:
                        print(f"Error optimizing {file}: {e}")
        
        print(f"Optimization complete. {optimized_count} images optimized.")


def optimize_uploaded_image(sender, instance, **kwargs):
    """
    Signal handler to automatically optimize uploaded images
    """
    # This can be connected to post_save signals for models with ImageFields
    for field in instance._meta.fields:
        if hasattr(field, 'upload_to') and hasattr(instance, field.name):
            image_field = getattr(instance, field.name)
            if image_field and hasattr(image_field, 'file'):
                try:
                    # Optimize the image
                    optimized = ImageOptimizer.optimize_image(image_field.file)
                    
                    # Save optimized version
                    image_field.save(
                        image_field.name,
                        optimized,
                        save=False
                    )
                    
                    # Create WebP version if enabled
                    webp_version = ImageOptimizer.create_webp_version(image_field.file)
                    if webp_version:
                        webp_name = os.path.splitext(image_field.name)[0] + '.webp'
                        default_storage.save(webp_name, webp_version)
                        
                except Exception as e:
                    print(f"Error in automatic image optimization: {e}")