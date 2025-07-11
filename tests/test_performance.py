import pytest
import time
import io
from PIL import Image
import numpy as np
from unittest.mock import patch, Mock
from core.image_compressor import ImageCompressor
from core.performance_optimizer import PerformanceOptimizer, MemoryMonitor, performance_timer, memory_efficient
from core.error_handler import check_system_resources


class TestPerformanceOptimizer:
    """Test performance optimization functionality."""
    
    def create_test_image(self, size=(1000, 1000), mode='RGB'):
        """Create a test image for performance testing."""
        image = Image.new(mode, size, color=(255, 0, 0))
        
        # Add some complexity to make it more realistic
        pixels = image.load()
        for i in range(0, size[0], 10):
            for j in range(0, size[1], 10):
                pixels[i, j] = (0, 255, 0)
        
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def test_performance_optimizer_init(self):
        """Test performance optimizer initialization."""
        optimizer = PerformanceOptimizer()
        
        assert optimizer.thread_pool is not None
        assert optimizer.memory_monitor is not None
        assert optimizer.performance_stats['total_operations'] == 0
        assert optimizer.performance_stats['average_time'] == 0.0
    
    def test_determine_optimizations_small_image(self):
        """Test optimization determination for small images."""
        optimizer = PerformanceOptimizer()
        small_image_data = self.create_test_image(size=(100, 100))
        
        optimizations = optimizer._determine_optimizations(small_image_data, 0.5)
        
        # Small image should not trigger heavy optimizations
        assert not optimizations['use_progressive_scaling']
        assert not optimizations['use_memory_efficient']
    
    def test_determine_optimizations_large_image(self):
        """Test optimization determination for large images."""
        optimizer = PerformanceOptimizer()
        
        # Create a large image data (simulate 10MB+)
        large_image_data = b'0' * (15 * 1024 * 1024)  # 15MB of dummy data
        
        optimizations = optimizer._determine_optimizations(large_image_data, 0.5)
        
        # Large image should trigger progressive scaling
        assert optimizations['use_progressive_scaling']
    
    def test_determine_optimizations_heavy_downscaling(self):
        """Test optimization determination for heavy downscaling."""
        optimizer = PerformanceOptimizer()
        image_data = self.create_test_image(size=(1000, 1000))
        
        optimizations = optimizer._determine_optimizations(image_data, 0.2)  # 20% scale
        
        # Heavy downscaling should trigger parallel processing
        assert optimizations['use_parallel_processing']
    
    def test_standard_process(self):
        """Test standard image processing."""
        optimizer = PerformanceOptimizer()
        image_data = self.create_test_image(size=(200, 200))
        
        result = optimizer._standard_process(image_data, 0.5, 'PNG')
        
        assert result is not None
        assert len(result) > 0
        
        # Verify result is a valid image
        result_image = Image.open(io.BytesIO(result))
        assert result_image.size == (100, 100)  # 50% of 200x200
    
    def test_memory_efficient_process(self):
        """Test memory-efficient processing."""
        optimizer = PerformanceOptimizer()
        image_data = self.create_test_image(size=(500, 500))
        
        result = optimizer._memory_efficient_process(image_data, 0.5, 'PNG')
        
        assert result is not None
        assert len(result) > 0
        
        # Verify result is a valid image
        result_image = Image.open(io.BytesIO(result))
        assert result_image.size == (250, 250)  # 50% of 500x500
    
    def test_progressive_scale(self):
        """Test progressive scaling."""
        optimizer = PerformanceOptimizer()
        image_data = self.create_test_image(size=(1000, 1000))
        
        result = optimizer._progressive_scale(image_data, 0.25, 'PNG')
        
        assert result is not None
        assert len(result) > 0
        
        # Verify result is a valid image
        result_image = Image.open(io.BytesIO(result))
        assert result_image.size == (250, 250)  # 25% of 1000x1000
    
    def test_optimize_image_processing(self):
        """Test complete image processing optimization."""
        optimizer = PerformanceOptimizer()
        image_data = self.create_test_image(size=(300, 300))
        
        result = optimizer.optimize_image_processing(image_data, 0.5, 'PNG')
        
        assert result is not None
        assert len(result) > 0
        
        # Check that statistics were updated
        assert optimizer.performance_stats['total_operations'] == 1
        assert optimizer.performance_stats['average_time'] > 0
    
    def test_performance_stats_update(self):
        """Test performance statistics updating."""
        optimizer = PerformanceOptimizer()
        
        # Simulate processing
        optimizer._update_stats(0.5, 1000, 500)
        
        assert optimizer.performance_stats['total_operations'] == 1
        assert optimizer.performance_stats['average_time'] == 0.5
        assert len(optimizer.performance_stats['memory_usage']) == 1
    
    def test_get_performance_stats(self):
        """Test getting performance statistics."""
        optimizer = PerformanceOptimizer()
        
        # Process an image to generate stats
        image_data = self.create_test_image(size=(100, 100))
        optimizer.optimize_image_processing(image_data, 0.5, 'PNG')
        
        stats = optimizer.get_performance_stats()
        
        assert 'total_operations' in stats
        assert 'average_time' in stats
        assert 'memory_usage' in stats
        assert stats['total_operations'] == 1
    
    def test_reset_stats(self):
        """Test resetting performance statistics."""
        optimizer = PerformanceOptimizer()
        
        # Generate some stats
        optimizer._update_stats(0.5, 1000, 500)
        assert optimizer.performance_stats['total_operations'] == 1
        
        # Reset stats
        optimizer.reset_stats()
        
        assert optimizer.performance_stats['total_operations'] == 0
        assert optimizer.performance_stats['average_time'] == 0.0
        assert optimizer.performance_stats['memory_usage'] == []
    
    def test_cleanup(self):
        """Test cleanup of performance optimizer."""
        optimizer = PerformanceOptimizer()
        
        # Should not raise any exceptions
        optimizer.cleanup()


