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
from datetime import datetime, timedelta
import pytz
import io
from pathlib import Path
import logging
from functools import wraps
import time
from config import CAFE24_API_VERSION, DEFAULT_MALL_ID, API_CACHE_DURATION

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

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
from persistent_token_manager import persistent_token_manager
from enhanced_products_api import products_bp, ProductAPI, register_routes
from margin_management import margin_bp, MarginManager, register_margin_routes
from vendor_management_debug import vendor_bp, VendorManager, register_vendor_routes
from oauth_routes import oauth_bp, register_oauth_routes
from sales_analytics import sales_bp, SalesAnalytics, register_sales_routes

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
CACHE_DURATION = API_CACHE_DURATION  # config.py에서 관리

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
    """오늘 주문 조회 - 한국 시간 기준"""
    try:
        headers = get_headers()
        mall_id = get_mall_id()
    except Exception as e:
        logger.error(f"Failed to get headers: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 401
    
    # 한국 시간 기준 오늘 날짜
    utc_now = datetime.now(pytz.UTC)
    now_kst = utc_now.astimezone(KST)
    today = now_kst.strftime('%Y-%m-%d')
    
    logger.info(f"Fetching orders for today (KST): {today} ({now_kst.strftime('%Y-%m-%d %H:%M:%S %Z')})")
    
    url = f"https://{mall_id}.cafe24api.com/api/v2/admin/orders"
    params = {
        'start_date': today,
        'end_date': today,
        'limit': 500,
        'embed': 'items,receivers,return',  # 상세 정보 포함
        'order_status': 'N00,N10,N20,N21,N22,N30,N40',  # 정상 주문 상태만 (취소/환불 제외)
        'date_type': 'order_date'  # 주문일 기준
    }
    
    all_orders = []
    offset = 0
    total_amount = 0
    
    # 페이징 처리
    while True:
        params['offset'] = offset
        response = requests.get(url, headers=headers, params=params)
        
        logger.info(f"Today orders API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('orders', [])
            
            # 첫 번째 주문 상세 로깅
            if orders and offset == 0:
                logger.info(f"Sample order keys: {list(orders[0].keys())}")
                logger.info(f"Sample order data: {json.dumps(orders[0], ensure_ascii=False)[:500]}...")
            
            # 총액 계산 - 정확한 필드 사용
            for order in orders:
                # 주문 상태 확인 (취소/환불 제외)
                order_status = order.get('order_status', '')
                if order_status.startswith('C'):  # C로 시작하는 것은 취소 주문
                    continue
                
                # 다양한 금액 필드 확인
                amount = 0
                
                # 실제 결제 금액 우선 순위
                if 'actual_payment_amount' in order:
                    try:
                        amount = float(order.get('actual_payment_amount', '0').replace(',', ''))
                    except:
                        amount = 0
                elif 'payment_amount' in order:
                    try:
                        amount = float(order.get('payment_amount', '0').replace(',', ''))
                    except:
                        amount = 0
                elif 'order_price_amount' in order:
                    try:
                        amount = float(order.get('order_price_amount', '0').replace(',', ''))
                    except:
                        amount = 0
                
                if amount > 0:
                    logger.debug(f"Order {order.get('order_id')}: {amount} ({order_status})")
                
                total_amount += amount
            
            all_orders.extend(orders)
            
            if len(orders) < params['limit']:
                break
            offset += params['limit']
        else:
            logger.error(f"Orders API error: {response.status_code} - {response.text}")
            if response.status_code == 422:
                # 주문이 없는 경우
                break
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 오류: {response.status_code}',
                    'message': response.text
                }), response.status_code
    
    # 루프 종료 후 결과 반환
    logger.info(f"Today total: {total_amount} from {len(all_orders)} orders")
    
    return jsonify({
        'success': True,
        'orders': all_orders,
        'count': len(all_orders),
        'total_amount': total_amount,
        'date': today
    })

