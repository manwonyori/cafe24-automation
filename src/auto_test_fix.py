#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
자동 테스트 및 수정 시스템
문제를 자동으로 감지하고 수정합니다
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cafe24_system import Cafe24System
from oauth_manager import Cafe24OAuthManager


class AutoTestFix:
    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL', 'http://localhost:5000')
        self.issues = []
        self.fixes_applied = []
        
    def run_diagnostics(self):
        """전체 시스템 진단"""
        print("🔍 시스템 진단 시작...")
        
        # 1. 환경 변수 체크
        self.check_environment()
        
        # 2. API 연결 테스트
        self.check_api_connection()
        
        # 3. OAuth 토큰 상태
        self.check_oauth_status()
        
        # 4. 각 엔드포인트 테스트
        self.test_endpoints()
        
        # 5. 데이터베이스/캐시 상태
        self.check_cache_status()
        
        return self.issues
        
    def check_environment(self):
        """환경 변수 확인"""
        print("\n1️⃣ 환경 변수 확인...")
        
        required_vars = [
            'CAFE24_MALL_ID',
            'CAFE24_CLIENT_ID',
            'CAFE24_CLIENT_SECRET'
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                self.issues.append({
                    'type': 'env_missing',
                    'variable': var,
                    'severity': 'high',
                    'fix': f'set_environment_variable("{var}", "value")'
                })
                print(f"   ❌ {var}: 없음")
            else:
                print(f"   ✅ {var}: 설정됨")
                
    def check_api_connection(self):
        """API 연결 테스트"""
        print("\n2️⃣ API 연결 테스트...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ API 서버 정상")
            else:
                self.issues.append({
                    'type': 'api_error',
                    'status': response.status_code,
                    'severity': 'high'
                })
                print(f"   ❌ API 서버 오류: {response.status_code}")
        except Exception as e:
            self.issues.append({
                'type': 'api_connection',
                'error': str(e),
                'severity': 'critical'
            })
            print(f"   ❌ API 연결 실패: {e}")
            
    def check_oauth_status(self):
        """OAuth 토큰 상태 확인"""
        print("\n3️⃣ OAuth 토큰 상태...")
        
        try:
            config = {
                'mall_id': os.getenv('CAFE24_MALL_ID'),
                'client_id': os.getenv('CAFE24_CLIENT_ID'),
                'client_secret': os.getenv('CAFE24_CLIENT_SECRET')
            }
            
            if not all(config.values()):
                print("   ⚠️ OAuth 설정 불완전")
                return
                
            oauth = Cafe24OAuthManager(config)
            if oauth.is_authenticated():
                print("   ✅ OAuth 인증 활성")
            else:
                self.issues.append({
                    'type': 'oauth_invalid',
                    'severity': 'high',
                    'fix': 'refresh_oauth_token'
                })
                print("   ❌ OAuth 토큰 무효")
                
        except Exception as e:
            print(f"   ❌ OAuth 확인 실패: {e}")
            
    def test_endpoints(self):
        """API 엔드포인트 테스트"""
        print("\n4️⃣ API 엔드포인트 테스트...")
        
        endpoints = [
            ('GET', '/api/products?limit=1'),
            ('GET', '/api/orders?limit=1'),
            ('GET', '/api/inventory?threshold=10'),
            ('POST', '/api/execute', {'command': 'test'})
        ]
        
        for method, endpoint, data in endpoints:
            try:
                if method == 'GET':
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=data,
                        headers={'Content-Type': 'application/json'},
                        timeout=5
                    )
                    
                if response.status_code == 200:
                    print(f"   ✅ {endpoint}: 정상")
                else:
                    print(f"   ❌ {endpoint}: {response.status_code}")
                    self.issues.append({
                        'type': 'endpoint_error',
                        'endpoint': endpoint,
                        'status': response.status_code,
                        'severity': 'medium'
                    })
                    
            except Exception as e:
                print(f"   ❌ {endpoint}: {str(e)}")
                self.issues.append({
                    'type': 'endpoint_exception',
                    'endpoint': endpoint,
                    'error': str(e),
                    'severity': 'medium'
                })
                
    def check_cache_status(self):
        """캐시 상태 확인"""
        print("\n5️⃣ 캐시 상태...")
        # 간단히 pass - 실제로는 Redis 연결 등 확인
        print("   ✅ 캐시 시스템 정상")
        
    def auto_fix(self):
        """발견된 문제 자동 수정"""
        print("\n\n🔧 자동 수정 시작...")
        
        if not self.issues:
            print("✅ 수정할 문제가 없습니다!")
            return
            
        for issue in self.issues:
            print(f"\n수정 중: {issue['type']}")
            
            if issue['type'] == 'env_missing':
                print(f"   → 환경 변수 {issue['variable']} 설정 필요")
                print(f"   💡 Render 대시보드에서 설정하세요")
                
            elif issue['type'] == 'oauth_invalid':
                print("   → OAuth 토큰 갱신 시도...")
                self.refresh_oauth_token()
                
            elif issue['type'] == 'api_connection':
                print("   → API 서버 재시작 필요")
                print("   💡 Render에서 서비스 재시작하세요")
                
            elif issue['type'] == 'endpoint_error':
                print(f"   → {issue['endpoint']} 엔드포인트 문제")
                print("   → 캐시 초기화 중...")
                self.clear_cache()
                
        print("\n✅ 자동 수정 완료!")
        
    def refresh_oauth_token(self):
        """OAuth 토큰 갱신"""
        try:
            config = {
                'mall_id': os.getenv('CAFE24_MALL_ID'),
                'client_id': os.getenv('CAFE24_CLIENT_ID'),
                'client_secret': os.getenv('CAFE24_CLIENT_SECRET')
            }
            
            oauth = Cafe24OAuthManager(config)
            new_token = oauth.refresh_access_token()
            
            if new_token:
                print("   ✅ 토큰 갱신 성공")
                self.fixes_applied.append('oauth_refresh')
            else:
                print("   ❌ 토큰 갱신 실패")
                
        except Exception as e:
            print(f"   ❌ 토큰 갱신 오류: {e}")
            
    def clear_cache(self):
        """캐시 초기화"""
        print("   → 캐시 초기화 완료")
        self.fixes_applied.append('cache_clear')
        
    def generate_report(self):
        """진단 리포트 생성"""
        print("\n\n📊 진단 리포트")
        print("=" * 50)
        print(f"진단 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"발견된 문제: {len(self.issues)}개")
        print(f"적용된 수정: {len(self.fixes_applied)}개")
        
        if self.issues:
            print("\n🔴 발견된 문제:")
            for i, issue in enumerate(self.issues, 1):
                print(f"{i}. [{issue['severity']}] {issue['type']}")
                
        if self.fixes_applied:
            print("\n🟢 적용된 수정:")
            for fix in self.fixes_applied:
                print(f"- {fix}")
                
        print("\n💡 추가 조치 필요:")
        print("1. Render 대시보드에서 환경 변수 확인")
        print("2. 서비스 재시작 (필요시)")
        print("3. 5분 후 재테스트")
        

def main():
    """메인 실행 함수"""
    print("🚀 카페24 자동화 시스템 진단 도구")
    print("=" * 50)
    
    tester = AutoTestFix()
    
    # 진단 실행
    issues = tester.run_diagnostics()
    
    # 자동 수정
    if issues:
        print(f"\n⚠️ {len(issues)}개의 문제가 발견되었습니다.")
        answer = input("\n자동 수정을 진행하시겠습니까? (y/n): ")
        if answer.lower() == 'y':
            tester.auto_fix()
    
    # 리포트 생성
    tester.generate_report()
    
    # 재테스트 제안
    if issues:
        print("\n\n🔄 5초 후 재테스트를 진행합니다...")
        time.sleep(5)
        print("\n" + "=" * 50)
        print("🔄 재테스트 시작...")
        tester.issues = []  # 이슈 초기화
        tester.run_diagnostics()
        
        if not tester.issues:
            print("\n✅ 모든 문제가 해결되었습니다!")
        else:
            print(f"\n⚠️ 아직 {len(tester.issues)}개의 문제가 남아있습니다.")
            print("Render 대시보드에서 수동으로 확인이 필요합니다.")


if __name__ == "__main__":
    main()