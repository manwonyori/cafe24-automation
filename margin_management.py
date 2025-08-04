#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
마진율 관리 시스템
- 공급가/판매가 마진율 계산
- 구간별 마진율 분석
- 가격 수정 기능
"""
from flask import Blueprint, request, jsonify
import requests
from datetime import datetime
import pandas as pd

margin_bp = Blueprint('margin', __name__)

class MarginManager:
    def __init__(self, get_headers, get_mall_id):
        self.get_headers = get_headers
        self.get_mall_id = get_mall_id
    
    def calculate_margin(self, supply_price, selling_price):
        """마진율 계산"""
        if supply_price <= 0:
            return 0
        margin_rate = ((selling_price - supply_price) / supply_price) * 100
        return round(margin_rate, 2)
    
    def get_margin_analysis(self):
        """전체 상품의 마진율 분석"""
        try:
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            # 모든 상품 가져오기
            url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
            all_products = []
            offset = 0
            limit = 100
            
            while True:
                params = {
                    'limit': limit,
                    'offset': offset,
                    'fields': 'product_no,product_code,product_name,price,supply_price,retail_price,quantity,display,selling'
                }
                
                response = requests.get(url, headers=headers, params=params)
                if response.status_code != 200:
                    break
                
                data = response.json()
                products = data.get('products', [])
                if not products:
                    break
                
                all_products.extend(products)
                offset += limit
                
                if len(products) < limit:
                    break
            
            # 마진율 계산 및 구간별 분석
            margin_ranges = {
                '적자 (-100% ~ 0%)': {'products': [], 'count': 0, 'total_value': 0},
                '저마진 (0% ~ 10%)': {'products': [], 'count': 0, 'total_value': 0},
                '일반 (10% ~ 20%)': {'products': [], 'count': 0, 'total_value': 0},
                '양호 (20% ~ 30%)': {'products': [], 'count': 0, 'total_value': 0},
                '우수 (30% ~ 50%)': {'products': [], 'count': 0, 'total_value': 0},
                '최우수 (50% 이상)': {'products': [], 'count': 0, 'total_value': 0}
            }
            
            total_margin_sum = 0
            margin_calculated_count = 0
            
            for product in all_products:
                try:
                    selling_price = float(product.get('price', 0))
                    supply_price = float(product.get('supply_price', 0))
                    quantity = int(product.get('quantity', 0))
                    
                    if supply_price > 0:
                        margin_rate = self.calculate_margin(supply_price, selling_price)
                        profit = selling_price - supply_price
                        inventory_value = selling_price * quantity
                        
                        product_info = {
                            'product_no': product['product_no'],
                            'product_code': product.get('product_code', ''),
                            'product_name': product['product_name'],
                            'supply_price': supply_price,
                            'selling_price': selling_price,
                            'margin_rate': margin_rate,
                            'profit': profit,
                            'quantity': quantity,
                            'inventory_value': inventory_value,
                            'display': product.get('display', 'F'),
                            'selling': product.get('selling', 'F')
                        }
                        
                        # 구간별 분류
                        if margin_rate < 0:
                            range_key = '적자 (-100% ~ 0%)'
                        elif margin_rate < 10:
                            range_key = '저마진 (0% ~ 10%)'
                        elif margin_rate < 20:
                            range_key = '일반 (10% ~ 20%)'
                        elif margin_rate < 30:
                            range_key = '양호 (20% ~ 30%)'
                        elif margin_rate < 50:
                            range_key = '우수 (30% ~ 50%)'
                        else:
                            range_key = '최우수 (50% 이상)'
                        
                        margin_ranges[range_key]['products'].append(product_info)
                        margin_ranges[range_key]['count'] += 1
                        margin_ranges[range_key]['total_value'] += inventory_value
                        
                        total_margin_sum += margin_rate
                        margin_calculated_count += 1
                        
                except Exception as e:
                    continue
            
            # 평균 마진율 계산
            avg_margin = total_margin_sum / margin_calculated_count if margin_calculated_count > 0 else 0
            
            # 각 구간별 상품 정렬 (마진율 기준)
            for range_key in margin_ranges:
                margin_ranges[range_key]['products'].sort(
                    key=lambda x: x['margin_rate'], 
                    reverse=True
                )
            
            return jsonify({
                'success': True,
                'total_products': len(all_products),
                'margin_calculated_products': margin_calculated_count,
                'average_margin_rate': round(avg_margin, 2),
                'margin_ranges': margin_ranges,
                'generated_at': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def update_prices_by_margin(self):
        """마진율 기준으로 가격 일괄 수정"""
        try:
            data = request.json
            target_margin = data.get('target_margin')  # 목표 마진율
            product_nos = data.get('product_nos', [])  # 수정할 상품 번호들
            update_type = data.get('update_type', 'selling')  # 'selling' or 'supply'
            
            if not target_margin or not product_nos:
                return jsonify({'success': False, 'error': '필수 파라미터가 누락되었습니다'}), 400
            
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            results = []
            success_count = 0
            failed_count = 0
            
            for product_no in product_nos:
                try:
                    # 현재 상품 정보 조회
                    url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{product_no}"
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code != 200:
                        results.append({
                            'product_no': product_no,
                            'status': 'failed',
                            'error': '상품 정보 조회 실패'
                        })
                        failed_count += 1
                        continue
                    
                    product_data = response.json().get('product', {})
                    current_selling_price = float(product_data.get('price', 0))
                    current_supply_price = float(product_data.get('supply_price', 0))
                    
                    if current_supply_price <= 0:
                        results.append({
                            'product_no': product_no,
                            'status': 'failed',
                            'error': '공급가가 0이거나 설정되지 않음'
                        })
                        failed_count += 1
                        continue
                    
                    # 새로운 가격 계산
                    if update_type == 'selling':
                        # 판매가 수정 (공급가 기준)
                        new_selling_price = current_supply_price * (1 + target_margin / 100)
                        new_selling_price = round(new_selling_price, -2)  # 100원 단위 반올림
                        
                        update_data = {
                            'product': {
                                'price': str(int(new_selling_price))
                            }
                        }
                        old_price = current_selling_price
                        new_price = new_selling_price
                        
                    else:  # update_type == 'supply'
                        # 공급가 수정 (판매가 기준)
                        new_supply_price = current_selling_price / (1 + target_margin / 100)
                        new_supply_price = round(new_supply_price, -2)  # 100원 단위 반올림
                        
                        update_data = {
                            'product': {
                                'supply_price': str(int(new_supply_price))
                            }
                        }
                        old_price = current_supply_price
                        new_price = new_supply_price
                    
                    # 가격 업데이트
                    response = requests.put(url, headers=headers, json=update_data)
                    
                    if response.status_code == 200:
                        success_count += 1
                        results.append({
                            'product_no': product_no,
                            'product_name': product_data.get('product_name', ''),
                            'status': 'success',
                            'old_price': old_price,
                            'new_price': new_price,
                            'margin_rate': target_margin
                        })
                    else:
                        failed_count += 1
                        results.append({
                            'product_no': product_no,
                            'status': 'failed',
                            'error': response.text
                        })
                        
                except Exception as e:
                    failed_count += 1
                    results.append({
                        'product_no': product_no,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return jsonify({
                'success': True,
                'total': len(product_nos),
                'success_count': success_count,
                'failed_count': failed_count,
                'results': results
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_products_by_margin_range(self):
        """특정 마진율 구간의 상품 조회"""
        try:
            min_margin = request.args.get('min_margin', type=float)
            max_margin = request.args.get('max_margin', type=float)
            
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            # 모든 상품 조회
            url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
            params = {
                'limit': 100,
                'fields': 'product_no,product_code,product_name,price,supply_price,quantity,display'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                # 마진율 필터링
                filtered_products = []
                for product in products:
                    supply_price = float(product.get('supply_price', 0))
                    selling_price = float(product.get('price', 0))
                    
                    if supply_price > 0:
                        margin_rate = self.calculate_margin(supply_price, selling_price)
                        
                        if (min_margin is None or margin_rate >= min_margin) and \
                           (max_margin is None or margin_rate <= max_margin):
                            product['margin_rate'] = margin_rate
                            product['profit'] = selling_price - supply_price
                            filtered_products.append(product)
                
                # 마진율 기준 정렬
                filtered_products.sort(key=lambda x: x['margin_rate'], reverse=True)
                
                return jsonify({
                    'success': True,
                    'products': filtered_products,
                    'count': len(filtered_products),
                    'filter': {
                        'min_margin': min_margin,
                        'max_margin': max_margin
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 오류: {response.status_code}'
                }), response.status_code
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

# 라우트 등록
def register_margin_routes(bp, manager):
    """마진 관리 라우트 등록"""
    bp.add_url_rule('/analysis', 'get_margin_analysis', manager.get_margin_analysis, methods=['GET'])
    bp.add_url_rule('/update-prices', 'update_prices_by_margin', manager.update_prices_by_margin, methods=['POST'])
    bp.add_url_rule('/by-range', 'get_products_by_margin_range', manager.get_products_by_margin_range, methods=['GET'])