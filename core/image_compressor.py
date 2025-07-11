from PIL import Image
import io
import logging

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
        
        # Validate parameters
        if not 0.0 < target_scale <= 1.0:
            raise ValueError("target_scale must be between 0.0 and 1.0")
        
        if format not in ['PNG', 'JPEG', 'WEBP']:
            raise ValueError("format must be PNG, JPEG, or WEBP")
    
    def compress(self, image_data):
        """
        Compress image data by scaling and optimizing format.
        
        Args:
            image_data (bytes): Original image data
            
        Returns:
            bytes: Compressed image data, or original data if compression fails
        """
        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(image_data))
            
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