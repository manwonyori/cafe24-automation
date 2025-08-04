#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
리포트 생성 모듈
"""
import json
from datetime import datetime, timedelta
import pandas as pd
import os

class ReportGenerator:
    def __init__(self, api_client):
        self.api_client = api_client
        
    def generate_daily_report(self):
        """일일 리포트 생성"""
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'generated_at': datetime.now().isoformat(),
            'sections': {}
        }
        
        # 주문 데이터
        try:
            orders_response = self.api_client.get('/api/orders/today')
            if orders_response.status_code == 200:
                orders_data = orders_response.json()
                report['sections']['orders'] = {
                    'total_count': orders_data.get('count', 0),
                    'total_amount': orders_data.get('total_amount', 0),
                    'average_order': orders_data.get('total_amount', 0) / max(orders_data.get('count', 1), 1)
                }
        except Exception as e:
            report['sections']['orders'] = {'error': str(e)}
        
        # 상품 통계
        try:
            products_response = self.api_client.get('/api/products?limit=100')
            if products_response.status_code == 200:
                products_data = products_response.json()
                products = products_data.get('products', [])
                
                # 재고 분석
                low_stock = [p for p in products if int(p.get('quantity', 0)) < 10]
                out_of_stock = [p for p in products if int(p.get('quantity', 0)) == 0]
                
                report['sections']['inventory'] = {
                    'total_products': len(products),
                    'low_stock_count': len(low_stock),
                    'out_of_stock_count': len(out_of_stock),
                    'low_stock_items': [{'name': p['product_name'], 'stock': p.get('quantity', 0)} for p in low_stock[:5]]
                }
        except Exception as e:
            report['sections']['inventory'] = {'error': str(e)}
        
        return report
    
    def generate_inventory_report(self):
        """재고 리포트 생성"""
        try:
            response = self.api_client.get('/api/products?limit=500')
            if response.status_code != 200:
                return {'error': 'Failed to fetch products'}
            
            products = response.json().get('products', [])
            
            # 재고 분석
            inventory_analysis = {
                'total_products': len(products),
                'by_status': {
                    'well_stocked': 0,
                    'low_stock': 0,
                    'out_of_stock': 0
                },
                'alerts': [],
                'recommendations': []
            }
            
            for product in products:
                stock = int(product.get('quantity', 0))
                
                if stock == 0:
                    inventory_analysis['by_status']['out_of_stock'] += 1
                    inventory_analysis['alerts'].append({
                        'type': 'out_of_stock',
                        'product': product['product_name'],
                        'product_code': product.get('product_code', 'N/A')
                    })
                elif stock < 10:
                    inventory_analysis['by_status']['low_stock'] += 1
                    inventory_analysis['alerts'].append({
                        'type': 'low_stock',
                        'product': product['product_name'],
                        'stock': stock,
                        'product_code': product.get('product_code', 'N/A')
                    })
                else:
                    inventory_analysis['by_status']['well_stocked'] += 1
            
            # 추천사항
            if inventory_analysis['by_status']['out_of_stock'] > 0:
                inventory_analysis['recommendations'].append(
                    f"긴급: {inventory_analysis['by_status']['out_of_stock']}개 상품이 품절 상태입니다. 즉시 재입고가 필요합니다."
                )
            
            if inventory_analysis['by_status']['low_stock'] > 5:
                inventory_analysis['recommendations'].append(
                    f"주의: {inventory_analysis['by_status']['low_stock']}개 상품이 재고 부족 상태입니다."
                )
            
            return inventory_analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_sales_report(self, days=30):
        """매출 리포트 생성"""
        report = {
            'period': f'Last {days} days',
            'generated_at': datetime.now().isoformat(),
            'summary': {},
            'daily_sales': []
        }
        
        try:
            # 일별 매출 데이터 수집 (실제로는 여러 API 호출이 필요할 수 있음)
            today = datetime.now()
            total_revenue = 0
            total_orders = 0
            
            # 오늘 데이터만 가져오기 (데모)
            response = self.api_client.get('/api/orders/today')
            if response.status_code == 200:
                data = response.json()
                report['summary'] = {
                    'total_revenue': data.get('total_amount', 0),
                    'total_orders': data.get('count', 0),
                    'average_order_value': data.get('total_amount', 0) / max(data.get('count', 1), 1),
                    'top_day': today.strftime('%Y-%m-%d')
                }
            
            return report
            
        except Exception as e:
            return {'error': str(e)}
    
    def export_to_excel(self, report_type='daily'):
        """리포트를 엑셀 파일로 내보내기"""
        try:
            if report_type == 'daily':
                report = self.generate_daily_report()
            elif report_type == 'inventory':
                report = self.generate_inventory_report()
            elif report_type == 'sales':
                report = self.generate_sales_report()
            else:
                return None
            
            # DataFrame 생성 및 엑셀 저장
            filename = f"cafe24_report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # 각 섹션을 시트로 저장
                if isinstance(report, dict):
                    for section, data in report.items():
                        if isinstance(data, dict) or isinstance(data, list):
                            df = pd.DataFrame([data] if isinstance(data, dict) else data)
                            df.to_excel(writer, sheet_name=str(section)[:30], index=False)
            
            return filename
            
        except Exception as e:
            return None