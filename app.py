#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카페24 자동화 프로젝트 서버 - 완벽한 연동 버전
"""
import os
import sys
from flask import Flask, render_template, jsonify, request, send_file
import json
import requests
from datetime import datetime
import io
from pathlib import Path
import logging
from functools import wraps
import time

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 자동 토큰 관리자 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auto_token_manager import get_token_manager
from enhanced_products_api import products_bp, ProductAPI, register_routes
from margin_management import margin_bp, MarginManager, register_margin_routes
from vendor_management_debug import vendor_bp, VendorManager, register_vendor_routes
from oauth_routes import oauth_bp, register_oauth_routes

# 토큰 매니저 초기화 및 자동 갱신 시작
token_manager = get_token_manager()
token_manager.start_auto_refresh()

# Flask 앱 생성
app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)

# 에러 핸들러 데코레이터
def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e),
                'function': f.__name__
            }), 500
    return decorated_function

# API 응답 캐싱
cache = {}
CACHE_DURATION = 60  # 1분

def get_cached_or_fetch(key, fetch_function, *args, **kwargs):
    """캐시에서 가져오거나 새로 fetch"""
    now = time.time()
    if key in cache:
        data, timestamp = cache[key]
        if now - timestamp < CACHE_DURATION:
            logger.info(f"Cache hit for {key}")
            return data
    
    logger.info(f"Cache miss for {key}, fetching...")
    data = fetch_function(*args, **kwargs)
    cache[key] = (data, now)
    return data

@app.route('/')
def index():
    """메인 페이지"""
    return jsonify({
        'message': 'Cafe24 Automation API Server',
        'status': 'running',
        'version': '2.0',
        'endpoints': {
            'dashboard': '/dashboard',
            'margin': '/margin-dashboard',
            'vendor': '/vendor-dashboard',
            'products': '/api/products',
            'orders': '/api/orders/today',
            'categories': '/api/categories',
            'status': '/api/status'
        }
    })

@app.route('/health')
def health():
    """헬스체크 엔드포인트"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'token_status': token_manager.get_valid_token() is not None
    }), 200

@app.route('/dashboard')
def dashboard():
    """대시보드 페이지"""
    return render_template('dashboard.html')

@app.route('/advanced-dashboard')
def advanced_dashboard():
    """고급 대시보드 페이지"""
    return render_template('advanced_dashboard.html')

@app.route('/margin-dashboard')
def margin_dashboard():
    """마진율 관리 대시보드"""
    return render_template('margin_dashboard.html')

@app.route('/vendor-dashboard')
def vendor_dashboard():
    """업체 관리 대시보드"""
    return render_template('vendor_dashboard.html')

@app.route('/api/command', methods=['POST'])
@handle_errors
def process_command():
    """자연어 명령 처리"""
    try:
        from nlp_processor import NLPProcessor
    except ImportError:
        return jsonify({'success': False, 'error': 'NLP 모듈을 찾을 수 없습니다'}), 500
    
    data = request.get_json()
    command = data.get('command', '')
    
    if not command:
        return jsonify({'success': False, 'error': '명령어를 입력하세요'}), 400
    
    # NLP 처리
    processor = NLPProcessor()
    result = processor.process(command)
    
    # 명령 실행
    if result['action'] == 'list_products':
        return product_api.get_products_advanced()
    elif result['action'] == 'list_orders':
        return get_today_orders()
    elif result['action'] == 'check_inventory':
        return get_low_stock()
    elif result['action'] == 'sales_report':
        from report_generator import ReportGenerator
        generator = ReportGenerator(app.test_client())
        report = generator.generate_daily_report()
        return jsonify({'success': True, 'report': report})
    else:
        return jsonify({
            'success': False, 
            'error': '알 수 없는 명령입니다',
            'parsed': result
        }), 400

@app.route('/api/report/<report_type>', methods=['GET'])
@handle_errors
def generate_report(report_type):
    """리포트 생성"""
    from report_generator import ReportGenerator
    
    generator = ReportGenerator(app.test_client())
    
    if report_type == 'daily':
        report = generator.generate_daily_report()
    elif report_type == 'inventory':
        report = generator.generate_inventory_report()
    elif report_type == 'sales':
        days = request.args.get('days', 30, type=int)
        report = generator.generate_sales_report(days)
    else:
        return jsonify({'success': False, 'error': 'Invalid report type'}), 400
    
    return jsonify({'success': True, 'report': report})

