import logging
import time
import threading
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
import io
import gc
import psutil
from functools import wraps
from core.error_handler import handle_errors, ErrorCode

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """Optimizes performance for image processing operations."""
    
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=2)  # Limit concurrent operations
        self.memory_monitor = MemoryMonitor()
        self.performance_stats = {
            'total_operations': 0,
            'average_time': 0.0,
            'memory_usage': [],
            'optimization_applied': 0
        }
        
    def optimize_image_processing(self, image_data: bytes, target_scale: float, format: str) -> bytes:
        """
        Optimize image processing with performance considerations.
        
        Args:
            image_data: Raw image data
            target_scale: Scale factor for resizing
            format: Output format
            
        Returns:
            Optimized image data
        """
        start_time = time.time()
        
        try:
            # Check if we need to apply optimizations
            optimizations = self._determine_optimizations(image_data, target_scale)
            
            if optimizations['use_progressive_scaling']:
                result = self._progressive_scale(image_data, target_scale, format)
            elif optimizations['use_memory_efficient']:
                result = self._memory_efficient_process(image_data, target_scale, format)
            else:
                result = self._standard_process(image_data, target_scale, format)
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_stats(processing_time, len(image_data), len(result))
            
            return result
            
        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")
            # Fallback to standard processing
            return self._standard_process(image_data, target_scale, format)
    
    def _determine_optimizations(self, image_data: bytes, target_scale: float) -> Dict[str, bool]:
        """Determine which optimizations to apply."""
        optimizations = {
            'use_progressive_scaling': False,
            'use_memory_efficient': False,
            'use_parallel_processing': False
        }
        
        # Check image size
        image_size = len(image_data)
        
        # Large images benefit from progressive scaling
        if image_size > 10 * 1024 * 1024:  # 10MB
            optimizations['use_progressive_scaling'] = True
        
        # Memory-constrained systems need memory-efficient processing
        memory_info = psutil.virtual_memory()
        if memory_info.available < 500 * 1024 * 1024:  # 500MB
            optimizations['use_memory_efficient'] = True
        
        # Very large scale changes benefit from parallel processing
        if target_scale < 0.25:  # Heavy downscaling
            optimizations['use_parallel_processing'] = True
        
        return optimizations
    
    def _progressive_scale(self, image_data: bytes, target_scale: float, format: str) -> bytes:
        """Apply progressive scaling for large images."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Calculate intermediate scales
            current_scale = 1.0
            scales = []
            
            while current_scale > target_scale:
                next_scale = max(current_scale * 0.5, target_scale)
                scales.append(next_scale)
                current_scale = next_scale
            
            # Apply scales progressively
            current_image = image
            for scale in scales:
                if scale == target_scale:
                    # Final scaling
                    new_size = (int(image.width * scale), int(image.height * scale))
                    current_image = current_image.resize(new_size, Image.LANCZOS)
                else:
                    # Intermediate scaling with faster algorithm
                    new_size = (int(image.width * scale), int(image.height * scale))
                    current_image = current_image.resize(new_size, Image.BILINEAR)
                
                # Force garbage collection after each step
                gc.collect()
            
            # Save result
            output = io.BytesIO()
            save_kwargs = {'format': format, 'optimize': True}
            
            if format == 'PNG':
                save_kwargs['compress_level'] = 6
            elif format == 'JPEG':
                save_kwargs['quality'] = 85
                save_kwargs['progressive'] = True
            
            current_image.save(output, **save_kwargs)
            
            self.performance_stats['optimization_applied'] += 1
            logger.info(f"Progressive scaling applied with {len(scales)} steps")
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Progressive scaling failed: {e}")
            raise
    
    def _memory_efficient_process(self, image_data: bytes, target_scale: float, format: str) -> bytes:
        """Process image with memory efficiency priority."""
        try:
            # Use a more memory-efficient approach
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB early if needed to save memory
            if format != 'PNG' and image.mode in ('RGBA', 'LA', 'P'):
                if image.mode == 'RGBA':
                    # Create white background
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])
                    image = background
                else:
                    image = image.convert('RGB')
            
            # Force garbage collection
            gc.collect()
            
            # Calculate target size
            new_size = (int(image.width * target_scale), int(image.height * target_scale))
            
            # Use memory-efficient resizing
            resized = image.resize(new_size, Image.LANCZOS)
            
            # Clear original image from memory
            image.close()
            del image
            gc.collect()
            
            # Save with memory-efficient settings
            output = io.BytesIO()
            
            if format == 'PNG':
                # Use lower compression level for speed
                resized.save(output, format='PNG', optimize=True, compress_level=3)
            elif format == 'JPEG':
                # Use quality setting that balances size and memory
                resized.save(output, format='JPEG', quality=80, optimize=True)
            elif format == 'WEBP':
                resized.save(output, format='WEBP', quality=80, method=4)
            
            self.performance_stats['optimization_applied'] += 1
            logger.info("Memory-efficient processing applied")
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Memory-efficient processing failed: {e}")
            raise
    
    def _standard_process(self, image_data: bytes, target_scale: float, format: str) -> bytes:
        """Standard image processing without optimizations."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Handle transparency
            if format != 'PNG' and image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
            
            # Resize
            new_size = (int(image.width * target_scale), int(image.height * target_scale))
            resized = image.resize(new_size, Image.LANCZOS)
            
            # Save
            output = io.BytesIO()
            save_kwargs = {'format': format, 'optimize': True}
            
            if format == 'PNG':
                save_kwargs['compress_level'] = 6
            elif format == 'JPEG':
                save_kwargs['quality'] = 85
                save_kwargs['progressive'] = True
            elif format == 'WEBP':
                save_kwargs['quality'] = 85
                save_kwargs['method'] = 6
            
            resized.save(output, **save_kwargs)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Standard processing failed: {e}")
            raise
    
    def _update_stats(self, processing_time: float, input_size: int, output_size: int):
        """Update performance statistics."""
        self.performance_stats['total_operations'] += 1
        
        # Update average time
        total_ops = self.performance_stats['total_operations']
        current_avg = self.performance_stats['average_time']
        self.performance_stats['average_time'] = (
            (current_avg * (total_ops - 1) + processing_time) / total_ops
        )
        
        # Track memory usage
        memory_info = psutil.virtual_memory()
        self.performance_stats['memory_usage'].append(memory_info.percent)
        
        # Keep only last 10 measurements
        if len(self.performance_stats['memory_usage']) > 10:
            self.performance_stats['memory_usage'].pop(0)
        
        logger.debug(f"Processing time: {processing_time:.3f}s, "
                    f"Compression: {input_size} -> {output_size} bytes")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return self.performance_stats.copy()
    
    def reset_stats(self):
        """Reset performance statistics."""
        self.performance_stats = {
            'total_operations': 0,
            'average_time': 0.0,
            'memory_usage': [],
            'optimization_applied': 0
        }
    
    def cleanup(self):
        """Clean up resources."""
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
        self.memory_monitor.stop()