class TestMemoryMonitor:
    """Test memory monitoring functionality."""
    
    def test_memory_monitor_init(self):
        """Test memory monitor initialization."""
        monitor = MemoryMonitor()
        
        assert not monitor.monitoring
        assert monitor.monitor_thread is None
        assert monitor.memory_threshold == 0.85
        assert monitor.callbacks == []
    
    def test_add_callback(self):
        """Test adding memory warning callbacks."""
        monitor = MemoryMonitor()
        callback = Mock()
        
        monitor.add_callback(callback)
        
        assert len(monitor.callbacks) == 1
        assert monitor.callbacks[0] == callback
    
    def test_start_stop_monitoring(self):
        """Test starting and stopping memory monitoring."""
        monitor = MemoryMonitor()
        
        # Start monitoring
        monitor.start()
        assert monitor.monitoring
        assert monitor.monitor_thread is not None
        
        # Stop monitoring
        monitor.stop()
        assert not monitor.monitoring


class TestPerformanceDecorators:
    """Test performance decorators."""
    
    def test_performance_timer_decorator(self):
        """Test performance timer decorator."""
        
        @performance_timer
        def test_function():
            time.sleep(0.1)
            return "test"
        
        # Should not raise any exceptions and should return the result
        result = test_function()
        assert result == "test"
    
    def test_performance_timer_decorator_with_exception(self):
        """Test performance timer decorator with exception."""
        
        @performance_timer
        def test_function():
            raise ValueError("Test error")
        
        # Should re-raise the exception
        with pytest.raises(ValueError, match="Test error"):
            test_function()
    
    def test_memory_efficient_decorator(self):
        """Test memory efficient decorator."""
        
        @memory_efficient
        def test_function():
            return "test"
        
        # Should not raise any exceptions and should return the result
        result = test_function()
        assert result == "test"
    
    def test_memory_efficient_decorator_with_exception(self):
        """Test memory efficient decorator with exception."""
        
        @memory_efficient
        def test_function():
            raise ValueError("Test error")
        
        # Should re-raise the exception
        with pytest.raises(ValueError, match="Test error"):
            test_function()


class TestImageCompressorPerformance:
    """Test image compressor performance integration."""
    
    def create_test_image(self, size=(1000, 1000), mode='RGB'):
        """Create a test image for performance testing."""
        image = Image.new(mode, size, color=(255, 0, 0))
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def test_compressor_with_small_image(self):
        """Test compressor performance with small image."""
        compressor = ImageCompressor(target_scale=0.5)
        small_image_data = self.create_test_image(size=(200, 200))
        
        start_time = time.time()
        result = compressor.compress(small_image_data)
        end_time = time.time()
        
        assert result is not None
        assert len(result) > 0
        assert end_time - start_time < 5.0  # Should complete within 5 seconds
    
    def test_compressor_with_large_image_uses_optimizer(self):
        """Test that compressor uses optimizer for large images."""
        compressor = ImageCompressor(target_scale=0.5)
        
        # Create a large image (simulate 6MB)
        large_image_data = b'0' * (6 * 1024 * 1024)
        
        with patch('core.image_compressor.performance_optimizer') as mock_optimizer:
            mock_optimizer.optimize_image_processing.return_value = b'compressed_data'
            
            result = compressor.compress(large_image_data)
            
            # Should have called the performance optimizer
            mock_optimizer.optimize_image_processing.assert_called_once()
            assert result == b'compressed_data'
    
    def test_compressor_performance_with_various_scales(self):
        """Test compressor performance with different scale factors."""
        compressor = ImageCompressor()
        image_data = self.create_test_image(size=(500, 500))
        
        scales = [0.25, 0.5, 0.75, 1.0]
        
        for scale in scales:
            compressor.target_scale = scale
            
            start_time = time.time()
            result = compressor.compress(image_data)
            end_time = time.time()
            
            assert result is not None
            assert len(result) > 0
            assert end_time - start_time < 3.0  # Should complete within 3 seconds
    
    def test_compressor_memory_usage(self):
        """Test compressor memory usage."""
        compressor = ImageCompressor(target_scale=0.5)
        image_data = self.create_test_image(size=(1000, 1000))
        
        # Get initial memory usage
        initial_memory = check_system_resources()['memory']['percent']
        
        # Process image
        result = compressor.compress(image_data)
        
        # Check memory usage after processing
        final_memory = check_system_resources()['memory']['percent']
        
        assert result is not None
        # Memory usage should not increase dramatically (allow for some variance)
        assert final_memory - initial_memory < 20  # Less than 20% increase