@app.route('/api/status')
@handle_errors
def api_status():
    """API 상태 확인"""
    # OAuth 토큰 확인
    oauth_token_exists = os.path.exists('oauth_token.json')
    
    # 토큰 유효성 검사
    token_valid = False
    token_info = {}
    if oauth_token_exists:
        try:
            token = token_manager.get_valid_token()
            token_valid = token is not None
            if token_valid:
                token_info = {
                    'expires_in': token_manager.get_remaining_time(),
                    'auto_refresh': token_manager.running
                }
        except:
            pass
    
    # API 테스트
    api_test = {}
    try:
        headers = get_headers()
        mall_id = get_mall_id()
        test_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/count"
        response = requests.get(test_url, headers=headers, timeout=5)
        api_test = {
            'reachable': response.status_code < 500,
            'authenticated': response.status_code != 401,
            'status_code': response.status_code
        }
    except:
        api_test = {
            'reachable': False,
            'authenticated': False,
            'status_code': 0
        }
    
    status = {
        'status': 'ok' if token_valid else 'token_invalid',
        'timestamp': datetime.now().isoformat(),
        'apis': {
            'cafe24': 'ready' if token_valid else 'token_invalid'
        },
        'token_status': {
            'exists': oauth_token_exists,
            'valid': token_valid,
            'info': token_info
        },
        'api_test': api_test,
        'server': {
            'uptime': time.time(),
            'version': '2.0'
        }
    }
    return jsonify(status)

@app.route('/api/products', methods=['GET'])
@handle_errors
def get_products():
    """기본 상품 목록 조회 (캐싱 적용)"""
    # 캐시 키 생성
    params = request.args.to_dict()
    cache_key = f"products_{json.dumps(params, sort_keys=True)}"
    
    def fetch():
        return product_api.get_products_advanced()
    
    # 캐시 사용 안함 (실시간 데이터 필요)
    return product_api.get_products_advanced()

@app.route('/api/orders/today', methods=['GET'])
@handle_errors
def get_today_orders():
    """오늘 주문 조회"""
    try:
        headers = get_headers()
        mall_id = get_mall_id()
    except Exception as e:
        logger.error(f"Failed to get headers: {str(e)}")
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
        logger.error(f"Orders API error: {response.status_code} - {response.text}")
        return jsonify({
            'success': False,
            'error': f'API 오류: {response.status_code}',
            'message': response.text
        }), response.status_code

