#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redirect URI 문제 해결 및 대안 제공
"""

import webbrowser

def show_solutions():
    """Redirect URI 문제 해결 방법"""
    
    print("=" * 60)
    print("Cafe24 OAuth Redirect URI Error Solution")
    print("=" * 60)
    
    print("\n[PROBLEM]")
    print("The redirect_uri is not matching in Cafe24 Developer Center")
    
    print("\n[SOLUTION 1] Check Cafe24 Developer Center Settings")
    print("1. Go to: https://developers.cafe24.com")
    print("2. Login and select your app")
    print("3. Check 'Redirect URI(s)' field")
    print("4. Make sure it contains EXACTLY:")
    print("   https://cafe24-automation.onrender.com/callback")
    print("5. If not, add it and save")
    
    print("\n[SOLUTION 2] Use Developer Center Token (Fastest!)")
    print("Skip OAuth completely and get token directly:")
    print("\n1. Opening Developer Center...")
    
    # 개발자센터 열기
    webbrowser.open("https://developers.cafe24.com")
    
    print("\n2. Steps to get token:")
    print("   a) Login with your Cafe24 account")
    print("   b) Go to 'My Apps' (내 앱)")
    print("   c) Select your app (만원요리 자동화)")
    print("   d) Click 'Authentication' tab (인증 정보)")
    print("   e) Scroll to 'Test Access Token' section")
    print("   f) Click 'Issue Token' (토큰 발급)")
    print("   g) Check all permissions:")
    print("      - mall.read_product")
    print("      - mall.write_product")
    print("      - mall.read_order")
    print("      - mall.write_order")
    print("      - mall.read_customer")
    print("   h) Click 'Generate' (생성)")
    print("   i) Copy the Access Token and Refresh Token")
    
    print("\n[SOLUTION 3] Alternative Redirect URIs")
    print("Try these variations in Developer Center:")
    print("- https://cafe24-automation.onrender.com/callback")
    print("- https://cafe24-automation.onrender.com/callback/")
    print("- https://cafe24-automation-vvkx.onrender.com/callback")
    
    print("\n" + "-" * 60)
    print("After getting the token, paste it below:")
    print("-" * 60)
    
    # 토큰 입력 받기
    access_token = input("\nAccess Token: ").strip()
    
    if access_token:
        refresh_token = input("Refresh Token (optional): ").strip()
        save_tokens(access_token, refresh_token)
    else:
        print("\nNo token entered. Please try again.")

def save_tokens(access_token, refresh_token=""):
    """토큰 저장 및 배포 준비"""
    import json
    from datetime import datetime, timedelta
    
    # 설정 로드
    config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 토큰 업데이트
    config['access_token'] = access_token
    if refresh_token:
        config['refresh_token'] = refresh_token
    config['expires_at'] = (datetime.now() + timedelta(hours=2)).isoformat()
    
    # 저장
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("\n[SUCCESS] Tokens saved!")
    
    # Render 환경변수 파일 생성
    env_content = f"""# Cafe24 Environment Variables
# Copy these to Render.com

CAFE24_MALL_ID={config['mall_id']}
CAFE24_CLIENT_ID={config['client_id']}
CAFE24_CLIENT_SECRET={config['client_secret']}
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={access_token}
CAFE24_REFRESH_TOKEN={refresh_token or config.get('refresh_token', '')}
"""
    
    with open("render_env_working.txt", "w") as f:
        f.write(env_content)
    
    print("\n[NEXT STEPS]")
    print("1. Copy contents of render_env_working.txt")
    print("2. Go to: https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env")
    print("3. Update environment variables")
    print("4. Save Changes")
    print("5. Manual Deploy -> Deploy latest commit")
    
    # API 테스트
    test_token(config)

def test_token(config):
    """토큰 테스트"""
    import requests
    
    print("\n[TESTING] Token validity...")
    
    test_url = f"https://{config['mall_id']}.cafe24api.com/api/v2/products?limit=1"
    headers = {
        'Authorization': f'Bearer {config["access_token"]}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': '2025-06-01'
    }
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("[OK] Token is working!")
            print("Your Cafe24 automation is ready!")
            print("\nDashboard: https://cafe24-automation.onrender.com/")
        else:
            print(f"[ERROR] API returned {response.status_code}")
            print("Please check the token and permissions")
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")

def main():
    show_solutions()
    
    print("\n" + "=" * 60)
    print("Remember: Developer Center method is the easiest!")
    print("=" * 60)

if __name__ == "__main__":
    main()