#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Health Checker
System health monitoring and diagnostics
"""

import sys
import logging
import importlib
from typing import Dict, Any


class HealthChecker:
    """System health monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger('HealthChecker')
        
    def check_environment(self) -> Dict[str, Any]:
        """Check Python environment"""
        return {
            'passed': sys.version_info >= (3, 8),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'message': 'Python 3.8+ required' if sys.version_info < (3, 8) else 'OK'
        }
        
    def check_dependencies(self) -> Dict[str, Any]:
        """Check required dependencies"""
        required = [
            'requests',
            'pandas',
            'flask',
            'python-dotenv'
        ]
        
        missing = []
        for package in required:
            try:
                importlib.import_module(package.replace('-', '_'))
            except ImportError:
                missing.append(package)
                
        return {
            'passed': len(missing) == 0,
            'missing': missing,
            'message': f"Missing: {', '.join(missing)}" if missing else 'All dependencies installed'
        }
        
    def check_api_connection(self, api_client) -> Dict[str, Any]:
        """Check API connectivity"""
        try:
            # Try a simple API call
            api_client.get_products(limit=1)
            return {
                'passed': True,
                'message': 'API connection successful'
            }
        except Exception as e:
            return {
                'passed': False,
                'message': f'API connection failed: {str(e)}'
            }
            
    def check_cache(self, cache_manager) -> Dict[str, Any]:
        """Check cache system"""
        try:
            # Test cache operations
            test_key = '_health_check_test'
            test_value = {'test': True}
            
            # Set
            cache_manager.set(test_key, test_value, ttl=60)
            
            # Get
            retrieved = cache_manager.get(test_key)
            
            # Delete
            cache_manager.delete(test_key)
            
            passed = retrieved == test_value
            
            return {
                'passed': passed,
                'message': 'Cache system operational' if passed else 'Cache test failed'
            }
        except Exception as e:
            return {
                'passed': False,
                'message': f'Cache error: {str(e)}'
            }