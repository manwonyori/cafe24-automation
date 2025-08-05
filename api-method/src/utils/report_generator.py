#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Generator
Generates various reports for Cafe24 data
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List


class ReportGenerator:
    """Generate business reports"""
    
    def __init__(self):
        self.logger = logging.getLogger('ReportGenerator')
        
    def generate_daily_report(self, system) -> Dict[str, Any]:
        """Generate daily business report"""
        try:
            # Get today's data
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Fetch orders
            orders = system.get_orders(start_date=today, end_date=today)
            
            # Fetch inventory status
            inventory = system.check_inventory()
            
            # Calculate metrics
            total_sales = sum(float(order.get('total_price', 0)) for order in orders)
            order_count = len(orders)
            avg_order_value = total_sales / order_count if order_count > 0 else 0
            
            report = {
                'report_type': 'daily',
                'date': today,
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_orders': order_count,
                    'total_sales': total_sales,
                    'average_order_value': avg_order_value,
                    'low_stock_items': len(inventory['low_stock']),
                    'out_of_stock_items': len(inventory['out_of_stock'])
                },
                'orders': orders[:10],  # Top 10 orders
                'inventory_alerts': {
                    'low_stock': inventory['low_stock'][:5],
                    'out_of_stock': inventory['out_of_stock'][:5]
                }
            }
            
            self.logger.info(f"Daily report generated for {today}")
            return report
            
        except Exception as e:
            self.logger.error(f"Daily report generation failed: {e}")
            raise
            
    def generate_inventory_report(self, system) -> Dict[str, Any]:
        """Generate inventory status report"""
        try:
            # Get all products
            products = system.get_products()
            
            # Analyze inventory
            total_products = len(products)
            low_stock = []
            out_of_stock = []
            well_stocked = []
            
            for product in products:
                quantity = product.get('inventory_quantity', 0)
                if quantity == 0:
                    out_of_stock.append(product)
                elif quantity < 10:
                    low_stock.append(product)
                else:
                    well_stocked.append(product)
                    
            report = {
                'report_type': 'inventory',
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_products': total_products,
                    'well_stocked': len(well_stocked),
                    'low_stock': len(low_stock),
                    'out_of_stock': len(out_of_stock),
                    'stock_health': (len(well_stocked) / total_products * 100) if total_products > 0 else 0
                },
                'details': {
                    'critical_items': out_of_stock[:20],
                    'warning_items': low_stock[:20]
                },
                'recommendations': self._generate_inventory_recommendations(low_stock, out_of_stock)
            }
            
            self.logger.info("Inventory report generated")
            return report
            
        except Exception as e:
            self.logger.error(f"Inventory report generation failed: {e}")
            raise
            
    def generate_sales_report(self, system) -> Dict[str, Any]:
        """Generate sales analysis report"""
        try:
            # Get date range (last 30 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # Fetch orders
            orders = system.get_orders(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            
            # Analyze sales
            daily_sales = {}
            product_sales = {}
            
            for order in orders:
                # Daily aggregation
                order_date = order.get('order_date', '')[:10]
                if order_date not in daily_sales:
                    daily_sales[order_date] = {'count': 0, 'total': 0}
                    
                daily_sales[order_date]['count'] += 1
                daily_sales[order_date]['total'] += float(order.get('total_price', 0))
                
                # Product aggregation
                for item in order.get('items', []):
                    product_name = item.get('product_name', 'Unknown')
                    if product_name not in product_sales:
                        product_sales[product_name] = {'quantity': 0, 'revenue': 0}
                        
                    product_sales[product_name]['quantity'] += item.get('quantity', 0)
                    product_sales[product_name]['revenue'] += float(item.get('price', 0)) * item.get('quantity', 0)
                    
            # Top products
            top_products = sorted(
                product_sales.items(),
                key=lambda x: x[1]['revenue'],
                reverse=True
            )[:10]
            
            report = {
                'report_type': 'sales',
                'period': {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                },
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_orders': len(orders),
                    'total_revenue': sum(float(order.get('total_price', 0)) for order in orders),
                    'average_order_value': sum(float(order.get('total_price', 0)) for order in orders) / len(orders) if orders else 0,
                    'unique_products_sold': len(product_sales)
                },
                'daily_trends': daily_sales,
                'top_products': [
                    {
                        'name': name,
                        'quantity': data['quantity'],
                        'revenue': data['revenue']
                    }
                    for name, data in top_products
                ]
            }
            
            self.logger.info("Sales report generated")
            return report
            
        except Exception as e:
            self.logger.error(f"Sales report generation failed: {e}")
            raise
            
    def _generate_inventory_recommendations(self, low_stock: List[Dict], 
                                           out_of_stock: List[Dict]) -> List[str]:
        """Generate inventory recommendations"""
        recommendations = []
        
        if len(out_of_stock) > 0:
            recommendations.append(
                f"URGENT: {len(out_of_stock)} products are out of stock. Immediate restocking required."
            )
            
        if len(low_stock) > 0:
            recommendations.append(
                f"WARNING: {len(low_stock)} products have low inventory. Consider restocking soon."
            )
            
        # Analyze patterns
        high_value_oos = [p for p in out_of_stock if float(p.get('price', 0)) > 50000]
        if high_value_oos:
            recommendations.append(
                f"High-value items out of stock: {len(high_value_oos)} products over 50,000 won"
            )
            
        return recommendations