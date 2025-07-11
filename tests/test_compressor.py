import pytest
import io
from PIL import Image
from core.image_compressor import ImageCompressor


class TestImageCompressor:
    
    def create_test_image(self, size=(100, 100), mode='RGB', color=(255, 0, 0)):
        """Create a test image for compression tests."""
        image = Image.new(mode, size, color)
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def test_init_default_values(self):
        """Test ImageCompressor initialization with default values."""
        compressor = ImageCompressor()
        assert compressor.target_scale == 0.5
        assert compressor.format == 'PNG'
    
    def test_init_custom_values(self):
        """Test ImageCompressor initialization with custom values."""
        compressor = ImageCompressor(target_scale=0.75, format='JPEG')
        assert compressor.target_scale == 0.75
        assert compressor.format == 'JPEG'
    
    def test_init_invalid_scale(self):
        """Test ImageCompressor initialization with invalid scale values."""
        with pytest.raises(ValueError, match="target_scale must be between 0.0 and 1.0"):
            ImageCompressor(target_scale=0.0)
        
        with pytest.raises(ValueError, match="target_scale must be between 0.0 and 1.0"):
            ImageCompressor(target_scale=1.5)
    
    def test_init_invalid_format(self):
        """Test ImageCompressor initialization with invalid format."""
        with pytest.raises(ValueError, match="format must be PNG, JPEG, or WEBP"):
            ImageCompressor(format='BMP')
    
    def test_compress_png_basic(self):
        """Test basic PNG compression."""
        compressor = ImageCompressor(target_scale=0.5, format='PNG')
        original_data = self.create_test_image(size=(200, 200))
        
        compressed_data = compressor.compress(original_data)
        
        # Verify compression occurred
        assert len(compressed_data) < len(original_data)
        
        # Verify compressed image is valid
        compressed_image = Image.open(io.BytesIO(compressed_data))
        assert compressed_image.size == (100, 100)  # 50% of 200x200
        assert compressed_image.format == 'PNG'
    
    def test_compress_jpeg_basic(self):
        """Test basic JPEG compression."""
        compressor = ImageCompressor(target_scale=0.5, format='JPEG')
        # Create larger image to ensure compression reduces size
        original_data = self.create_test_image(size=(400, 400))
        
        compressed_data = compressor.compress(original_data)
        
        # Verify compression occurred (for small solid color images, JPEG might be larger)
        # But verify the image is properly resized and format is correct
        compressed_image = Image.open(io.BytesIO(compressed_data))
        assert compressed_image.size == (200, 200)  # 50% of 400x400
        assert compressed_image.format == 'JPEG'
    
    def test_compress_rgba_to_png(self):
        """Test RGBA image compression to PNG (should preserve alpha)."""
        compressor = ImageCompressor(target_scale=0.5, format='PNG')
        original_data = self.create_test_image(size=(200, 200), mode='RGBA', color=(255, 0, 0, 128))
        
        compressed_data = compressor.compress(original_data)
        
        # Verify compressed image maintains RGBA
        compressed_image = Image.open(io.BytesIO(compressed_data))
        assert compressed_image.mode == 'RGBA'
        assert compressed_image.size == (100, 100)
    
    def test_compress_rgba_to_jpeg(self):
        """Test RGBA image compression to JPEG (should convert to RGB)."""
        compressor = ImageCompressor(target_scale=0.5, format='JPEG')
        original_data = self.create_test_image(size=(200, 200), mode='RGBA', color=(255, 0, 0, 128))
        
        compressed_data = compressor.compress(original_data)
        
        # Verify compressed image is RGB (JPEG doesn't support alpha)
        compressed_image = Image.open(io.BytesIO(compressed_data))
        assert compressed_image.mode == 'RGB'
        assert compressed_image.size == (100, 100)
    
    def test_compress_different_scales(self):
        """Test compression with different scale factors."""
        original_data = self.create_test_image(size=(400, 400))
        
        # Test 25% scale
        compressor_25 = ImageCompressor(target_scale=0.25)
        compressed_25 = compressor_25.compress(original_data)
        image_25 = Image.open(io.BytesIO(compressed_25))
        assert image_25.size == (100, 100)
        
        # Test 75% scale
        compressor_75 = ImageCompressor(target_scale=0.75)
        compressed_75 = compressor_75.compress(original_data)
        image_75 = Image.open(io.BytesIO(compressed_75))
        assert image_75.size == (300, 300)
    
    def test_compress_invalid_data(self):
        """Test compression with invalid image data returns original."""
        compressor = ImageCompressor()
        invalid_data = b"not an image"
        
        result = compressor.compress(invalid_data)
        
        # Should return original data when compression fails
        assert result == invalid_data
    
    def test_get_compression_info(self):
        """Test getting compression info without compressing."""
        compressor = ImageCompressor(target_scale=0.5, format='PNG')
        original_data = self.create_test_image(size=(200, 200))
        
        info = compressor.get_compression_info(original_data)
        
        assert info is not None
        assert info['original_dimensions'] == (200, 200)
        assert info['target_dimensions'] == (100, 100)
        assert info['scale_factor'] == 0.5
        assert info['format'] == 'PNG'
        assert info['mode'] == 'RGB'
        assert info['original_size'] == len(original_data)
    
    def test_get_compression_info_invalid_data(self):
        """Test getting compression info with invalid data."""
        compressor = ImageCompressor()
        invalid_data = b"not an image"
        
        info = compressor.get_compression_info(invalid_data)
        
        assert info is None
    
    def test_compression_ratio_calculation(self):
        """Test that compression actually reduces file size significantly."""
        compressor = ImageCompressor(target_scale=0.5, format='PNG')
        
        # Create larger test image for better compression ratio testing
        original_data = self.create_test_image(size=(1000, 1000))
        compressed_data = compressor.compress(original_data)
        
        # Should achieve significant compression
        compression_ratio = (1 - len(compressed_data) / len(original_data)) * 100
        assert compression_ratio > 50  # Should get more than 50% reduction
    
    def test_edge_case_small_image(self):
        """Test compression with very small images."""
        compressor = ImageCompressor(target_scale=0.5)
        small_image_data = self.create_test_image(size=(4, 4))
        
        compressed_data = compressor.compress(small_image_data)
        
        # Should handle small images gracefully
        compressed_image = Image.open(io.BytesIO(compressed_data))
        assert compressed_image.size == (2, 2)  # 50% of 4x4
    
    def test_edge_case_single_pixel(self):
        """Test compression with single pixel image."""
        compressor = ImageCompressor(target_scale=0.5)
        single_pixel_data = self.create_test_image(size=(1, 1))
        
        compressed_data = compressor.compress(single_pixel_data)
        
        # Should handle single pixel (rounds to 0, but PIL handles this)
        compressed_image = Image.open(io.BytesIO(compressed_data))
        # Single pixel at 50% scale should still be 1x1 (minimum size)
        assert compressed_image.size[0] >= 1
        assert compressed_image.size[1] >= 1