@app.route('/api/low-stock', methods=['GET'])
@handle_errors
def get_low_stock():
    """재고 부족 상품 조회"""
    headers = get_headers()
    mall_id = get_mall_id()
    
    url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
    params = {
        'limit': 100,
        'fields': 'product_no,product_name,price,quantity,display,product_code'
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        
        # 재고 부족 상품 필터링
        threshold = request.args.get('threshold', 10, type=int)
        low_stock_products = [
            p for p in products 
            if int(p.get('quantity', 0)) < threshold and int(p.get('quantity', 0)) > 0
        ]
        out_of_stock_products = [
            p for p in products 
            if int(p.get('quantity', 0)) == 0
        ]
        
        return jsonify({
            'success': True,
            'low_stock': low_stock_products,
            'out_of_stock': out_of_stock_products,
            'low_stock_count': len(low_stock_products),
            'out_of_stock_count': len(out_of_stock_products),
            'threshold': threshold
        })
    else:
        return jsonify({
            'success': False,
            'error': f'API 오류: {response.status_code}'
        }), response.status_code

@app.route('/api/template/download', methods=['GET'])
@handle_errors
def download_template():
    """엑셀 템플릿 다운로드"""
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'error': '파일명이 필요합니다'}), 400
    
    # 보안을 위해 파일명 검증
    allowed_files = [
        'product_upload_template.xlsx',
        'product_update_template.xlsx',
        'inventory_update_template.xlsx',
        'price_update_template.xlsx',
        'cafe24_product_create.xlsx',
        'cafe24_product_update.xlsx',
        'cafe24_inventory_update.xlsx',
        'cafe24_price_update.xlsx'
    ]
    
    if filename not in allowed_files:
        return jsonify({'error': '허용되지 않은 파일입니다'}), 403
    
    # 파일 경로
    file_path = Path('static/excel_templates') / filename
    
    if not file_path.exists():
        return jsonify({'error': '파일을 찾을 수 없습니다'}), 404
    
    return send_file(
        file_path,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/categories', methods=['GET'])
@handle_errors
def get_categories():
    """카테고리 목록 조회"""
    # 캐시 사용
    cache_key = "categories"
    
    def fetch():
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
                
                return {
                    'success': True,
                    'categories': category_list,
                    'source': 'realtime',
                    'count': len(category_list)
                }
            else:
                return {'success': False, 'error': 'API 오류'}
                
        except Exception as e:
            return {'success': False, 'error': f'카테고리 생성 실패: {str(e)}'}
    
    result = get_cached_or_fetch(cache_key, fetch)
    return jsonify(result)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

def get_mall_id():
    """mall_id 가져오기"""
    # 환경변수에서 먼저 시도
    mall_id = os.environ.get('CAFE24_MALL_ID')
    if mall_id:
        return mall_id
    
    # 파일에서 시도
    try:
        token_path = 'oauth_token.json'
        with open(token_path, 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        return token_data.get('mall_id')
    except:
        return 'manwonyori'

def get_headers():
    """API 헤더 가져오기 (자동 토큰 갱신 포함)"""
    access_token = None
    
    # 1. 환경변수에서 토큰 먼저 시도
    access_token = os.environ.get('CAFE24_ACCESS_TOKEN')
    if access_token:
        logger.info(f"Using token from environment variable: ***{access_token[-10:]}")
    
    # 2. 토큰 매니저에서 시도
    if not access_token:
        try:
            access_token = token_manager.get_valid_token()
            if access_token:
                logger.info(f"Using token from token manager: ***{access_token[-10:]}")
        except Exception as e:
            logger.error(f"Failed to get token from manager: {str(e)}")
    
    # 3. 파일에서 직접 시도
    if not access_token:
        try:
            with open('oauth_token.json', 'r', encoding='utf-8') as f:
                token_data = json.load(f)
                access_token = token_data.get('access_token')
                if access_token:
                    logger.info(f"Using token from file: ***{access_token[-10:]}")
        except Exception as e:
            logger.error(f"Failed to get token from file: {str(e)}")
    
    if not access_token:
        raise Exception("유효한 토큰을 가져올 수 없습니다")
    
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': '2024-06-01'
    }

# Enhanced Product API 초기화 (함수 정의 후에)
product_api = ProductAPI(get_headers, get_mall_id)
register_routes(products_bp, product_api)
app.register_blueprint(products_bp, url_prefix='/api/products')

# Margin Management API 초기화
margin_manager = MarginManager(get_headers, get_mall_id)
register_margin_routes(margin_bp, margin_manager)
app.register_blueprint(margin_bp, url_prefix='/api/margin')

# Vendor Management API 초기화
vendor_manager = VendorManager(get_headers, get_mall_id)
register_vendor_routes(vendor_bp, vendor_manager)
app.register_blueprint(vendor_bp, url_prefix='/api/vendor')

# OAuth 라우트 등록
register_oauth_routes(app)

# 디버그 라우트 추가
@app.route('/api/debug/token')
@handle_errors
def debug_token():
    """토큰 상태 디버그"""
    try:
        # 환경 변수 확인
        env_token = os.environ.get('CAFE24_ACCESS_TOKEN')
        env_has_token = env_token is not None
        
        # 토큰 매니저 확인
        manager_token = None
        try:
            manager_token = token_manager.get_valid_token()
        except:
            pass
            
        # 파일 확인
        file_token = None
        try:
            with open('oauth_token.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                file_token = data.get('access_token')
        except:
            pass
        
        # 남은 시간 확인
        remaining = 0
        try:
            remaining = token_manager.get_remaining_time()
        except:
            pass
        
        return jsonify({
            'env_has_token': env_has_token,
            'env_token_preview': f"***{env_token[-10:]}" if env_token else None,
            'manager_has_token': manager_token is not None,
            'file_has_token': file_token is not None,
            'remaining_seconds': remaining,
            'remaining_minutes': remaining / 60 if remaining else 0,
            'auto_refresh_active': token_manager.running,
            'next_refresh': '30분마다 자동 갱신',
            'mall_id': get_mall_id()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'has_token': False
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("==" * 30)
    print("Cafe24 Automation Server v2.0 Starting...")
    print("==" * 30)
    print(f"Server running on port {port}")
    print(f"API Status: http://localhost:{port}/api/status")
    print(f"Dashboard: http://localhost:{port}/dashboard")
    print(f"Token Debug: http://localhost:{port}/api/debug/token")
    print("==" * 30)
    print("✓ 자동 토큰 갱신: 30분마다")
    print("✓ 에러 로깅: app.log")
    print("✓ API 캐싱: 1분")
    print("==" * 30)
    
    app.run(host='0.0.0.0', port=port, debug=False)