@app.route('/api/low-stock', methods=['GET'])
@handle_errors
def get_low_stock():
    """재고 부족 상품 조회"""
    headers = get_headers()
    mall_id = get_mall_id()
    
    url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
    params = {
        'limit': 500,
        'fields': 'product_no,product_name,price,quantity,display,product_code'
    }
    
    # 모든 상품 가져오기 (페이징)
    all_products = []
    offset = 0
    
    while True:
        params['offset'] = offset
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            all_products.extend(products)
            
            if len(products) < params['limit']:
                break
            offset += params['limit']
        else:
            logger.error(f"Low stock API error: {response.status_code}")
            break
    
    # 재고 부족 상품 필터링
    threshold = request.args.get('threshold', 10, type=int)
    low_stock_products = [
        p for p in all_products 
        if int(p.get('quantity', 0)) < threshold and int(p.get('quantity', 0)) > 0
    ]
    out_of_stock_products = [
        p for p in all_products 
        if int(p.get('quantity', 0)) == 0
    ]
    
    logger.info(f"Stock stats: Total={len(all_products)}, Low={len(low_stock_products)}, Out={len(out_of_stock_products)}")
    
    return jsonify({
        'success': True,
        'low_stock': low_stock_products,
        'out_of_stock': out_of_stock_products,
        'low_stock_count': len(low_stock_products),
        'out_of_stock_count': len(out_of_stock_products),
        'total_products': len(all_products),
        'threshold': threshold
    })

@app.route('/api/template/download', methods=['GET'])
@handle_errors
def download_template():
    """엑셀 템플릿 다운로드"""
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'error': '파일명이 필요합니다'}), 400
    
    # 보안을 위해 파일명 검증 (동적 생성 파일도 포함)
    import glob
    static_dir = Path('static/excel_templates')
    existing_files = [f.name for f in static_dir.glob('*.xlsx')] if static_dir.exists() else []
    
    allowed_files = [
        'product_upload_template.xlsx',
        'product_update_template.xlsx',
        'inventory_update_template.xlsx',
        'price_update_template.xlsx',
        'cafe24_product_create.xlsx',
        'cafe24_product_update.xlsx',
        'cafe24_inventory_update.xlsx',
        'cafe24_price_update.xlsx'
    ] + existing_files
    
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

