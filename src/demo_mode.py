#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Mode for Cafe24 System
Provides mock data when API credentials are not available
"""

from datetime import datetime, timedelta
import random


class DemoAPIClient:
    """Mock API client for demo mode"""
    
    def __init__(self, config):
        self.mall_id = config.get('mall_id', 'demo_shop')
        self.demo_mode = True
        
    def get_products(self, **kwargs):
        """Return mock products"""
        return [
            {
                'product_no': 1,
                'product_code': 'P001',
                'product_name': '데모 상품 1',
                'selling_price': '25000.00',
                'inventory_quantity': 50,
                'display': 'T',
                'selling': 'T',
                'created_date': datetime.now().isoformat()
            },
            {
                'product_no': 2,
                'product_code': 'P002',
                'product_name': '데모 상품 2',
                'selling_price': '35000.00',
                'inventory_quantity': 5,
                'display': 'T',
                'selling': 'T',
                'created_date': datetime.now().isoformat()
            }
        ]
        
    def get_orders(self, **kwargs):
        """Return mock orders"""
        return [
            {
                'order_id': 'DEMO-2024-001',
                'order_date': datetime.now().isoformat(),
                'payment_amount': '25000.00',
                'order_status': 'N00',
                'buyer_name': '홍길동',
                'buyer_email': 'demo@example.com'
            }
        ]
        
    def get_product(self, product_no):
        """Return mock product detail"""
        return {
            'product_no': product_no,
            'product_code': f'P{product_no:03d}',
            'product_name': f'데모 상품 {product_no}',
            'selling_price': '25000.00',
            'inventory_quantity': random.randint(0, 100)
        }
        
    def update_product(self, product_no, data):
        """Mock update product"""
        return {'success': True, 'product_no': product_no}
        
    def get_customers(self, **kwargs):
        """Return mock customers"""
        return [
            {
                'member_id': 'demo_user',
                'name': '데모 사용자',
                'email': 'demo@example.com',
                'created_date': datetime.now().isoformat()
            }
        ]