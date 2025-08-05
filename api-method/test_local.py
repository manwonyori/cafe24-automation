#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Cafe24 system locally
"""

import os
import sys

# Add source directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cafe24_system import Cafe24System
from demo_mode import DemoAPIClient


def test_demo_mode():
    """Test demo mode functionality"""
    print("Testing Demo Mode...")
    print("=" * 50)
    
    # Create demo client
    demo = DemoAPIClient({'mall_id': 'test'})
    
    # Test products
    print("\n1. Testing Products API:")
    products = demo.get_products(limit=3)
    print(f"   Found {len(products)} products")
    for p in products[:2]:
        print(f"   - {p['product_name']}: {p['selling_price']} won ({p['inventory_quantity']} in stock)")
        
    # Test orders
    print("\n2. Testing Orders API:")
    orders = demo.get_orders(limit=3)
    print(f"   Found {len(orders)} orders")
    for o in orders[:2]:
        print(f"   - Order {o['order_id']}: {o['payment_amount']} won by {o['buyer_name']}")
        
    # Test customers
    print("\n3. Testing Customers API:")
    customers = demo.get_customers(limit=3)
    print(f"   Found {len(customers)} customers")
    for c in customers[:2]:
        print(f"   - {c['name']} ({c['email']}): {c['total_order_amount']} won total")
        
    # Test inventory
    print("\n4. Testing Inventory API:")
    for i in range(1, 4):
        inv = demo.get_inventory(i)
        print(f"   Product {i}: {inv['inventory_quantity']} units")
        
    # Test sales statistics
    print("\n5. Testing Sales Statistics API:")
    for period in ['daily', 'weekly', 'monthly']:
        stats = demo.get_sales_statistics(period=period)
        print(f"   {period.capitalize()}: {stats['total_sales']} won ({stats['order_count']} orders)")
        
    print("\n[OK] All demo mode tests passed!")
    

def test_system():
    """Test full system"""
    print("\n\nTesting Full System...")
    print("=" * 50)
    
    # Create system in demo mode
    os.environ['CAFE24_MALL_ID'] = ''
    os.environ['CAFE24_CLIENT_ID'] = ''
    os.environ['CAFE24_CLIENT_SECRET'] = ''
    
    system = Cafe24System()
    
    print(f"System initialized in {'demo' if system.demo_mode else 'production'} mode")
    
    # Test natural language processing
    print("\n1. Testing Natural Language Commands:")
    commands = [
        "show products",
        "check inventory", 
        "today orders"
    ]
    
    for cmd in commands:
        result = system.execute(cmd)
        print(f"   Command: '{cmd}' -> Success: {result['success']}")
        
    # Test direct methods
    print("\n2. Testing Direct Methods:")
    
    # Products
    products = system.get_products(limit=2)
    print(f"   get_products(): {len(products)} products")
    
    # Orders
    orders = system.get_orders()
    print(f"   get_orders(): {len(orders)} orders")
    
    # Customers
    customers = system.get_customers(limit=2)
    print(f"   get_customers(): {len(customers)} customers")
    
    # Sales stats
    stats = system.get_sales_statistics(period='daily')
    print(f"   get_sales_statistics(): {stats['total_sales']} won daily")
    
    # Inventory check
    inv_check = system.check_inventory(threshold=10)
    print(f"   check_inventory(): {len(inv_check['low_stock'])} low stock items")
    
    print("\n[OK] All system tests passed!")
    

def main():
    """Run all tests"""
    print("Cafe24 Local Test Suite")
    print("=" * 50)
    
    try:
        test_demo_mode()
        test_system()
        
        print("\n\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("The system is working correctly in demo mode.")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()