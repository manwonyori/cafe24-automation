#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Mode for Cafe24 System
Provides realistic mock data when API credentials are not available
"""

from datetime import datetime, timedelta
import random


class DemoAPIClient:
    """Mock API client for demo mode with realistic data"""
    
    def __init__(self, config):
        self.mall_id = config.get('mall_id', 'demo_shop')
        self.demo_mode = True
        
        # 실제 같은 상품 데이터
        self.products_data = [
            {
                'product_no': 1,
                'product_code': 'MW-001',
                'product_name': '만원요리 김치찌개 밀키트',
                'selling_price': '10000.00',
                'inventory_quantity': 45,
                'display': 'T',
                'selling': 'T',
                'summary_description': '집에서 즐기는 진짜 김치찌개',
                'created_date': (datetime.now() - timedelta(days=30)).isoformat()
            },
            {
                'product_no': 2,
                'product_code': 'MW-002',
                'product_name': '만원요리 된장찌개 밀키트',
                'selling_price': '10000.00',
                'inventory_quantity': 12,
                'display': 'T',
                'selling': 'T',
                'summary_description': '구수한 된장찌개 한 그릇',
                'created_date': (datetime.now() - timedelta(days=25)).isoformat()
            },
            {
                'product_no': 3,
                'product_code': 'MW-003',
                'product_name': '만원요리 부대찌개 밀키트',
                'selling_price': '12000.00',
                'inventory_quantity': 8,
                'display': 'T',
                'selling': 'T',
                'summary_description': '푸짐한 부대찌개 세트',
                'created_date': (datetime.now() - timedelta(days=20)).isoformat()
            },
            {
                'product_no': 4,
                'product_code': 'MW-004',
                'product_name': '만원요리 순두부찌개 밀키트',
                'selling_price': '10000.00',
                'inventory_quantity': 3,
                'display': 'T',
                'selling': 'T',
                'summary_description': '부드러운 순두부찌개',
                'created_date': (datetime.now() - timedelta(days=15)).isoformat()
            },
            {
                'product_no': 5,
                'product_code': 'MW-005',
                'product_name': '만원요리 갈비탕 밀키트',
                'selling_price': '15000.00',
                'inventory_quantity': 25,
                'display': 'T',
                'selling': 'T',
                'summary_description': '진한 갈비탕의 맛',
                'created_date': (datetime.now() - timedelta(days=10)).isoformat()
            }
        ]
        
        # 실제 같은 주문 데이터
        self.orders_data = []
        for i in range(5):
            order_date = datetime.now() - timedelta(hours=random.randint(0, 48))
            self.orders_data.append({
                'order_id': f'2024{order_date.strftime("%m%d")}-{1000+i:04d}',
                'order_date': order_date.isoformat(),
                'payment_amount': str(random.choice([10000, 20000, 30000, 45000])),
                'order_status': random.choice(['N00', 'N10', 'N20', 'N30']),
                'buyer_name': random.choice(['김철수', '이영희', '박민수', '최지은', '정대한']),
                'buyer_email': f'customer{i+1}@example.com',
                'order_items': [
                    {
                        'product_name': random.choice([p['product_name'] for p in self.products_data]),
                        'quantity': random.randint(1, 3),
                        'product_price': '10000.00'
                    }
                ]
            })
        
    def get_products(self, **kwargs):
        """Return mock products"""
        limit = kwargs.get('limit', 100)
        offset = kwargs.get('offset', 0)
        
        # 필터링
        products = self.products_data.copy()
        
        # 재고 필터
        if kwargs.get('inventory_quantity_lte'):
            threshold = int(kwargs.get('inventory_quantity_lte'))
            products = [p for p in products if p['inventory_quantity'] <= threshold]
            
        # 판매중 필터
        if kwargs.get('selling'):
            products = [p for p in products if p['selling'] == kwargs.get('selling')]
            
        # 페이징
        return products[offset:offset + limit]
        
    def get_orders(self, **kwargs):
        """Return mock orders"""
        limit = kwargs.get('limit', 100)
        offset = kwargs.get('offset', 0)
        
        # 날짜 필터
        orders = self.orders_data.copy()
        
        if kwargs.get('start_date'):
            start = datetime.fromisoformat(kwargs['start_date'])
            orders = [o for o in orders if datetime.fromisoformat(o['order_date']) >= start]
            
        if kwargs.get('end_date'):
            end = datetime.fromisoformat(kwargs['end_date'])
            orders = [o for o in orders if datetime.fromisoformat(o['order_date']) <= end]
            
        # 정렬 (최신순)
        orders.sort(key=lambda x: x['order_date'], reverse=True)
        
        return orders[offset:offset + limit]
        
    def get_product(self, product_no):
        """Return mock product detail"""
        for product in self.products_data:
            if product['product_no'] == int(product_no):
                return product
        return {
            'product_no': product_no,
            'product_code': f'MW-{product_no:03d}',
            'product_name': f'만원요리 상품 {product_no}',
            'selling_price': '10000.00',
            'inventory_quantity': random.randint(0, 100)
        }
        
    def update_product(self, product_no, data):
        """Mock update product"""
        return {'success': True, 'product_no': product_no}
        
    def get_customers(self, **kwargs):
        """Return mock customers"""
        customers = [
            {
                'member_id': 'customer001',
                'name': '김철수',
                'email': 'kim@example.com',
                'phone': '010-1234-5678',
                'group_name': 'VIP',
                'total_order_amount': '450000',
                'created_date': (datetime.now() - timedelta(days=180)).isoformat()
            },
            {
                'member_id': 'customer002',
                'name': '이영희',
                'email': 'lee@example.com',
                'phone': '010-2345-6789',
                'group_name': '일반',
                'total_order_amount': '120000',
                'created_date': (datetime.now() - timedelta(days=90)).isoformat()
            },
            {
                'member_id': 'customer003',
                'name': '박민수',
                'email': 'park@example.com',
                'phone': '010-3456-7890',
                'group_name': '신규',
                'total_order_amount': '30000',
                'created_date': (datetime.now() - timedelta(days=7)).isoformat()
            }
        ]
        
        limit = kwargs.get('limit', 100)
        offset = kwargs.get('offset', 0)
        return customers[offset:offset + limit]
        
    def get_inventory(self, product_no):
        """Get product inventory"""
        for product in self.products_data:
            if product['product_no'] == int(product_no):
                return {
                    'product_no': product_no,
                    'inventory_quantity': product['inventory_quantity'],
                    'safety_stock': 10,
                    'use_inventory': 'T'
                }
        return {'inventory_quantity': 0}
        
    def update_inventory(self, product_no, quantity):
        """Update product inventory"""
        for product in self.products_data:
            if product['product_no'] == int(product_no):
                product['inventory_quantity'] = quantity
                return {'success': True, 'inventory_quantity': quantity}
        return {'success': False}
        
    def get_order(self, order_id):
        """Get single order details"""
        for order in self.orders_data:
            if order['order_id'] == order_id:
                return order
        return {
            'order_id': order_id,
            'order_date': datetime.now().isoformat(),
            'payment_amount': '0',
            'order_status': 'N00'
        }
        
    def update_order_status(self, order_id, status):
        """Update order status"""
        for order in self.orders_data:
            if order['order_id'] == order_id:
                order['order_status'] = status
                return {'success': True, 'order_status': status}
        return {'success': False}
        
    def get_sales_statistics(self, period='daily', **kwargs):
        """Get sales statistics"""
        today = datetime.now()
        
        if period == 'daily':
            return {
                'period': 'daily',
                'date': today.strftime('%Y-%m-%d'),
                'total_sales': '125000',
                'order_count': 5,
                'average_order_value': '25000',
                'best_selling_products': [
                    {'product_name': '만원요리 김치찌개 밀키트', 'quantity': 12},
                    {'product_name': '만원요리 된장찌개 밀키트', 'quantity': 8}
                ]
            }
        elif period == 'weekly':
            return {
                'period': 'weekly',
                'start_date': (today - timedelta(days=7)).strftime('%Y-%m-%d'),
                'end_date': today.strftime('%Y-%m-%d'),
                'total_sales': '875000',
                'order_count': 35,
                'average_order_value': '25000'
            }
        elif period == 'monthly':
            return {
                'period': 'monthly',
                'month': today.strftime('%Y-%m'),
                'total_sales': '3750000',
                'order_count': 150,
                'average_order_value': '25000',
                'growth_rate': '+15.3%'
            }
            
    def test_connection(self):
        """Test API connection"""
        return True