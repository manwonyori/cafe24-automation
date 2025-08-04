#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 개발자센터에서 직접 토큰 받기
더 간단한 방법으로 토큰을 획득합니다
"""

import json
import os
import webbrowser
import subprocess
from datetime import datetime, timedelta

def get_token_from_dev_center():
    """개발자센터를 통한 토큰 획득"""
    
    print("=" * 60)
    print("Cafe24 Token from Developer Center")
    print("=" * 60)
    
    print("\n[STEP 1] Opening Cafe24 Developer Center...")
    print("URL: https://developers.cafe24.com")
    
    # 개발자센터 열기
    webbrowser.open("https://developers.cafe24.com")
    
    print("\n[STEP 2] Manual Steps:")
    print("1. Login with your Cafe24 account")
    print("2. Go to 'My Apps' (내 앱)")
    print("3. Select your app (만원요리 자동화)")
    print("4. Click 'Authentication' tab (인증 정보)")
    print("5. Scroll down to 'Test Access Token' section")
    print("6. Click 'Issue Token' button (토큰 발급)")
    print("7. Select all permissions (모든 권한 선택)")
    print("8. Click 'Generate' (생성)")
    
    print("\n[STEP 3] Enter the tokens below:")
    print("(You can find these in the popup window)")
    
    access_token = input("\nAccess Token: ").strip()
    refresh_token = input("Refresh Token (optional, press Enter to skip): ").strip()
    
    if not access_token:
        print("\n[ERROR] Access token is required!")
        return False
    
    # 기존 설정 로드
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
    
    print("\n[SUCCESS] Token saved!")
    
    # Render 환경변수 파일 생성
    create_render_env_file(config)
    
    # GitHub 자동 배포 시도
    try_github_deploy(config)
    
    return True

def create_render_env_file(config):
    """Render 환경변수 파일 생성"""
    print("\n[STEP 4] Creating Render environment file...")
    
    env_content = f"""CAFE24_MALL_ID={config['mall_id']}
CAFE24_CLIENT_ID={config['client_id']}
CAFE24_CLIENT_SECRET={config['client_secret']}
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={config['access_token']}
CAFE24_REFRESH_TOKEN={config.get('refresh_token', '')}"""
    
    with open("dev_center_tokens.txt", "w") as f:
        f.write(env_content)
    
    print("[OK] dev_center_tokens.txt created")
    
    print("\n[Manual Deployment]")
    print("1. Copy contents of dev_center_tokens.txt")
    print("2. Go to: https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env")
    print("3. Update environment variables")
    print("4. Click 'Save Changes'")
    print("5. Click 'Manual Deploy'")

def try_github_deploy(config):
    """GitHub Actions 자동 배포 시도"""
    print("\n[STEP 5] Trying automatic deployment...")
    
    try:
        # GitHub CLI 확인
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] GitHub CLI found")
            
            # Secrets 업데이트
            secrets = [
                ('CAFE24_ACCESS_TOKEN', config['access_token']),
                ('CAFE24_REFRESH_TOKEN', config.get('refresh_token', ''))
            ]
            
            for key, value in secrets:
                if value:
                    subprocess.run(
                        ['gh', 'secret', 'set', key],
                        input=value,
                        text=True,
                        capture_output=True
                    )
                    print(f"[OK] {key} updated")
            
            # Workflow 실행
            result = subprocess.run(
                ['gh', 'workflow', 'run', 'auto-deploy.yml'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("[OK] Deployment triggered!")
                print("Monitor: https://github.com/manwonyori/cafe24/actions")
            else:
                print("[WARN] Could not trigger workflow")
        else:
            print("[INFO] GitHub CLI not found, skipping auto-deploy")
            
    except Exception as e:
        print(f"[WARN] Auto-deploy failed: {e}")

def test_token(config):
    """토큰 테스트"""
    print("\n[STEP 6] Testing token...")
    
    import requests
    
    test_url = f"https://{config['mall_id']}.cafe24api.com/api/v2/products?limit=1"
    headers = {
        'Authorization': f'Bearer {config["access_token"]}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': '2025-06-01'
    }
    
    try:
        response = requests.get(test_url, headers=headers)
        
        if response.status_code == 200:
            print("[OK] Token is working!")
            print("API Response:", response.json())
            return True
        else:
            print(f"[ERROR] API returned {response.status_code}")
            print("Response:", response.text)
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

def main():
    """메인 함수"""
    print("Cafe24 Token Helper - Developer Center Method")
    print("This is the easiest way to get tokens!")
    
    if get_token_from_dev_center():
        # 토큰 테스트
        config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        if test_token(config):
            print("\n" + "=" * 60)
            print("SUCCESS! Everything is working!")
            print("=" * 60)
            print("\nYour Cafe24 automation is ready to use:")
            print("- Dashboard: https://cafe24-automation.onrender.com/")
            print("- API Test: https://cafe24-automation.onrender.com/api/test")
        else:
            print("\nToken test failed. Please check:")
            print("1. Token was copied correctly")
            print("2. All permissions were granted")
            print("3. App is approved in Cafe24")
    else:
        print("\nSetup cancelled.")

if __name__ == "__main__":
    main()