@app.route('/api/generate-price-excel', methods=['GET'])
@handle_errors
def generate_price_excel():
    """실시간 가격 수정용 엑셀 파일 생성"""
    try:
        import pandas as pd
        from datetime import datetime
        
        # 현재 상품 정보 가져오기
        headers = get_headers()
        mall_id = get_mall_id()
        url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
        params = {
            'limit': 100,
            'fields': 'product_no,product_name,price,supply_price,retail_price,product_code'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'상품 정보 조회 실패: {response.status_code}'
            }), 500
        
        products = response.json().get('products', [])
        
        # 엑셀 데이터 준비
        excel_data = []
        for product in products:
            product_no = product.get('product_no')
            product_name = product.get('product_name', '')
            current_price = float(product.get('price', 0))
            supply_price = float(product.get('supply_price', 0))
            
            # 현재 마진율 계산
            current_margin = 0
            if supply_price > 0:
                current_margin = ((current_price - supply_price) / supply_price) * 100
            
            excel_data.append({
                'product_no': product_no,
                'product_name': product_name,
                'current_price': int(current_price),
                'supply_price': int(supply_price),
                'current_margin_rate': round(current_margin, 2),
                'new_price': int(current_price),  # 사용자가 수정할 칸
                'memo': ''
            })
        
        # 데이터프레임 생성
        df = pd.DataFrame(excel_data)
        
        # 파일 경로
        filename = f'price_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        filepath = Path('static/excel_templates') / filename
        
        # 엑셀 파일 생성
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='가격수정', index=False)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/api/template/download?filename={filename}',
            'message': f'{len(excel_data)}개 상품의 가격 수정용 엑셀 파일이 생성되었습니다.',
            'count': len(excel_data)
        })
        
    except Exception as e:
        logger.error(f"Excel generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
        return DEFAULT_MALL_ID  # config.py에서 관리

def get_headers():
    """API 헤더 가져오기 (영구 저장소 우선)"""
    access_token = None
    
    # 1. 영구 토큰 관리자에서 먼저 시도
    try:
        access_token = persistent_token_manager.get_token()
        if access_token:
            logger.info(f"Using token from persistent storage: ***{access_token[-10:]}")
    except Exception as e:
        logger.error(f"Failed to get token from persistent storage: {str(e)}")
    
    # 2. 토큰 매니저에서 시도 (자동 갱신)
    if not access_token:
        try:
            access_token = token_manager.get_valid_token()
            if access_token:
                logger.info(f"Using token from token manager: ***{access_token[-10:]}")
                # 영구 저장소에 저장
                token_data = token_manager.token_data
                if token_data:
                    persistent_token_manager.save_token(token_data)
        except Exception as e:
            logger.error(f"Failed to get token from manager: {str(e)}")
    
    # 3. 환경변수 (폴백)
    if not access_token:
        access_token = os.environ.get('CAFE24_ACCESS_TOKEN')
        if access_token:
            logger.info(f"Using token from environment variable: ***{access_token[-10:]}")
    
    if not access_token:
        raise Exception("유효한 토큰을 가져올 수 없습니다")
    
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': CAFE24_API_VERSION  # config.py에서 관리
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

# Sales Analytics API 초기화
sales_analytics = SalesAnalytics(get_headers, get_mall_id)
register_sales_routes(sales_bp, sales_analytics)
app.register_blueprint(sales_bp, url_prefix='/api/sales')

# CSV Import/Export API 초기화
from product_csv_import_export import CSVProductManager, register_csv_routes, csv_bp
csv_manager = CSVProductManager(get_headers, get_mall_id)
register_csv_routes(csv_bp, csv_manager)
app.register_blueprint(csv_bp, url_prefix='/api/csv')

# Margin Export Enhancement API 초기화
from margin_export_enhancement import MarginExportManager, register_margin_export_routes, margin_export_bp
margin_export_manager = MarginExportManager(get_headers, get_mall_id)
register_margin_export_routes(margin_export_bp, margin_export_manager)
app.register_blueprint(margin_export_bp, url_prefix='/api/margin')


# OAuth Callback 엔드포인트
@app.route('/callback')
def oauth_callback():
    """OAuth 인증 콜백"""
    try:
        auth_code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            return f"""
            <html><body>
            <h1>인증 오류</h1>
            <p>오류: {error}</p>
            <p>설명: {request.args.get('error_description', '')}</p>
            </body></html>
            """, 400
        
        if not auth_code:
            return """
            <html><body>
            <h1>인증 코드 없음</h1>
            <p>인증 코드가 제공되지 않았습니다.</p>
            </body></html>
            """, 400
        
        # 성공 페이지
        return f"""
        <html><body>
        <h1>인증 성공!</h1>
        <p><strong>인증 코드:</strong></p>
        <textarea rows="3" cols="50" readonly onclick="this.select()">{auth_code}</textarea>
        <p>이 코드를 복사해서 개발자에게 전달하세요.</p>
        <p>State: {state}</p>
        
        <script>
        // 자동으로 코드 선택
        document.querySelector('textarea').select();
        </script>
        </body></html>
        """
        
    except Exception as e:
        return f"""
        <html><body>
        <h1>콜백 처리 오류</h1>
        <p>오류: {str(e)}</p>
        </body></html>
        """, 500

# 디버그 라우트 추가
@app.route('/api/debug/orders')
@handle_errors
def debug_orders():
    """주문 데이터 디버그"""
    try:
        from sales_analytics import SalesAnalytics
        from datetime import datetime, timedelta
        import pytz
        
        KST = pytz.timezone('Asia/Seoul')
        
        sales = SalesAnalytics(get_headers, get_mall_id)
        
        # 최근 7일 데이터
        end_date = datetime.now(KST)
        start_date = end_date - timedelta(days=7)
        
        orders = sales.get_date_range_orders(start_date, end_date)
        
        # 상품 데이터 분석
        items_summary = []
        for order in orders[:5]:  # 처음 5개 주문만
            items = order.get('items', [])
            for item in items:
                items_summary.append({
                    'product_no': item.get('product_no'),
                    'product_name': item.get('product_name'),
                    'quantity': item.get('quantity'),
                    'product_price': item.get('product_price'),
                    'price': item.get('price')
                })
        
        return jsonify({
            'success': True,
            'period': f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
            'total_orders': len(orders),
            'sample_items': items_summary[:10],
            'debug_info': {
                'mall_id': get_mall_id(),
                'has_token': bool(get_headers().get('Authorization'))
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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