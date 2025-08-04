#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 OAuth Token 자동 갱신
"""

import os
import sys
import json
import requests
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def refresh_cafe24_token():
    """Refresh token으로 새 access token 발급"""
    
    # 1. 기존 토큰 정보 로드
    config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
    
    if not os.path.exists(config_path):
        print("[ERROR] Config file not found")
        return None
        
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        
    # 2. Refresh token으로 새 토큰 요청
    mall_id = config['mall_id']
    client_id = config['client_id']
    client_secret = config['client_secret']
    refresh_token = config['refresh_token']
    
    print(f"Mall ID: {mall_id}")
    print(f"Client ID: {client_id[:10]}...")
    print(f"Refresh Token: {refresh_token[:10]}...")
    
    # OAuth refresh endpoint
    url = f"https://{mall_id}.cafe24api.com/api/auth/token"
    
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    
    auth = (client_id, client_secret)
    
    print("\n[REQUEST] Refreshing token...")
    
    try:
        response = requests.post(url, data=data, auth=auth)
        
        if response.status_code == 200:
            new_token_data = response.json()
            
            print("[SUCCESS] New token received!")
            print(f"New Access Token: {new_token_data['access_token'][:20]}...")
            
            # 3. 새 토큰 정보 저장
            config['access_token'] = new_token_data['access_token']
            config['expires_at'] = datetime.now().isoformat() + '.000'
            
            # 파일에 저장
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            print("\n[SAVED] Token updated in config file")
            
            # 4. Render 환경변수 업데이트용 파일 생성
            env_content = f"""CAFE24_MALL_ID={mall_id}
CAFE24_CLIENT_ID={client_id}
CAFE24_CLIENT_SECRET={client_secret}
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={new_token_data['access_token']}
CAFE24_REFRESH_TOKEN={refresh_token}"""
            
            with open("render_env_updated.txt", "w") as f:
                f.write(env_content)
                
            print("\n[CREATED] render_env_updated.txt")
            print("\nNext steps:")
            print("1. Copy the contents of render_env_updated.txt")
            print("2. Go to: https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env")
            print("3. Update the environment variables")
            print("4. Deploy the changes")
            
            return new_token_data
            
        else:
            print(f"[ERROR] Failed to refresh token: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 401:
                print("\n[INFO] Refresh token may also be expired.")
                print("You need to re-authenticate at Cafe24 Developer Center")
                
    except Exception as e:
        print(f"[ERROR] {e}")
        
    return None


if __name__ == "__main__":
    refresh_cafe24_token()