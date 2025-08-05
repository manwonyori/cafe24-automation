#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 API Client V2
Handles all API communications with OAuth 2.0 support
"""

import time
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from functools import wraps
from datetime import datetime, timedelta
from urllib.parse import urljoin

# Add OAuth manager import
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oauth_manager import Cafe24OAuthManager


def retry_on_error(max_retries: int = 3, delay: int = 2):
    """Decorator for automatic retry on API errors"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except requests.exceptions.RequestException as e:
                    last_error = e
                    wait_time = delay * (attempt + 1)  # Exponential backoff
                    self.logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(wait_time)
                except Exception as e:
                    self.logger.error(f"{func.__name__} error: {e}")
                    raise
                    
            raise last_error
            
        return wrapper
    return decorator


class Cafe24APIClient:
    """API client for Cafe24 e-commerce platform with OAuth 2.0"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize API client with configuration"""
        self.config = config
        self.mall_id = config['mall_id']
        self.base_url = f"https://{self.mall_id}.cafe24api.com/api/v2"
        self.api_version = config.get('api_version', '2025-06-01')
        
        # Setup logging
        self.logger = logging.getLogger('Cafe24APIClient')
        
        # Initialize OAuth manager
        self.oauth_manager = Cafe24OAuthManager(config)
        
        # Setup session with retry
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-Cafe24-Api-Version': self.api_version
        })
        
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with valid token"""
        headers = {
            'Content-Type': 'application/json',
            'X-Cafe24-Api-Version': self.api_version
        }
        
        # Get valid token from OAuth manager
        token = self.oauth_manager.get_valid_token()
        if token:
            headers['Authorization'] = f'Bearer {token}'
        else:
            self.logger.warning("No valid OAuth token available")
            
        return headers
        
    @retry_on_error()
    def _request(self, method: str, endpoint: str, 
                 data: Optional[Dict] = None, 
                 params: Optional[Dict] = None) -> requests.Response:
        """Make API request with retry logic"""
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        self.logger.info(f"API {method} {endpoint}")
        
        response = self.session.request(
            method=method,
            url=url,
            headers=self._get_headers(),
            json=data,
            params=params,
            timeout=30
        )
        
        # Check for token expiration (401 or 403)
        if response.status_code in [401, 403]:
            self.logger.warning(f"{response.status_code} error, attempting token refresh...")
            try:
                # Refresh token
                new_token = self.oauth_manager.refresh_access_token()
                if new_token:
                    self.logger.info("Token refreshed successfully")
                    # Update session headers with new token
                    self.session.headers.update(self._get_headers())
                    
                    # Retry with new token
                    response = self.session.request(
                        method=method,
                        url=url,
                        headers=self._get_headers(),
                        json=data,
                        params=params,
                        timeout=30
                    )
                    
                    # If still failing, token might be invalid
                    if response.status_code in [401, 403]:
                        self.logger.error("Token refresh did not resolve auth issue")
                else:
                    self.logger.error("Failed to obtain new token")
                    
            except Exception as e:
                self.logger.error(f"Token refresh failed: {e}")
                
        response.raise_for_status()
        return response
        
    # Product APIs
    def get_products(self, limit: int = 100, offset: int = 0, **kwargs) -> List[Dict]:
        """Get products list"""
        params = {
            'limit': limit,
            'offset': offset,
            **kwargs
        }
        
        response = self._request('GET', '/products', params=params)
        return response.json().get('products', [])
        
    def get_product(self, product_no: int) -> Dict:
        """Get single product details"""
        response = self._request('GET', f'/products/{product_no}')
        return response.json().get('product', {})
        
    def update_product(self, product_no: int, data: Dict) -> Dict:
        """Update product information"""
        response = self._request('PUT', f'/products/{product_no}', data={'product': data})
        return response.json()
        
    # Order APIs
    def get_orders(self, limit: int = 100, offset: int = 0, 
                   start_date: Optional[str] = None, 
                   end_date: Optional[str] = None, **kwargs) -> List[Dict]:
        """Get orders list"""
        params = {
            'limit': limit,
            'offset': offset,
            **kwargs
        }
        
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        response = self._request('GET', '/orders', params=params)
        return response.json().get('orders', [])
        
    def get_order(self, order_id: str) -> Dict:
        """Get single order details"""
        response = self._request('GET', f'/orders/{order_id}')
        return response.json().get('order', {})
        
    def update_order_status(self, order_id: str, status: str) -> Dict:
        """Update order status"""
        data = {'order': {'order_status': status}}
        response = self._request('PUT', f'/orders/{order_id}', data=data)
        return response.json()
        
    # Customer APIs
    def get_customers(self, limit: int = 100, offset: int = 0, **kwargs) -> List[Dict]:
        """Get customers list"""
        params = {
            'limit': limit,
            'offset': offset,
            **kwargs
        }
        
        response = self._request('GET', '/customers', params=params)
        return response.json().get('customers', [])
        
    # Inventory APIs
    def get_inventory(self, product_no: int) -> Dict:
        """Get product inventory"""
        response = self._request('GET', f'/products/{product_no}/inventory')
        return response.json().get('inventory', {})
        
    def update_inventory(self, product_no: int, quantity: int) -> Dict:
        """Update product inventory"""
        data = {'inventory': {'quantity': quantity}}
        response = self._request('PUT', f'/products/{product_no}/inventory', data=data)
        return response.json()
        
    # Customer APIs
    def get_customers(self, **kwargs) -> List[Dict]:
        """Get customers list"""
        params = {
            'limit': kwargs.get('limit', 100),
            'offset': kwargs.get('offset', 0)
        }
        
        response = self._request('GET', '/customers', params=params)
        data = response.json()
        
        # Handle Cafe24 response format
        if isinstance(data, dict) and 'customers' in data:
            return data['customers']
        return data
        
    # Statistics APIs
    def get_sales_statistics(self, period: str = 'daily', 
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> Dict:
        """Get sales statistics"""
        params = {
            'period': period
        }
        
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        response = self._request('GET', '/statistics/sales', params=params)
        return response.json()
        
    # Utility methods
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            self.get_products(limit=1)
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False