#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
인증 코드를 토큰으로 교환
"""

import json
import requests
import base64
from datetime import datetime, timedelta

def exchange_auth_code():
    """인증 코드를 Access Token으로 교환"""
    
    # 받은 인증 코드
    auth_code = "A1PPUpyzBZTv8QlKPHvNQA"
    
    print("=" * 60)
    print("Exchanging Authorization Code for Tokens")
    print("=" * 60)
    print(f"\nAuth Code: {auth_code}")
    
    # 설정 로드
    config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    mall_id = config['mall_id']
    client_id = config['client_id']
    client_secret = config['client_secret']
    
    # 토큰 교환 요청
    token_url = f"https://{mall_id}.cafe24api.com/api/v2/oauth/token"
    
    # Basic Auth 헤더
    auth_string = f"{client_id}:{client_secret}"
    auth_header = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
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
            
            print("\n[SAVED] Configuration updated")
            
            # Render 환경변수 파일 생성
            create_render_env(config)
            
            # API 테스트
            test_api(config)
            
            return True
            
        else:
            print(f"\n[ERROR] Token exchange failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        return False

def create_render_env(config):
    """Render 환경변수 파일 생성"""
    env_content = f"""# Cafe24 Environment Variables - Ready to Deploy!
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CAFE24_MALL_ID={config['mall_id']}
CAFE24_CLIENT_ID={config['client_id']}
CAFE24_CLIENT_SECRET={config['client_secret']}
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={config['access_token']}
CAFE24_REFRESH_TOKEN={config.get('refresh_token', '')}
"""
    
    with open("render_env_final.txt", "w") as f:
        f.write(env_content)
    
    print("\n[CREATED] render_env_final.txt")
    print("\nDeploy to Render:")
    print("1. Copy contents of render_env_final.txt")
    print("2. Go to: https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env")
    print("3. Update all environment variables")
    print("4. Save Changes")
    print("5. Manual Deploy -> Deploy latest commit")

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
            
            # GitHub Actions 배포 시도
            try_github_deploy(config)
            
        else:
            print(f"[ERROR] API Test Failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"[ERROR] Test Exception: {e}")

def try_github_deploy(config):
    """GitHub Actions 자동 배포"""
    print("\n[DEPLOY] Attempting GitHub Actions deployment...")
    
    import subprocess
    
    try:
        # GitHub Secrets 업데이트
        secrets = [
            ('CAFE24_ACCESS_TOKEN', config['access_token']),
            ('CAFE24_REFRESH_TOKEN', config.get('refresh_token', ''))
        ]
        
        for key, value in secrets:
            if value:
                result = subprocess.run(
                    ['gh', 'secret', 'set', key],
                    input=value,
                    text=True,
                    capture_output=True
                )
                if result.returncode == 0:
                    print(f"[OK] {key} updated in GitHub")
        
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
            print("[INFO] Manual deployment needed")
            
    except Exception as e:
        print(f"[INFO] GitHub CLI not available: {e}")

def main():
    if exchange_auth_code():
        print("\n" + "=" * 60)
        print("SUCCESS! OAuth Setup Complete!")
        print("=" * 60)
        print("\nYour Cafe24 automation is ready!")
        print("Dashboard: https://cafe24-automation.onrender.com/")
    else:
        print("\nFailed to exchange auth code.")
        print("The code may have expired. Please try again.")

if __name__ == "__main__":
    main()