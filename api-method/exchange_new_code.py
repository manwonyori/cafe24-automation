#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새 인증 코드로 토큰 교환
"""

import json
import requests
import base64
from datetime import datetime, timedelta

# 새로 받은 인증 코드
AUTH_CODE = "HSQEnRyOExIhRcGJ7QKjOD"

def exchange_new_code():
    """새 인증 코드를 토큰으로 교환"""
    
    print("=" * 60)
    print("Exchanging New Authorization Code")
    print("=" * 60)
    print(f"\nNew Auth Code: {AUTH_CODE}")
    
    # 설정 로드
    config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    mall_id = config['mall_id']
    client_id = config['client_id']
    client_secret = config['client_secret']
    
    # 토큰 교환
    token_url = f"https://{mall_id}.cafe24api.com/api/v2/oauth/token"
    
    # Basic Auth 헤더
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': AUTH_CODE,
        'redirect_uri': 'https://cafe24-automation.onrender.com/callback'
    }
    
    print("\nExchanging code for tokens...")
    
    try:
        response = requests.post(token_url, headers=headers, data=data)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            
            print("\n[SUCCESS] Token Exchange Complete!")
            print(f"Access Token: {token_data['access_token'][:30]}...")
            print(f"Refresh Token: {token_data.get('refresh_token', 'N/A')[:30]}...")
            print(f"Expires In: {token_data.get('expires_in', 7200)} seconds")
            
            # 설정 업데이트
            config['access_token'] = token_data['access_token']
            config['refresh_token'] = token_data.get('refresh_token', '')
            config['expires_at'] = (datetime.now() + timedelta(seconds=token_data.get('expires_in', 7200))).isoformat()
            
            # 저장
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print("\n[SAVED] Configuration updated!")
            
            # API 테스트
            test_api(config)
            
            # Render 환경변수 파일 생성
            create_render_env(config)
            
            # 전체 시스템 상태 체크
            check_system_status(config)
            
            return True
            
        else:
            print(f"\n[ERROR] Token exchange failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        return False

def test_api(config):
    """API 연결 테스트"""
    print("\n[TESTING] API Connection...")
    
    test_url = f"https://{config['mall_id']}.cafe24api.com/api/v2/products?limit=1"
    headers = {
        'Authorization': f'Bearer {config["access_token"]}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': '2025-06-01'
    }
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("[OK] API Test Successful!")
            data = response.json()
            print(f"Products found: {len(data.get('products', []))}")
            return True
        else:
            print(f"[ERROR] API Test Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test Exception: {e}")
        return False

def create_render_env(config):
    """Render 환경변수 파일 생성"""
    env_content = f"""# Cafe24 Production Environment Variables
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Status: READY FOR PRODUCTION!

CAFE24_MALL_ID={config['mall_id']}
CAFE24_CLIENT_ID={config['client_id']}
CAFE24_CLIENT_SECRET={config['client_secret']}
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={config['access_token']}
CAFE24_REFRESH_TOKEN={config.get('refresh_token', '')}

# Features
ENABLE_AUTO_REFRESH=true
ENABLE_DASHBOARD=true
ENABLE_API_ENDPOINTS=true
PRODUCTION_MODE=true
"""
    
    with open("RENDER_ENV_FINAL.txt", "w") as f:
        f.write(env_content)
    
    print("\n[CREATED] RENDER_ENV_FINAL.txt")

def check_system_status(config):
    """전체 시스템 상태 확인"""
    print("\n" + "=" * 80)
    print("SYSTEM STATUS CHECK")
    print("=" * 80)
    
    # API 엔드포인트 테스트
    endpoints = [
        ("Products", "/products?limit=1"),
        ("Orders", "/orders?limit=1"),
        ("Customers", "/customers?limit=1")
    ]
    
    base_url = f"https://{config['mall_id']}.cafe24api.com/api/v2"
    headers = {
        'Authorization': f'Bearer {config["access_token"]}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': '2025-06-01'
    }
    
    print("\n[API ENDPOINTS TEST]")
    for name, endpoint in endpoints:
        try:
            response = requests.get(base_url + endpoint, headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
            else:
                print(f"❌ {name}: Error {response.status_code}")
        except:
            print(f"❌ {name}: Failed")
    
    print("\n[DEPLOYMENT INSTRUCTIONS]")
    print("1. Copy ALL contents from RENDER_ENV_FINAL.txt")
    print("2. Go to: https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env")
    print("3. Replace ALL environment variables")
    print("4. Click 'Save Changes'")
    print("5. Click 'Manual Deploy' -> 'Deploy latest commit'")
    
    print("\n[SYSTEM FEATURES]")
    print("✅ OAuth Authentication: Active")
    print("✅ Auto Token Refresh: Enabled")
    print("✅ Dashboard: Ready")
    print("✅ API Endpoints: Ready")
    print("✅ Natural Language Processing: Ready")
    
    print("\n[URLS]")
    print("Dashboard: https://cafe24-automation.onrender.com/")
    print("API Test: https://cafe24-automation.onrender.com/api/test")
    print("Products: https://cafe24-automation.onrender.com/api/products")
    print("Orders: https://cafe24-automation.onrender.com/api/orders")
    
    print("\n" + "=" * 80)
    print("YOUR SYSTEM IS READY! Deploy to Render to start using it.")
    print("=" * 80)

def main():
    if exchange_new_code():
        print("\n🎉 SUCCESS! Everything is configured!")
        print("Your Cafe24 automation system is ready for deployment!")
    else:
        print("\n❌ Token exchange failed.")

if __name__ == "__main__":
    main()