#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 API Client
Handles all API communications with proper error handling and retry logic
"""

import time
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from functools import wraps
from datetime import datetime, timedelta
from urllib.parse import urljoin


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
    """API client for Cafe24 e-commerce platform"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize API client with configuration"""
        self.config = config
        self.mall_id = config['mall_id']
        self.base_url = f"https://{self.mall_id}.cafe24api.com/api/v2"
        self.api_version = config.get('api_version', '2025-06-01')
        
        # Setup logging
        self.logger = logging.getLogger('Cafe24APIClient')
        
        # Initialize token
        self.token_data = self._load_token()
        self._check_token_validity()
        
    def _load_token(self) -> Dict[str, Any]:
        """Load OAuth token"""
        # Use environment variables for Render deployment
        import os
        
        # Create token structure from environment
        return {
            'access_token': os.getenv('CAFE24_ACCESS_TOKEN', ''),
            'refresh_token': os.getenv('CAFE24_REFRESH_TOKEN', ''),
            'expires_at': (datetime.now() + timedelta(hours=2)).isoformat(),
                'client_id': self.config['client_id'],
                'mall_id': self.mall_id
            }
            
    def _save_token(self, token_data: Dict[str, Any]):
        """Save OAuth token"""
        import os
        token_file = os.getenv('CAFE24_TOKEN_FILE', 'config/oauth_token.json')
        
        os.makedirs(os.path.dirname(token_file), exist_ok=True)
        
        with open(token_file, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, indent=2)
            
    def _check_token_validity(self):
        """Check and refresh token if needed"""
        try:
            expires_at = datetime.fromisoformat(
                self.token_data['expires_at'].replace('.000', '')
            )
            
            if datetime.now() > expires_at - timedelta(minutes=5):
                self.logger.info("Token expired or expiring soon, refreshing...")
                self._refresh_token()
        except Exception as e:
            self.logger.error(f"Token validity check failed: {e}")
            
    def _refresh_token(self):
        """Refresh OAuth token"""
        try:
            response = requests.post(
                f"https://{self.mall_id}.cafe24api.com/api/v2/oauth/token",
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': self.token_data['refresh_token']
                },
                auth=(
                    self.config['client_id'],
                    self.config['client_secret']
                ),
                timeout=30
            )
            
            if response.status_code == 200:
                new_token = response.json()
                
                # Update token data
                self.token_data['access_token'] = new_token['access_token']
                self.token_data['refresh_token'] = new_token['refresh_token']
                self.token_data['expires_at'] = (
                    datetime.now() + timedelta(seconds=new_token.get('expires_in', 7200))
                ).isoformat()
                
                # Save updated token
                self._save_token(self.token_data)
                self.logger.info("Token refreshed successfully")
                
            else:
                self.logger.error(f"Token refresh failed: {response.status_code}")
                raise Exception("Token refresh failed")
                
        except Exception as e:
            self.logger.error(f"Token refresh error: {e}")
            raise
            
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return {
            'Authorization': f"Bearer {self.token_data['access_token']}",
            'Content-Type': 'application/json',
            'X-Cafe24-Api-Version': self.api_version
        }
        
    @retry_on_error()
    def _request(self, method: str, endpoint: str, 
                 data: Optional[Dict] = None, 
                 params: Optional[Dict] = None) -> requests.Response:
        """Make API request with retry logic"""
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        self.logger.info(f"API {method} {endpoint}")
        
        response = requests.request(
            method=method,
            url=url,
            headers=self._get_headers(),
            json=data,
            params=params,
            timeout=30
        )
        
        # Check for token expiration
        if response.status_code == 401:
            self.logger.warning("401 Unauthorized, refreshing token...")
            self._refresh_token()
            
            # Retry with new token
            response = requests.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                json=data,
                params=params,
                timeout=30
            )
            
        response.raise_for_status()
        return response
        
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
        payload = {
            'shop_no': 1,
            'request': data
        }
        
        response = self._request('PUT', f'/products/{product_no}', data=payload)
        return response.json()
        
    def get_orders(self, start_date: str, end_date: str, **kwargs) -> List[Dict]:
        """Get orders within date range"""
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'embed': 'items,buyer,receivers',
            **kwargs
        }
        
        response = self._request('GET', '/orders', params=params)
        return response.json().get('orders', [])
        
    def get_order(self, order_id: str) -> Dict:
        """Get single order details"""
        response = self._request('GET', f'/orders/{order_id}')
        return response.json().get('order', {})
        
    def update_order_status(self, order_id: str, status: str) -> Dict:
        """Update order status"""
        data = {
            'shop_no': 1,
            'request': {
                'status': status
            }
        }
        
        response = self._request('PUT', f'/orders/{order_id}', data=data)
        return response.json()
        
    def get_customers(self, **kwargs) -> List[Dict]:
        """Get customers list"""
        response = self._request('GET', '/customers', params=kwargs)
        return response.json().get('customers', [])
        
    def get_inventory(self, product_no: int) -> Dict:
        """Get product inventory"""
        response = self._request('GET', f'/products/{product_no}/inventory')
        return response.json().get('inventory', {})
        
    def update_inventory(self, product_no: int, quantity: int) -> Dict:
        """Update product inventory"""
        data = {
            'shop_no': 1,
            'request': {
                'quantity': quantity
            }
        }
        
        response = self._request('PUT', f'/products/{product_no}/inventory', data=data)
        return response.json()