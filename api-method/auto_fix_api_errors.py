#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 API 오류 자동 진단 및 수정
상품 API와 주문 API 오류를 자동으로 해결합니다
"""

import json
import requests
import os
import subprocess
from datetime import datetime, timedelta
import time

class AutoFixAPIErrors:
    """API 오류 자동 수정 클래스"""
    
    def __init__(self):
        self.config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
        self.render_url = "https://cafe24-automation.onrender.com"
        self.load_config()
        
    def load_config(self):
        """설정 로드"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            
    def diagnose_and_fix(self):
        """문제 진단 및 자동 수정"""
        print("=" * 80)
        print("Cafe24 API Error Auto-Fix System")
        print("=" * 80)
        
        # 1. 현재 API 상태 확인
        print("\n[STEP 1] Checking current API status...")
        api_status = self.check_api_status()
        
        # 2. 토큰 상태 확인
        print("\n[STEP 2] Checking token validity...")
        token_status = self.check_token_status()
        
        # 3. 문제 진단
        print("\n[STEP 3] Diagnosing issues...")
        issues = self.diagnose_issues(api_status, token_status)
        
        # 4. 자동 수정
        print("\n[STEP 4] Applying automatic fixes...")
        self.apply_fixes(issues)
        
        # 5. 수정 후 재테스트
        print("\n[STEP 5] Retesting after fixes...")
        self.retest_apis()
        
        # 6. 최종 보고서
        self.generate_fix_report()
        
    def check_api_status(self):
        """API 상태 확인"""
        results = {}
        
        # Render 서버의 API 테스트
        endpoints = {
            "health": f"{self.render_url}/health",
            "products": f"{self.render_url}/api/products",
            "orders": f"{self.render_url}/api/orders",
            "test": f"{self.render_url}/api/test"
        }
        
        for name, url in endpoints.items():
            try:
                response = requests.get(url, timeout=10)
                results[name] = {
                    "status": response.status_code,
                    "ok": response.status_code == 200,
                    "data": response.json() if response.status_code == 200 else response.text[:200]
                }
                print(f"  {name}: {'OK' if results[name]['ok'] else f'ERROR ({response.status_code})'}")
            except Exception as e:
                results[name] = {
                    "status": 0,
                    "ok": False,
                    "data": str(e)
                }
                print(f"  {name}: CONNECTION ERROR")
                
        return results
        
    def check_token_status(self):
        """토큰 상태 확인"""
        # 직접 Cafe24 API 호출
        headers = {
            'Authorization': f'Bearer {self.config["access_token"]}',
            'Content-Type': 'application/json',
            'X-Cafe24-Api-Version': '2025-06-01'
        }
        
        test_url = f"https://{self.config['mall_id']}.cafe24api.com/api/v2/products?limit=1"
        
        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            return {
                "valid": response.status_code == 200,
                "status_code": response.status_code,
                "expires_at": self.config.get("expires_at", "Unknown")
            }
        except:
            return {
                "valid": False,
                "status_code": 0,
                "expires_at": self.config.get("expires_at", "Unknown")
            }
            
    def diagnose_issues(self, api_status, token_status):
        """문제 진단"""
        issues = []
        
        # 토큰 만료 확인
        if not token_status["valid"]:
            if token_status["status_code"] in [401, 403]:
                issues.append("TOKEN_EXPIRED")
            else:
                issues.append("TOKEN_INVALID")
                
        # API 오류 확인
        if not api_status.get("products", {}).get("ok"):
            issues.append("PRODUCTS_API_ERROR")
            
        if not api_status.get("orders", {}).get("ok"):
            issues.append("ORDERS_API_ERROR")
            
        # Render 서버 연결 확인
        if not api_status.get("health", {}).get("ok"):
            issues.append("RENDER_SERVER_DOWN")
            
        print(f"\nIdentified issues: {issues}")
        return issues
        
    def apply_fixes(self, issues):
        """문제 자동 수정"""
        
        if "TOKEN_EXPIRED" in issues or "TOKEN_INVALID" in issues:
            print("\n[FIX] Refreshing access token...")
            self.refresh_token()
            
        if "RENDER_SERVER_DOWN" in issues:
            print("\n[FIX] Render server may be sleeping. Waking up...")
            self.wake_render_server()
            
        if "PRODUCTS_API_ERROR" in issues or "ORDERS_API_ERROR" in issues:
            print("\n[FIX] Updating Render environment variables...")
            self.update_render_env()
            
    def refresh_token(self):
        """토큰 갱신"""
        if not self.config.get('refresh_token'):
            print("  [ERROR] No refresh token available")
            print("  [ACTION] Please get new tokens from Developer Center")
            self.provide_token_instructions()
            return
            
        # Refresh token 사용
        refresh_url = f"https://{self.config['mall_id']}.cafe24api.com/api/v2/oauth/token"
        
        import base64
        auth_header = base64.b64encode(
            f"{self.config['client_id']}:{self.config['client_secret']}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.config['refresh_token']
        }
        
        try:
            response = requests.post(refresh_url, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.config['access_token'] = token_data['access_token']
                self.config['refresh_token'] = token_data.get('refresh_token', self.config['refresh_token'])
                self.config['expires_at'] = (datetime.now() + timedelta(seconds=token_data.get('expires_in', 7200))).isoformat()
                
                # 저장
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                    
                print("  [SUCCESS] Token refreshed!")
                
                # Render 환경변수 업데이트
                self.create_updated_env()
                
            else:
                print(f"  [ERROR] Token refresh failed: {response.status_code}")
                self.provide_token_instructions()
                
        except Exception as e:
            print(f"  [ERROR] Token refresh exception: {e}")
            
    def wake_render_server(self):
        """Render 서버 깨우기"""
        print("  Sending wake-up request...")
        try:
            requests.get(f"{self.render_url}/health", timeout=30)
            print("  [OK] Server wake-up request sent")
            print("  Waiting 30 seconds for server to fully start...")
            time.sleep(30)
        except:
            print("  [WARNING] Could not reach server")
            
    def update_render_env(self):
        """Render 환경변수 업데이트 안내"""
        self.create_updated_env()
        
        print("\n[ACTION REQUIRED] Update Render environment variables:")
        print("1. Open FIXED_ENV.txt")
        print("2. Copy all contents")
        print("3. Go to: https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env")
        print("4. Replace all variables")
        print("5. Save Changes")
        print("6. Manual Deploy")
        
    def create_updated_env(self):
        """업데이트된 환경변수 파일 생성"""
        env_content = f"""# FIXED ENVIRONMENT VARIABLES
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CAFE24_MALL_ID={self.config['mall_id']}
CAFE24_CLIENT_ID={self.config['client_id']}
CAFE24_CLIENT_SECRET={self.config['client_secret']}
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={self.config['access_token']}
CAFE24_REFRESH_TOKEN={self.config.get('refresh_token', '')}
ENABLE_AUTO_REFRESH=true
ENABLE_DASHBOARD=true
ENABLE_API_ENDPOINTS=true
PRODUCTION_MODE=true
LOG_LEVEL=INFO
"""
        
        with open("FIXED_ENV.txt", "w") as f:
            f.write(env_content)
            
        print("  [CREATED] FIXED_ENV.txt with updated tokens")
        
    def retest_apis(self):
        """수정 후 재테스트"""
        print("\nRetesting APIs...")
        
        # 잠시 대기
        time.sleep(5)
        
        # 재테스트
        final_status = self.check_api_status()
        
        print("\n[FINAL STATUS]")
        all_ok = True
        for name, result in final_status.items():
            status = "OK" if result["ok"] else f"STILL ERROR ({result['status']})"
            print(f"  {name}: {status}")
            if not result["ok"]:
                all_ok = False
                
        return all_ok
        
    def provide_token_instructions(self):
        """토큰 재발급 안내"""
        print("\n[MANUAL TOKEN REFRESH REQUIRED]")
        print("1. Go to: https://developers.cafe24.com")
        print("2. Login -> My Apps -> Your App")
        print("3. Authentication -> Test Access Token")
        print("4. Issue Token -> Check all permissions -> Generate")
        print("5. Run: python simple_token_setup.py")
        
    def generate_fix_report(self):
        """수정 보고서 생성"""
        report = f"""# API Error Fix Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Actions Taken:
1. Diagnosed API connection issues
2. Checked token validity
3. Applied automatic fixes
4. Created updated environment variables

## Next Steps:
1. If tokens were refreshed, update Render environment
2. Wait 5 minutes for deployment
3. Test again at: https://cafe24-automation.onrender.com/

## Manual Actions Required:
- Update Render environment variables with FIXED_ENV.txt
- Redeploy the service
- Monitor for 5 minutes

## Support:
If issues persist:
1. Check Render logs
2. Verify Cafe24 app permissions
3. Ensure tokens are valid
"""
        
        with open("API_FIX_REPORT.md", "w") as f:
            f.write(report)
            
        print("\n[SAVED] API_FIX_REPORT.md")
        
def main():
    """메인 실행"""
    fixer = AutoFixAPIErrors()
    fixer.diagnose_and_fix()
    
    print("\n" + "=" * 80)
    print("Auto-fix process completed!")
    print("Check API_FIX_REPORT.md for details")
    print("=" * 80)

if __name__ == "__main__":
    main()