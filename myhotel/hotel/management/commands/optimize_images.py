"""
Management command to optimize existing media images
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from myhotel.image_optimizer import ImageOptimizer


class Command(BaseCommand):
    help = 'Optimize existing media images for better performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be optimized without making changes',
        )
        parser.add_argument(
            '--create-webp',
            action='store_true',
            help='Create WebP versions of images',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting image optimization...'))
        
        media_root = settings.MEDIA_ROOT
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        optimized_count = 0
        webp_count = 0
        total_savings = 0

        for root, dirs, files in os.walk(media_root):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in image_extensions:
                    try:
                        # Get original size
                        original_size = os.path.getsize(file_path)
                        
                        if not options['dry_run']:
                            # Optimize image
                            with open(file_path, 'rb') as f:
                                optimized = ImageOptimizer.optimize_image(f)
                            
                            # Save optimized version
                            with open(file_path, 'wb') as f:
                                f.write(optimized.read())
                            
                            # Create WebP version if requested
                            if options['create_webp']:
                                with open(file_path, 'rb') as f:
                                    webp_version = ImageOptimizer.create_webp_version(f)
                                
                                if webp_version:
                                    webp_path = os.path.splitext(file_path)[0] + '.webp'
                                    with open(webp_path, 'wb') as f:
                                        f.write(webp_version.read())
                                    webp_count += 1
                                    self.stdout.write(f"Created WebP: {os.path.basename(webp_path)}")
                        
                        # Get new size
                        new_size = os.path.getsize(file_path) if not options['dry_run'] else original_size
                        
                        if new_size < original_size or options['dry_run']:
                            optimized_count += 1
                            savings = original_size - new_size
                            total_savings += savings
                            reduction = ((original_size - new_size) / original_size) * 100
                            
                            status = "Would optimize" if options['dry_run'] else "Optimized"
                            self.stdout.write(
                                f"{status} {file}: {reduction:.1f}% reduction "
                                f"({self.format_bytes(original_size)} → {self.format_bytes(new_size)})"
                            )
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Error processing {file}: {e}")
                        )

        # Summary
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nDry run complete. Would optimize {optimized_count} images, "
                    f"saving approximately {self.format_bytes(total_savings)}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nOptimization complete! Optimized {optimized_count} images, "
                    f"saved {self.format_bytes(total_savings)}"
                )
            )
            if webp_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f"Created {webp_count} WebP versions")
                )

    def format_bytes(self, bytes_size):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"