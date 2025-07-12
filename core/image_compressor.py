from PIL import Image
import io
import logging
import psutil
import os
from core.error_handler import handle_errors, ErrorCode, ImageProcessingError, MemoryError
from core.performance_optimizer import performance_optimizer, performance_timer, memory_efficient

logger = logging.getLogger(__name__)


class ImageCompressor:
    def __init__(self, target_scale=0.5, format='PNG'):
        """
        Initialize ImageCompressor with configurable compression settings.
        
        Args:
            target_scale (float): Scale factor for resizing (0.0 to 1.0)
            format (str): Output format ('PNG', 'JPEG', 'WEBP')
        """
        self.target_scale = target_scale
        self.format = format
        
        # Memory and performance constraints
        self.max_image_size = 50 * 1024 * 1024  # 50MB max input size
        self.max_pixels = 8000 * 8000  # 8K max resolution
        self.memory_threshold = 100 * 1024 * 1024  # 100MB available memory required
        
        # Validate parameters
        if not 0.0 < target_scale <= 1.0:
            raise ValueError("target_scale must be between 0.0 and 1.0")
        
        if format not in ['PNG', 'JPEG', 'WEBP']:
            raise ValueError("format must be PNG, JPEG, or WEBP")
    
    @handle_errors(ErrorCode.IMAGE_COMPRESS_ERROR, "image compression", return_on_error=None)
    @performance_timer
    @memory_efficient
    def compress(self, image_data):
        """
        Compress image data by scaling and optimizing format.
        
        Args:
            image_data (bytes): Original image data
            
        Returns:
            bytes: Compressed image data, or original data if compression fails
        """
        # Pre-compression validation - return original data if validation fails
        try:
            self._validate_input(image_data)
        except Exception as e:
            logger.warning(f"Input validation failed: {e}, returning original data")
            return image_data
        
        # Use performance optimizer for large images or memory-constrained situations
        if len(image_data) > 5 * 1024 * 1024:  # 5MB threshold
            logger.info("Using performance optimizer for large image")
            return performance_optimizer.optimize_image_processing(
                image_data, self.target_scale, self.format
            )
        
        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Validate image constraints
            self._validate_image_constraints(image)
            
            # Handle RGBA for PNG, convert to RGB for other formats
            if self.format != 'PNG' and image.mode == 'RGBA':
                # Create white background for transparency
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                image = background
            
            # Calculate new dimensions
            new_width = int(image.width * self.target_scale)
            new_height = int(image.height * self.target_scale)
            new_size = (new_width, new_height)
            
            # Ensure minimum dimensions
            if new_width < 1 or new_height < 1:
                new_size = (max(1, new_width), max(1, new_height))
            
            # Resize with high-quality resampling
            resized = image.resize(new_size, Image.LANCZOS)
            
            # Prepare output buffer
            output = io.BytesIO()
            
            # Configure save parameters based on format
            save_kwargs = {'format': self.format, 'optimize': True}
            
            if self.format == 'PNG':
                save_kwargs['compress_level'] = 6  # Balance between speed and size
            elif self.format == 'JPEG':
                save_kwargs['quality'] = 85  # Good quality while maintaining compression
                save_kwargs['progressive'] = True
            elif self.format == 'WEBP':
                save_kwargs['quality'] = 85
                save_kwargs['method'] = 6  # Better compression
            
            # Save compressed image
            resized.save(output, **save_kwargs)
            compressed_data = output.getvalue()
            
            # Validate output size
            if len(compressed_data) > self.max_image_size:
                logger.warning("Compressed image exceeds size limit, using more aggressive compression")
                compressed_data = self._aggressive_compress(resized)
            
            # Log compression stats
            original_size = len(image_data)
            compressed_size = len(compressed_data)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            logger.info(f"Compression: {original_size} -> {compressed_size} bytes "
                       f"({compression_ratio:.1f}% reduction)")
            
            return compressed_data
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            # Return original data as fallback
            return image_data
    
    def _validate_input(self, image_data):
        """Validate input image data."""
        if not image_data:
            logger.warning("Empty image data provided")
            # For empty data, we'll let the caller handle it by returning the original data
            return
        
        if len(image_data) > self.max_image_size:
            raise ImageProcessingError(
                f"Image too large: {len(image_data)} bytes (max: {self.max_image_size})",
                ErrorCode.IMAGE_TOO_LARGE
            )
        
        # Check available memory
        memory_info = psutil.virtual_memory()
        if memory_info.available < self.memory_threshold:
            raise MemoryError(
                f"Insufficient memory: {memory_info.available} bytes available",
                ErrorCode.OUT_OF_MEMORY
            )
    
    def _validate_image_constraints(self, image):
        """Validate image constraints."""
        total_pixels = image.width * image.height
        
        if total_pixels > self.max_pixels:
            raise ImageProcessingError(
                f"Image too large: {total_pixels} pixels (max: {self.max_pixels})",
                ErrorCode.IMAGE_TOO_LARGE
            )
        
        # Estimate memory usage (rough approximation)
        estimated_memory = total_pixels * 4  # 4 bytes per pixel (RGBA)
        memory_info = psutil.virtual_memory()
        
        if estimated_memory > memory_info.available * 0.5:  # Use max 50% of available memory
            raise MemoryError(
                f"Image would use too much memory: {estimated_memory} bytes",
                ErrorCode.MEMORY_ALLOCATION_ERROR
            )
    
    def _aggressive_compress(self, image):
        """Apply more aggressive compression when needed."""
        try:
            output = io.BytesIO()
            
            if self.format == 'PNG':
                # Use maximum compression level
                image.save(output, format='PNG', optimize=True, compress_level=9)
            elif self.format == 'JPEG':
                # Reduce quality for smaller size
                image.save(output, format='JPEG', quality=60, optimize=True, progressive=True)
            elif self.format == 'WEBP':
                # Use higher compression
                image.save(output, format='WEBP', quality=60, method=6)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Aggressive compression failed: {e}")
            # Final fallback - convert to JPEG with low quality
            output = io.BytesIO()
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            image.save(output, format='JPEG', quality=30, optimize=True)
            return output.getvalue()
    
    def get_compression_info(self, image_data):
        """
        Get compression information without actually compressing.
        
        Args:
            image_data (bytes): Original image data
            
        Returns:
            dict: Information about the image and expected compression
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            new_width = int(image.width * self.target_scale)
            new_height = int(image.height * self.target_scale)
            
            return {
                'original_size': len(image_data),
                'original_dimensions': (image.width, image.height),
                'target_dimensions': (new_width, new_height),
                'scale_factor': self.target_scale,
                'format': self.format,
                'mode': image.mode
            }
            
        except Exception as e:
            logger.error(f"Failed to get image info: {e}")
            return None