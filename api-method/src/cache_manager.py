#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache Manager
High-performance caching system for Cafe24 data
"""

import os
import json
import time
import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from threading import Lock


class CacheManager:
    """Manages caching for API responses"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize cache manager"""
        self.config = config
        self.enabled = config.get('enabled', True)
        self.ttl = config.get('ttl', 3600)  # Default 1 hour
        self.cache_dir = config.get('cache_dir', 'cache')
        self.memory_cache = {}
        self.lock = Lock()
        
        # Setup logging
        self.logger = logging.getLogger('CacheManager')
        
        # Create cache directory
        if self.enabled:
            os.makedirs(self.cache_dir, exist_ok=True)
            
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
            
        # Try memory cache first
        with self.lock:
            if key in self.memory_cache:
                data, timestamp = self.memory_cache[key]
                if self._is_valid(timestamp):
                    self.logger.debug(f"Memory cache hit: {key}")
                    return data
                else:
                    # Remove expired entry
                    del self.memory_cache[key]
                    
        # Try file cache
        file_path = self._get_cache_file_path(key)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                if self._is_valid(cache_data['timestamp']):
                    self.logger.debug(f"File cache hit: {key}")
                    # Update memory cache
                    with self.lock:
                        self.memory_cache[key] = (cache_data['data'], cache_data['timestamp'])
                    return cache_data['data']
                else:
                    # Remove expired file
                    os.remove(file_path)
                    
            except Exception as e:
                self.logger.error(f"Cache read error: {e}")
                
        return None
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not self.enabled:
            return False
            
        ttl = ttl or self.ttl
        timestamp = time.time()
        
        # Update memory cache
        with self.lock:
            self.memory_cache[key] = (value, timestamp)
            
        # Write to file cache
        file_path = self._get_cache_file_path(key)
        try:
            cache_data = {
                'key': key,
                'data': value,
                'timestamp': timestamp,
                'ttl': ttl,
                'created_at': datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            self.logger.debug(f"Cache set: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Cache write error: {e}")
            return False
            
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        # Remove from memory cache
        with self.lock:
            if key in self.memory_cache:
                del self.memory_cache[key]
                
        # Remove file
        file_path = self._get_cache_file_path(key)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                self.logger.debug(f"Cache deleted: {key}")
                return True
            except Exception as e:
                self.logger.error(f"Cache delete error: {e}")
                
        return False
        
    def clear(self) -> int:
        """Clear all cache"""
        count = 0
        
        # Clear memory cache
        with self.lock:
            count += len(self.memory_cache)
            self.memory_cache.clear()
            
        # Clear file cache
        if os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        os.remove(file_path)
                        count += 1
                    except Exception as e:
                        self.logger.error(f"Failed to delete {filename}: {e}")
                        
        self.logger.info(f"Cache cleared: {count} entries removed")
        return count
        
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            'enabled': self.enabled,
            'memory_entries': len(self.memory_cache),
            'file_entries': 0,
            'total_size': 0,
            'hit_rate': 0.0  # Would need to track hits/misses for this
        }
        
        if os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    stats['file_entries'] += 1
                    file_path = os.path.join(self.cache_dir, filename)
                    stats['total_size'] += os.path.getsize(file_path)
                    
        return stats
        
    def _is_valid(self, timestamp: float) -> bool:
        """Check if cache entry is still valid"""
        return time.time() - timestamp < self.ttl
        
    def _get_cache_file_path(self, key: str) -> str:
        """Get file path for cache key"""
        # Create safe filename from key
        safe_key = key.replace('/', '_').replace(':', '_')
        # Hash if too long
        if len(safe_key) > 200:
            import hashlib
            safe_key = hashlib.md5(key.encode()).hexdigest()
            
        return os.path.join(self.cache_dir, f"{safe_key}.json")
        
    def save_product_cache(self, products: list) -> bool:
        """Save product data with statistics"""
        try:
            # Calculate statistics
            displayed = len([p for p in products if p.get('display') == 'T'])
            selling = len([p for p in products if p.get('selling') == 'T'])
            
            cache_data = {
                'cached_at': datetime.now().isoformat(),
                'total_count': len(products),
                'stats': {
                    'displayed': displayed,
                    'selling': selling,
                    'display_rate': (displayed / len(products) * 100) if products else 0,
                    'sell_rate': (selling / len(products) * 100) if products else 0
                },
                'products': products
            }
            
            # Save to special product cache file
            file_path = os.path.join(self.cache_dir, 'product_cache.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Product cache saved: {len(products)} products")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save product cache: {e}")
            return False
            
    def load_product_cache(self) -> Optional[Dict[str, Any]]:
        """Load product cache with validation"""
        file_path = os.path.join(self.cache_dir, 'product_cache.json')
        
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # Check if cache is still valid
            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            if datetime.now() - cached_at < timedelta(seconds=self.ttl):
                self.logger.info(f"Product cache loaded: {cache_data['total_count']} products")
                return cache_data
            else:
                self.logger.info("Product cache expired")
                os.remove(file_path)
                
        except Exception as e:
            self.logger.error(f"Failed to load product cache: {e}")
            
        return None