class TestSystemResources:
    """Test system resource monitoring."""
    
    def test_check_system_resources(self):
        """Test checking system resources."""
        resources = check_system_resources()
        
        assert 'memory' in resources
        assert 'disk' in resources
        assert 'cpu' in resources
        
        # Check memory info
        assert 'total' in resources['memory']
        assert 'available' in resources['memory']
        assert 'percent' in resources['memory']
        assert 'free_mb' in resources['memory']
        
        # Check disk info
        assert 'total' in resources['disk']
        assert 'free' in resources['disk']
        assert 'percent' in resources['disk']
        assert 'free_gb' in resources['disk']
        
        # Check CPU info
        assert 'percent' in resources['cpu']
    
    def test_system_resources_values(self):
        """Test that system resource values are reasonable."""
        resources = check_system_resources()
        
        # Memory values should be positive
        assert resources['memory']['total'] > 0
        assert resources['memory']['available'] > 0
        assert 0 <= resources['memory']['percent'] <= 100
        
        # Disk values should be positive
        assert resources['disk']['total'] > 0
        assert resources['disk']['free'] > 0
        assert 0 <= resources['disk']['percent'] <= 100
        
        # CPU percent should be reasonable
        assert 0 <= resources['cpu']['percent'] <= 100


class TestPerformanceBenchmarks:
    """Performance benchmarks for the application."""
    
    def create_test_image(self, size=(1000, 1000), mode='RGB'):
        """Create a test image for benchmarking."""
        image = Image.new(mode, size, color=(255, 0, 0))
        
        # Add some complexity
        pixels = image.load()
        for i in range(0, size[0], 50):
            for j in range(0, size[1], 50):
                pixels[i, j] = (0, 255, 0)
        
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def test_compression_speed_benchmark(self):
        """Benchmark compression speed for different image sizes."""
        compressor = ImageCompressor(target_scale=0.5)
        
        sizes = [(100, 100), (500, 500), (1000, 1000)]
        
        for size in sizes:
            image_data = self.create_test_image(size=size)
            
            start_time = time.time()
            result = compressor.compress(image_data)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Log benchmark results
            print(f"Size {size}: {processing_time:.3f}s, "
                  f"Input: {len(image_data)} bytes, "
                  f"Output: {len(result)} bytes, "
                  f"Ratio: {(1 - len(result) / len(image_data)) * 100:.1f}%")
            
            # Reasonable performance expectations
            if size == (100, 100):
                assert processing_time < 1.0  # Small image should be fast
            elif size == (500, 500):
                assert processing_time < 3.0  # Medium image
            elif size == (1000, 1000):
                assert processing_time < 10.0  # Large image
    
    def test_memory_efficiency_benchmark(self):
        """Benchmark memory efficiency."""
        compressor = ImageCompressor(target_scale=0.5)
        
        # Get initial memory
        initial_resources = check_system_resources()
        initial_memory = initial_resources['memory']['percent']
        
        # Process multiple images
        for i in range(5):
            image_data = self.create_test_image(size=(800, 800))
            result = compressor.compress(image_data)
            assert result is not None
        
        # Check final memory
        final_resources = check_system_resources()
        final_memory = final_resources['memory']['percent']
        
        # Memory usage should not increase significantly
        memory_increase = final_memory - initial_memory
        print(f"Memory increase: {memory_increase:.1f}%")
        
        # Should not use more than 10% additional memory
        assert memory_increase < 10.0