class MemoryMonitor:
    """Monitors memory usage and provides warnings."""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.memory_threshold = 0.85  # 85% memory usage threshold
        self.callbacks = []
    
    def start(self):
        """Start memory monitoring."""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Memory monitoring started")
    
    def stop(self):
        """Stop memory monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        logger.info("Memory monitoring stopped")
    
    def add_callback(self, callback):
        """Add callback for memory warnings."""
        self.callbacks.append(callback)
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                memory_info = psutil.virtual_memory()
                
                if memory_info.percent > self.memory_threshold * 100:
                    # Memory usage is high
                    for callback in self.callbacks:
                        try:
                            callback(memory_info.percent)
                        except Exception as e:
                            logger.error(f"Memory callback error: {e}")
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                time.sleep(10)  # Wait longer on error


def performance_timer(func):
    """Decorator to time function execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    return wrapper


def memory_efficient(func):
    """Decorator to ensure memory-efficient execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check memory before execution
        memory_info = psutil.virtual_memory()
        if memory_info.percent > 85:
            logger.warning(f"High memory usage ({memory_info.percent}%) before {func.__name__}")
            gc.collect()
        
        try:
            result = func(*args, **kwargs)
            
            # Force garbage collection after execution
            gc.collect()
            
            return result
        except Exception as e:
            # Clean up on error
            gc.collect()
            raise
    return wrapper


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()