#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시스템 전체 디버그 및 테스트
"""
import requests
import json
import os
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

class SystemDebugger:
    def __init__(self):
        self.base_url = "https://cafe24-automation.onrender.com"
        self.local_url = "http://localhost:5000"
        self.results = {}
        
    def check_oauth_token(self):
        """OAuth 토큰 상태 확인"""
        print("\n=== OAuth 토큰 상태 확인 ===")
        try:
            # 토큰 파일 확인
            token_file = 'oauth_token.json'
            if os.path.exists(token_file):
                with open(token_file, 'r', encoding='utf-8') as f:
                    token_data = json.load(f)
                print(f"[OK] 토큰 파일 존재")
                print(f"  - Mall ID: {token_data.get('mall_id')}")
                print(f"  - Access Token: {'***' + token_data.get('access_token', '')[-10:]}")
                print(f"  - Expires In: {token_data.get('expires_in')} seconds")
                print(f"  - Token Date: {token_data.get('token_date')}")
                
                # 토큰 만료 확인
                if 'token_date' in token_data:
                    token_date = datetime.fromisoformat(token_data['token_date'])
                    expires_in = token_data.get('expires_in', 3600)
                    now = datetime.now()
                    elapsed = (now - token_date).total_seconds()
                    
                    if elapsed > expires_in:
                        print(f"[FAIL] 토큰 만료됨 (경과 시간: {elapsed}초)")
                        return False
                    else:
                        print(f"[OK] 토큰 유효 (남은 시간: {expires_in - elapsed}초)")
                        return True
            else:
                print("[FAIL] 토큰 파일 없음")
                return False
                
        except Exception as e:
            print(f"[FAIL] 토큰 확인 오류: {str(e)}")
            return False
    
    def test_api_endpoints(self, base_url):
        """API 엔드포인트 테스트"""
        print(f"\n=== API 엔드포인트 테스트 ({base_url}) ===")
        
        endpoints = [
            ('/api/status', 'GET', None),
            ('/api/products', 'GET', {'limit': 10}),
            ('/api/categories', 'GET', None),
            ('/api/margin/analysis', 'GET', None),
            ('/api/vendor/suppliers', 'GET', None),
            ('/api/vendor/brands', 'GET', None),
            ('/api/orders/today', 'GET', None),
            ('/api/low-stock', 'GET', {'threshold': 10})
        ]
        
        results = {}
        
        for endpoint, method, params in endpoints:
            url = base_url + endpoint
            try:
                if method == 'GET':
                    response = requests.get(url, params=params, timeout=10)
                else:
                    response = requests.post(url, json=params, timeout=10)
                
                status = response.status_code
                try:
                    data = response.json()
                    success = data.get('success', False)
                    error = data.get('error', '')
                    count = data.get('count', len(data.get('products', [])))
                except:
                    success = False
                    error = response.text[:100]
                    count = 0
                
                results[endpoint] = {
                    'status': status,
                    'success': success,
                    'error': error,
                    'count': count
                }
                
                if status == 200 and success:
                    print(f"[OK] {endpoint}: OK (데이터: {count}개)")
                else:
                    print(f"[FAIL] {endpoint}: {status} - {error}")
                    
            except requests.exceptions.RequestException as e:
                print(f"[FAIL] {endpoint}: 요청 실패 - {str(e)}")
                results[endpoint] = {
                    'status': 0,
                    'success': False,
                    'error': str(e),
                    'count': 0
                }
                
        return results
    
    def check_auto_token_refresh(self):
        """자동 토큰 갱신 상태 확인"""
        print("\n=== 자동 토큰 갱신 확인 ===")
        try:
            # auto_token_manager의 스레드 상태 확인
            import threading
            active_threads = threading.enumerate()
            token_thread = None
            
            for thread in active_threads:
                if 'token' in thread.name.lower():
                    token_thread = thread
                    break
            
            if token_thread:
                print(f"[OK] 토큰 갱신 스레드 활성: {token_thread.name}")
                print(f"  - 상태: {'실행중' if token_thread.is_alive() else '중지됨'}")
                return True
            else:
                print("[FAIL] 토큰 갱신 스레드 없음")
                return False
                
        except Exception as e:
            print(f"[FAIL] 스레드 확인 오류: {str(e)}")
            return False
    
    def check_database_connection(self):
        """데이터베이스 연결 확인 (필요시)"""
        print("\n=== 데이터베이스 연결 확인 ===")
        # 현재는 파일 기반이므로 스킵
        print("[INFO] 파일 기반 시스템 (DB 연결 불필요)")
        return True
    
    def check_static_files(self):
        """정적 파일 접근 확인"""
        print("\n=== 정적 파일 확인 ===")
        
        static_files = [
            '/static/excel_templates/cafe24_product_create.xlsx',
            '/static/excel_templates/cafe24_product_update.xlsx'
        ]
        
        for file_path in static_files:
            url = self.base_url + file_path
            try:
                response = requests.head(url, timeout=5)
                if response.status_code == 200:
                    print(f"[OK] {file_path}: OK")
                else:
                    print(f"[FAIL] {file_path}: {response.status_code}")
            except:
                print(f"[FAIL] {file_path}: 접근 실패")
    
    def generate_debug_report(self):
        """디버그 리포트 생성"""
        print("\n" + "="*50)
        print("디버그 리포트 요약")
        print("="*50)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'oauth_status': self.check_oauth_token(),
            'auto_refresh': self.check_auto_token_refresh(),
            'api_endpoints': self.test_api_endpoints(self.base_url),
            'recommendations': []
        }
        
        # 문제점 분석 및 권장사항
        if not report['oauth_status']:
            report['recommendations'].append("OAuth 토큰 갱신 필요")
        
        failed_endpoints = [ep for ep, res in report['api_endpoints'].items() 
                           if not res.get('success', False)]
        
        if failed_endpoints:
            report['recommendations'].append(f"실패한 엔드포인트 수정 필요: {', '.join(failed_endpoints)}")
        
        # 마진율 분석 확인
        margin_status = report['api_endpoints'].get('/api/margin/analysis', {})
        if not margin_status.get('success'):
            report['recommendations'].append("마진율 분석 API 점검 필요 - supply_price 필드 확인")
        
        # 공급업체 확인
        supplier_status = report['api_endpoints'].get('/api/vendor/suppliers', {})
        if supplier_status.get('count', 0) < 8:
            report['recommendations'].append("공급업체 데이터 추출 로직 재확인 필요")
        
        print("\n권장사항:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        
        # 결과 저장
        with open('debug_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n[OK] 디버그 리포트 저장: debug_report.json")
        
        return report

# Flask 디버그 엔드포인트
@app.route('/debug/system')
def debug_system():
    """시스템 전체 상태 디버그"""
    debugger = SystemDebugger()
    report = debugger.generate_debug_report()
    return jsonify(report)

@app.route('/debug/test-cafe24-api')
def test_cafe24_api():
    """Cafe24 API 직접 테스트"""
    try:
        # 토큰 가져오기
        from app import get_headers, get_mall_id
        headers = get_headers()
        mall_id = get_mall_id()
        
        # 상품 API 테스트
        url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
        params = {
            'limit': 5,
            'fields': 'product_no,product_name,price,supply_price,quantity'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        return jsonify({
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'data': response.json() if response.status_code == 200 else response.text,
            'mall_id': mall_id,
            'token_exists': 'Authorization' in headers
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__
        }), 500

if __name__ == '__main__':
    # 독립 실행 모드
    debugger = SystemDebugger()
    debugger.generate_debug_report()