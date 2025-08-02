import pytest
import time
import tempfile
import shutil
from src.cache_manager import CacheManager


class TestCacheManager:
    """Test cache management functionality"""
    
    @pytest.fixture
    def cache_dir(self):
        """Create temporary cache directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def cache(self, cache_dir):
        """Create cache manager instance"""
        config = {
            'enabled': True,
            'ttl': 2,  # 2 seconds for testing
            'cache_dir': cache_dir
        }
        return CacheManager(config)
    
    def test_cache_set_and_get(self, cache):
        """Test basic cache operations"""
        key = 'test_key'
        value = {'data': 'test_value'}
        
        # Set value
        result = cache.set(key, value)
        assert result is True
        
        # Get value
        retrieved = cache.get(key)
        assert retrieved == value
        
    def test_cache_expiration(self, cache):
        """Test cache TTL"""
        key = 'expire_test'
        value = 'test_data'
        
        cache.set(key, value)
        assert cache.get(key) == value
        
        # Wait for expiration
        time.sleep(3)
        assert cache.get(key) is None
        
    def test_cache_delete(self, cache):
        """Test cache deletion"""
        key = 'delete_test'
        value = 'data'
        
        cache.set(key, value)
        assert cache.get(key) == value
        
        # Delete
        result = cache.delete(key)
        assert result is True
        assert cache.get(key) is None
        
    def test_cache_clear(self, cache):
        """Test clearing all cache"""
        # Add multiple items
        for i in range(5):
            cache.set(f'key_{i}', f'value_{i}')
            
        # Clear all
        count = cache.clear()
        assert count >= 5
        
        # Verify all cleared
        for i in range(5):
            assert cache.get(f'key_{i}') is None
            
    def test_product_cache(self, cache):
        """Test product-specific caching"""
        products = [
            {'product_no': 1, 'product_name': 'Test 1', 'display': 'T', 'selling': 'T'},
            {'product_no': 2, 'product_name': 'Test 2', 'display': 'T', 'selling': 'F'}
        ]
        
        # Save product cache
        result = cache.save_product_cache(products)
        assert result is True
        
        # Load product cache
        cached_data = cache.load_product_cache()
        assert cached_data is not None
        assert cached_data['total_count'] == 2
        assert cached_data['stats']['display_rate'] == 100.0
        assert cached_data['stats']['sell_rate'] == 50.0