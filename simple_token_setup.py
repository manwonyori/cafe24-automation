#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 간단 토큰 설정
개발자센터에서 토큰을 받아 바로 설정합니다
"""

import json
import os
import webbrowser
from datetime import datetime, timedelta

def simple_setup():
    """간단한 토큰 설정"""
    
    print("=" * 60)
    print("Cafe24 Simple Token Setup")
    print("=" * 60)
    
    print("\n[METHOD 1] Use the code from URL")
    print("If you see a URL like:")
    print("https://cafe24-automation.onrender.com/callback?code=ABC123...")
    print("The 'ABC123...' part is your authorization code!")
    
    print("\n[METHOD 2] Get token from Developer Center (Easier)")
    print("Opening Cafe24 Developer Center...")
    
    # 개발자센터 열기
    webbrowser.open("https://developers.cafe24.com")
    
    print("\nSteps:")
    print("1. Login to Cafe24")
    print("2. Click '내 앱' (My Apps)")
    print("3. Select your app")
    print("4. Go to '인증 정보' (Authentication)")
    print("5. Find '테스트 Access Token' section")
    print("6. Click '토큰 발급' (Issue Token)")
    print("7. Select all permissions")
    print("8. Click '생성' (Generate)")
    
    print("\n" + "-" * 60)
    print("Choose your method:")
    print("1. I have an authorization code from the URL")
    print("2. I will get a token from Developer Center")
    print("-" * 60)
    
    # 설정 파일 경로
    config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
    
    # 기존 설정 로드
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 입력 받기
    access_token = input("\nPaste your Access Token here: ").strip()
    
    if not access_token:
        print("\n[ERROR] Token is required!")
        return False
    
    # 토큰 업데이트
    config['access_token'] = access_token
    config['expires_at'] = (datetime.now() + timedelta(hours=2)).isoformat()
    
    # Refresh token (선택사항)
    refresh_token = input("Paste Refresh Token (optional, press Enter to skip): ").strip()
    if refresh_token:
        config['refresh_token'] = refresh_token
    
    # 설정 저장
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("\n[SUCCESS] Configuration saved!")
    
    # Render 환경변수 파일 생성
    create_env_file(config)
    
    # 테스트
    test_api(config)
    
    return True

def create_env_file(config):
    """환경변수 파일 생성"""
    env_content = f"""# Cafe24 Environment Variables
# Copy this to Render.com

CAFE24_MALL_ID={config['mall_id']}
CAFE24_CLIENT_ID={config['client_id']}
CAFE24_CLIENT_SECRET={config['client_secret']}
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={config['access_token']}
CAFE24_REFRESH_TOKEN={config.get('refresh_token', '')}
"""
    
    filename = "render_env_simple.txt"
    with open(filename, "w") as f:
        f.write(env_content)
    
    print(f"\n[CREATED] {filename}")
    print("\nNext steps:")
    print("1. Copy the contents of", filename)
    print("2. Go to: https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env")
    print("3. Update environment variables")
    print("4. Click 'Save Changes'")
    print("5. Click 'Manual Deploy' -> 'Deploy latest commit'")

def test_api(config):
    """API 테스트"""
    print("\n[TESTING] API Connection...")
    
    try:
        import requests
        
        url = f"https://{config['mall_id']}.cafe24api.com/api/v2/products?limit=1"
        headers = {
            'Authorization': f'Bearer {config["access_token"]}',
            'Content-Type': 'application/json',
            'X-Cafe24-Api-Version': '2025-06-01'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("[OK] API connection successful!")
            data = response.json()
            print(f"Found {len(data.get('products', []))} products")
        else:
            print(f"[ERROR] API returned {response.status_code}")
            print("Response:", response.text[:200])
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")

def main():
    """메인 함수"""
    if simple_setup():
        print("\n" + "=" * 60)
        print("Setup Complete!")
        print("=" * 60)
        print("\nYour token has been saved and is ready to use.")
        print("Don't forget to update Render environment variables!")
    else:
        print("\nSetup failed. Please try again.")

if __name__ == "__main__":
    main()