#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카페24 자동화 프로젝트 서버 - 완성된 버전
"""
import os
import sys
from flask import Flask, render_template, jsonify, request, send_file
import json
import requests
from datetime import datetime
import io

# 자동 토큰 관리자 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auto_token_manager import get_token_manager

# 토큰 매니저 초기화 및 자동 갱신 시작
token_manager = get_token_manager()
token_manager.start_auto_refresh()

# Flask 앱 생성
app = Flask(__name__, 
    template_folder='src/web/templates',
    static_folder='src/web/static'
)

@app.route('/')
def index():
    """메인 페이지"""
    return jsonify({
        'message': 'Cafe24 Automation API Server',
        'status': 'running',
        'endpoints': {
            'products': '/api/products',
            'orders': '/api/orders/today',
            'categories': '/api/categories',
            'status': '/api/status'
        }
    })

@app.route('/health')
def health():
    """헬스체크 엔드포인트"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/status')
def api_status():
    """API 상태 확인"""
    # OAuth 토큰 확인
    oauth_token_exists = os.path.exists('oauth_token.json')
    
    # 토큰 유효성 검사
    token_valid = False
    if oauth_token_exists:
        try:
            token = token_manager.get_valid_token()
            token_valid = token is not None
        except:
            pass
    
    status = {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'apis': {
            'cafe24': 'ready' if token_valid else 'token_invalid'
        },
        'token_status': {
            'exists': oauth_token_exists,
            'valid': token_valid
        }
    }
    return jsonify(status)

@app.route('/api/products', methods=['GET'])
def get_products():
    """상품 목록 조회"""
    try:
        # 자동 갱신된 토큰과 헤더 사용
        try:
            headers = get_headers()
            mall_id = get_mall_id()
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 401
        
        limit = request.args.get('limit', 100)
        offset = request.args.get('offset', 0)
        
        url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
        params = {
            'limit': limit,
            'offset': offset,
            'fields': 'product_no,product_name,price,quantity,display,product_code,created_date'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'products': data.get('products', []),
                'count': len(data.get('products', []))
            })
        else:
            return jsonify({
                'success': False,
                'error': f'API 오류: {response.status_code}',
                'message': response.text
            }), response.status_code
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/orders/today', methods=['GET'])
def get_today_orders():
    """오늘 주문 조회"""
    try:
        # 자동 갱신된 토큰과 헤더 사용
        try:
            headers = get_headers()
            mall_id = get_mall_id()
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 401
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        url = f"https://{mall_id}.cafe24api.com/api/v2/admin/orders"
        params = {
            'start_date': today,
            'end_date': today,
            'limit': 100,
            'fields': 'order_id,order_date,payment_amount,order_status,buyer_name'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('orders', [])
            
            # 총액 계산
            total_amount = sum(float(order.get('payment_amount', '0')) for order in orders)
            
            return jsonify({
                'success': True,
                'orders': orders,
                'count': len(orders),
                'total_amount': total_amount,
                'date': today
            })
        elif response.status_code == 422:
            # 주문이 없는 경우
            return jsonify({
                'success': True,
                'orders': [],
                'count': 0,
                'total_amount': 0,
                'date': today
            })
        else:
            return jsonify({
                'success': False,
                'error': f'API 오류: {response.status_code}',
                'message': response.text
            }), response.status_code
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """카테고리 목록 조회"""
    try:
        # 실시간 카테고리 생성
        try:
            response = requests.get(
                f"https://{get_mall_id()}.cafe24api.com/api/v2/admin/products",
                headers=get_headers(),
                params={'limit': 100}
            )
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                categories = set()
                for product in products:
                    name = product.get('product_name', '')
                    if '[' in name and ']' in name:
                        start = name.find('[')
                        end = name.find(']')
                        if start < end:
                            brand = name[start+1:end]
                            categories.add(brand)
                
                category_list = [{'category_name': cat, 'category_no': i+1} 
                               for i, cat in enumerate(sorted(categories))]
                
                return jsonify({
                    'success': True,
                    'categories': category_list,
                    'source': 'realtime',
                    'count': len(category_list)
                })
            else:
                return jsonify({'success': False, 'error': 'API 오류'}), response.status_code
                
        except Exception as e:
            return jsonify({'success': False, 'error': f'카테고리 생성 실패: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def get_mall_id():
    """mall_id 가져오기"""
    token_path = 'oauth_token.json'
    with open(token_path, 'r', encoding='utf-8') as f:
        token_data = json.load(f)
    return token_data.get('mall_id')

def get_headers():
    """API 헤더 가져오기 (자동 토큰 갱신 포함)"""
    # 자동 갱신된 토큰 사용
    access_token = token_manager.get_valid_token()
    if not access_token:
        raise Exception("유효한 토큰을 가져올 수 없습니다")
    
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': '2025-06-01'
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("==" * 30)
    print("Cafe24 Automation Server Starting...")
    print("==" * 30)
    print(f"Server running on port {port}")
    print(f"API Status: http://localhost:{port}/api/status")
    print(f"Products: http://localhost:{port}/api/products")
    print(f"Orders: http://localhost:{port}/api/orders/today")
    print("==" * 30)
    
    app.run(host='0.0.0.0', port=port, debug=False)