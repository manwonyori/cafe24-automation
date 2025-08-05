#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카페24 시스템 간단 진단 보고서
핵심 문제점과 해결방안을 제시합니다.
"""
import os
import json
import requests
from datetime import datetime, timedelta

def check_token_status():
    """토큰 상태 확인"""
    print("1. 토큰 상태 확인")
    print("-" * 30)
    
    if os.path.exists('oauth_token.json'):
        try:
            with open('oauth_token.json', 'r', encoding='utf-8') as f:
                token_data = json.load(f)
            
            access_token = token_data.get('access_token')
            expires_at = token_data.get('expires_at', '')
            mall_id = token_data.get('mall_id')
            
            print(f"[정상] 토큰 파일 존재: oauth_token.json")
            print(f"[정상] Mall ID: {mall_id}")
            print(f"[정상] 토큰: ***{access_token[-10:] if access_token else 'None'}")
            
            # 만료 시간 확인
            if expires_at:
                try:
                    expire_time = datetime.fromisoformat(expires_at.replace('.000', ''))
                    now = datetime.now()
                    if expire_time > now:
                        print(f"[정상] 토큰 상태: 유효 (만료: {expire_time})")
                        return True, token_data
                    else:
                        print(f"[만료] 토큰 상태: 만료됨 (만료: {expire_time})")
                        return False, token_data
                except:
                    print("[오류] 토큰 만료 시간 파싱 실패")
                    return False, token_data
            else:
                print("[오류] 만료 시간 정보 없음")
                return False, token_data
                
        except Exception as e:
            print(f"[오류] 토큰 파일 읽기 실패: {str(e)}")
            return False, None
    else:
        print("[오류] 토큰 파일 없음")
        return False, None

def test_api_connection(token_data):
    """API 연결 테스트"""
    print("\n2. API 연결 테스트")
    print("-" * 30)
    
    if not token_data:
        print("[오류] 토큰 데이터 없음 - API 테스트 불가")
        return False
    
    access_token = token_data.get('access_token')
    mall_id = token_data.get('mall_id')
    
    if not access_token or not mall_id:
        print("[오류] 필수 토큰 정보 누락")
        return False
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': '2025-06-01'
    }
    
    # 상품 수량 조회로 테스트
    test_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/count"
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        print(f"[정상] API 호출: {test_url}")
        print(f"[정상] 응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"[정상] 상품 수량: {count}개")
            return True
        elif response.status_code == 401:
            print("[실패] 인증 실패: 토큰이 만료되었거나 잘못되었습니다")
            return False
        else:
            print(f"[실패] API 오류: {response.status_code} - {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"[실패] API 호출 실패: {str(e)}")
        return False

def test_deployed_service():
    """배포된 서비스 테스트"""
    print("\n3. 배포된 서비스 테스트")
    print("-" * 30)
    
    service_url = "https://cafe24-automation.onrender.com"
    
    try:
        # 메인 페이지 테스트
        response = requests.get(service_url, timeout=15)
        print(f"[정상] 서비스 URL: {service_url}")
        print(f"[정상] 응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            print("[정상] 서비스 상태: 정상 운영 중")
            
            # 상태 페이지 테스트
            status_response = requests.get(f"{service_url}/api/status", timeout=15)
            if status_response.status_code == 200:
                status_data = status_response.json()
                token_valid = status_data.get('token_status', {}).get('valid', False)
                print(f"[정상] 서버의 토큰 상태: {'유효' if token_valid else '무효'}")
                return True
            else:
                print("[실패] 상태 API 호출 실패")
                return False
        else:
            print(f"[실패] 서비스 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[실패] 서비스 연결 실패: {str(e)}")
        return False

def check_local_modules():
    """로컬 모듈 확인"""
    print("\n4. 핵심 모듈 확인")
    print("-" * 30)
    
    critical_modules = [
        'app.py',
        'config.py',
        'sales_analytics.py',
        'market_intelligence_system.py',
        'auto_token_manager.py'
    ]
    
    missing_modules = []
    existing_modules = []
    
    for module in critical_modules:
        if os.path.exists(module):
            existing_modules.append(module)
            print(f"[정상] {module} 존재")
        else:
            missing_modules.append(module)
            print(f"[누락] {module} 없음")
    
    return len(missing_modules) == 0, existing_modules, missing_modules

def generate_diagnosis_report():
    """진단 보고서 생성"""
    print("=" * 50)
    print("카페24 시스템 진단 보고서")
    print("=" * 50)
    print(f"진단 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 토큰 확인
    token_valid, token_data = check_token_status()
    
    # 2. API 연결 확인
    api_working = test_api_connection(token_data)
    
    # 3. 배포 서비스 확인
    service_working = test_deployed_service()
    
    # 4. 로컬 모듈 확인
    modules_complete, existing, missing = check_local_modules()
    
    # 5. 종합 진단
    print("\n5. 종합 진단 결과")
    print("-" * 30)
    
    issues = []
    recommendations = []
    
    if not token_valid:
        issues.append("토큰 만료")
        recommendations.append("1. 새 인증 코드로 토큰 재발급 필요")
        recommendations.append("   - Cafe24 Developer Center에서 새 인증 코드 생성")
        recommendations.append("   - exchange_auth_code.py 스크립트 사용")
    
    if not api_working:
        issues.append("API 연결 실패")
        if token_valid:
            recommendations.append("2. API 권한 또는 네트워크 문제 확인 필요")
    
    if not service_working:
        issues.append("배포 서비스 문제")
        recommendations.append("3. Render 서비스 환경변수 확인 필요")
    
    if not modules_complete:
        issues.append("핵심 모듈 누락")
        recommendations.append(f"4. 누락된 모듈 복구 필요: {', '.join(missing)}")
    
    print(f"[요약] 발견된 문제: {len(issues)}개")
    for issue in issues:
        print(f"  - {issue}")
    
    print(f"\n[요약] 정상 작동 부분:")
    if token_data:
        print("  - 토큰 파일 구조 정상")
    if service_working:
        print("  - 배포 서비스 정상")
    if existing:
        print(f"  - 로컬 모듈 {len(existing)}개 정상")
    
    print(f"\n6. 해결 방안")
    print("-" * 30)
    
    if recommendations:
        for rec in recommendations:
            print(rec)
    else:
        print("[완료] 모든 시스템이 정상 작동 중입니다!")
    
    # 우선순위 판단
    print(f"\n7. 긴급도 판정")
    print("-" * 30)
    
    if not token_valid:
        print("[긴급] 토큰 만료로 인해 데이터 조회가 불가능합니다.")
        print("       즉시 토큰 재발급이 필요합니다.")
    elif not api_working:
        print("[주의] API 연결에 문제가 있습니다.")
        print("       API 설정과 권한을 확인하세요.")
    else:
        print("[정상] 핵심 기능이 정상 작동 중입니다.")
    
    print("\n" + "=" * 50)
    
    return {
        'token_valid': token_valid,
        'api_working': api_working,
        'service_working': service_working,
        'modules_complete': modules_complete,
        'issues': issues,
        'recommendations': recommendations
    }

if __name__ == '__main__':
    # 현재 디렉토리를 스크립트 위치로 변경
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 진단 실행
    result = generate_diagnosis_report()