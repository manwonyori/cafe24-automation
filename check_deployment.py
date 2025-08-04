#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
배포 상태 확인 스크립트
"""
import requests
import time
import json
from datetime import datetime

def check_deployment():
    """배포 상태 확인"""
    base_url = "https://cafe24-automation.onrender.com"
    
    print("=" * 50)
    print("Cafe24 Automation 배포 상태 확인")
    print("=" * 50)
    
    checks = [
        ("/health", "헬스체크"),
        ("/api/status", "API 상태"),
        ("/api/debug/token", "토큰 디버그"),
        ("/", "메인 페이지")
    ]
    
    all_success = True
    
    for endpoint, name in checks:
        url = base_url + endpoint
        try:
            print(f"\n[{name}] 확인 중... {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"[OK] 성공 (HTTP {response.status_code})")
                
                # JSON 응답인 경우 내용 표시
                try:
                    data = response.json()
                    if endpoint == "/api/debug/token":
                        print(f"  - 토큰 존재: {data.get('has_token', False)}")
                        print(f"  - 자동 갱신: {data.get('auto_refresh_active', False)}")
                        if data.get('remaining_minutes'):
                            print(f"  - 남은 시간: {data.get('remaining_minutes', 0):.1f}분")
                    elif endpoint == "/api/status":
                        print(f"  - 서버 상태: {data.get('status', 'unknown')}")
                        print(f"  - 버전: {data.get('server', {}).get('version', 'unknown')}")
                        token_info = data.get('token_status', {})
                        print(f"  - 토큰 유효: {token_info.get('valid', False)}")
                except:
                    pass
                    
            elif response.status_code == 404:
                print(f"[FAIL] 실패 (HTTP 404) - 아직 배포되지 않음")
                all_success = False
            else:
                print(f"[FAIL] 실패 (HTTP {response.status_code})")
                all_success = False
                
        except requests.exceptions.ConnectionError:
            print(f"[FAIL] 연결 실패 - 서버가 아직 시작되지 않음")
            all_success = False
        except requests.exceptions.Timeout:
            print(f"[FAIL] 시간 초과")
            all_success = False
        except Exception as e:
            print(f"[FAIL] 오류: {str(e)}")
            all_success = False
    
    print("\n" + "=" * 50)
    if all_success:
        print("[SUCCESS] 배포 완료! 모든 엔드포인트가 정상 작동 중입니다.")
    else:
        print("[WAITING] 아직 배포 중입니다. 잠시 후 다시 확인하세요.")
    print("=" * 50)
    
    return all_success

def monitor_deployment(check_interval=30, max_attempts=20):
    """배포 완료까지 모니터링"""
    print(f"배포 모니터링 시작 ({check_interval}초마다 확인)")
    print(f"최대 {max_attempts}회 시도 (약 {max_attempts * check_interval / 60:.1f}분)")
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n시도 {attempt}/{max_attempts} - {datetime.now().strftime('%H:%M:%S')}")
        
        if check_deployment():
            print("\n[COMPLETE] 배포가 성공적으로 완료되었습니다!")
            return True
        
        if attempt < max_attempts:
            print(f"\n{check_interval}초 후 재시도...")
            time.sleep(check_interval)
    
    print("\n[WARNING] 최대 시도 횟수를 초과했습니다. Render 대시보드를 직접 확인하세요.")
    return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        # 모니터링 모드
        monitor_deployment()
    else:
        # 단일 체크
        check_deployment()