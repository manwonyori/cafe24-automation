#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OAuth Manager for Cafe24 API
Handles token acquisition and automatic refresh
"""

import os
import json
import time
import base64
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional


class Cafe24OAuthManager:
    """Manages OAuth authentication for Cafe24 API"""
    
    def __init__(self, config: Dict):
        self.mall_id = config['mall_id']
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.redirect_uri = config.get('redirect_uri', 'https://localhost:8000/callback')
        self.scope = config.get('scope', 'mall.read_product,mall.write_product,mall.read_order,mall.write_order,mall.read_customer,mall.read_supply')
        
        self.auth_base_url = f"https://{self.mall_id}.cafe24api.com/api/v2/oauth"
        self.token_url = f"{self.auth_base_url}/token"
        
        self.logger = logging.getLogger('Cafe24OAuth')
        
        # Load existing token if available
        self.token_data = self._load_token()
        
    def _load_token(self) -> Dict:
        """Load token from environment or storage"""
        # First try environment variables
        access_token = os.getenv('CAFE24_ACCESS_TOKEN')
        refresh_token = os.getenv('CAFE24_REFRESH_TOKEN')
        
        if access_token:
            return {
                'access_token': access_token,
                'refresh_token': refresh_token or '',
                'expires_at': datetime.now() + timedelta(hours=2),  # Default 2 hours
                'token_type': 'Bearer'
            }
        
        # Try loading from Redis or database if configured
        # For now, return empty
        return {}
        
    def get_authorization_url(self) -> str:
        """Get OAuth authorization URL"""
        auth_url = f"{self.auth_base_url}/authorize"
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'state': base64.b64encode(os.urandom(16)).decode('utf-8')
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{auth_url}?{query_string}"
        
    def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        
        return self._request_token(data)
        
    def refresh_access_token(self) -> Dict:
        """Refresh access token using refresh token"""
        if not self.token_data.get('refresh_token'):
            raise ValueError("No refresh token available")
            
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.token_data['refresh_token']
        }
        
        return self._request_token(data)
        
    def _request_token(self, data: Dict) -> Dict:
        """Common token request method"""
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(
                self.token_url,
                data=data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            
            # Calculate expiration time
            expires_in = token_data.get('expires_in', 7200)  # Default 2 hours
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            self.token_data = {
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token', ''),
                'expires_at': expires_at,
                'token_type': token_data.get('token_type', 'Bearer'),
                'scope': token_data.get('scope', self.scope)
            }
            
            self._save_token(self.token_data)
            self.logger.info("Token acquired successfully")
            
            return self.token_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Token request failed: {e}")
            raise
            
    def _save_token(self, token_data: Dict):
        """Save token to storage"""
        # In production, save to Redis or database
        # For now, just log
        self.logger.info("Token saved (in-memory only)")
        
    def get_valid_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary"""
        if not self.token_data:
            self.logger.warning("No token available, OAuth flow required")
            return None
            
        # Check if token is expired or about to expire (5 min buffer)
        expires_at = self.token_data.get('expires_at')
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
            
        if expires_at and datetime.now() > expires_at - timedelta(minutes=5):
            self.logger.info("Token expired or expiring soon, refreshing...")
            try:
                self.refresh_access_token()
            except Exception as e:
                self.logger.error(f"Token refresh failed: {e}")
                return None
                
        return self.token_data.get('access_token')
        
    def is_authenticated(self) -> bool:
        """Check if we have a valid token"""
        return self.get_valid_token() is not None