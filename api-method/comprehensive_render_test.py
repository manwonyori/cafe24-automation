#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render 서버 종합 테스트
"""
import requests
import json
import sys
import io
from datetime import datetime

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Render 서버 URL
base_url = 'https://cafe24-automation.onrender.com'

print("=== Render 서버 종합 테스트 ===")
print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"서버: {base_url}")
print("="*50)

# 테스트 결과 저장
test_results = {}

# 1. 서버 상태 확인
print("\n1. 서버 상태 확인")
print("-"*30)
tests = [
    ('/', 'GET', None, '홈페이지'),
    ('/api/status', 'GET', None, 'API 상태'),
    ('/health', 'GET', None, '헬스체크'),
    ('/api/debug/token', 'GET', None, '토큰 디버그'),
]

for endpoint, method, data, desc in tests:
    print(f"\n테스트: {desc} ({method} {endpoint})")
    try:
        if method == 'GET':
            response = requests.get(f'{base_url}{endpoint}', timeout=10)
        else:
            response = requests.post(f'{base_url}{endpoint}', json=data, timeout=10)
        
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"응답: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}...")
                test_results[endpoint] = {'status': 'OK', 'data': result}
            except:
                print(f"응답 (HTML): {response.text[:100]}...")
                test_results[endpoint] = {'status': 'OK', 'data': 'HTML'}
        else:
            print(f"오류 응답: {response.text[:100]}...")
            test_results[endpoint] = {'status': f'ERROR {response.status_code}'}
    except Exception as e:
        print(f"예외 발생: {str(e)}")
        test_results[endpoint] = {'status': 'EXCEPTION', 'error': str(e)}

# 2. 제품 관련 API 테스트
print("\n\n2. 제품 관련 API 테스트")
print("-"*30)
product_endpoints = [
    ('/api/products', 'GET', None, '제품 목록'),
    ('/api/products/all', 'GET', None, '전체 제품'),
    ('/api/margin/analysis', 'GET', None, '마진 분석'),
    ('/api/margin/products', 'GET', None, '마진 제품'),
    ('/api/execute', 'POST', {"command": "전체 상품"}, '자연어 명령'),
]

for endpoint, method, data, desc in product_endpoints:
    print(f"\n테스트: {desc} ({method} {endpoint})")
    try:
        if method == 'GET':
            response = requests.get(f'{base_url}{endpoint}', timeout=10)
        else:
            response = requests.post(
                f'{base_url}{endpoint}', 
                json=data, 
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
        
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                print(f"응답 타입: dict")
                print(f"키: {list(result.keys())}")
                if 'products' in result:
                    print(f"제품 수: {len(result['products'])}")
                if 'data' in result:
                    print(f"데이터 수: {len(result['data']) if isinstance(result['data'], list) else 'N/A'}")
            elif isinstance(result, list):
                print(f"응답 타입: list")
                print(f"항목 수: {len(result)}")
                if result:
                    print(f"첫 번째 항목: {result[0]}")
            test_results[endpoint] = {'status': 'OK', 'count': len(result) if isinstance(result, list) else 'dict'}
        else:
            test_results[endpoint] = {'status': f'ERROR {response.status_code}'}
    except Exception as e:
        print(f"예외 발생: {str(e)}")
        test_results[endpoint] = {'status': 'EXCEPTION', 'error': str(e)}

# 3. OAuth 토큰 상태 확인
print("\n\n3. OAuth 토큰 상태 확인")
print("-"*30)
token_endpoint = '/api/debug/token'
try:
    response = requests.get(f'{base_url}{token_endpoint}')
    if response.status_code == 200:
        token_info = response.json()
        print(f"토큰 존재: {token_info.get('has_token', False)}")
        print(f"토큰 유효: {token_info.get('is_valid', False)}")
        if 'expires_in' in token_info:
            print(f"만료까지: {token_info['expires_in']}초")
        if 'mall_id' in token_info:
            print(f"Mall ID: {token_info['mall_id']}")
except Exception as e:
    print(f"토큰 확인 실패: {str(e)}")

# 4. 테스트 요약
print("\n\n4. 테스트 결과 요약")
print("-"*30)
success_count = sum(1 for r in test_results.values() if r['status'] == 'OK')
error_count = sum(1 for r in test_results.values() if 'ERROR' in str(r['status']))
exception_count = sum(1 for r in test_results.values() if r['status'] == 'EXCEPTION')

print(f"성공: {success_count}")
print(f"오류: {error_count}")
print(f"예외: {exception_count}")

# 5. 문제 진단
print("\n\n5. 문제 진단")
print("-"*30)
if error_count > 0 or exception_count > 0:
    print("❌ API 연결에 문제가 있습니다.")
    print("\n가능한 원인:")
    print("1. OAuth 토큰 만료 또는 무효")
    print("2. Cafe24 API 연결 문제")
    print("3. 데모 모드로 전환됨")
    print("4. 환경변수 설정 문제")
else:
    print("✅ API 연결 상태 양호")

# 6. 권장 조치
print("\n\n6. 권장 조치")
print("-"*30)
print("1. Render 대시보드에서 로그 확인")
print("   https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/logs")
print("2. 환경변수 확인 (특히 CAFE24_CLIENT_ID, CLIENT_SECRET)")
print("3. OAuth 토큰 갱신 필요 여부 확인")
print("4. 로컬에서 app.py 실행하여 비교 테스트")

# 결과 파일로 저장
result_file = f'render_test_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump({
        'test_time': datetime.now().isoformat(),
        'server': base_url,
        'results': test_results,
        'summary': {
            'success': success_count,
            'error': error_count,
            'exception': exception_count
        }
    }, f, indent=2, ensure_ascii=False)

print(f"\n\n📁 테스트 결과 저장됨: {result_file}")