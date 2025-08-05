#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로컬 토큰을 서버로 업로드하는 스크립트
"""
import json
import requests
import sys

def upload_token():
    """로컬 토큰을 서버에 업로드"""
    try:
        # 로컬 토큰 읽기
        with open('oauth_token.json', 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        
        print(f"토큰 정보:")
        print(f"- Access Token: ***{token_data['access_token'][-10:]}")
        print(f"- Mall ID: {token_data['mall_id']}")
        print(f"- Expires At: {token_data['expires_at']}")
        
        # Render 환경 변수 업데이트를 위한 안내
        print("\n다음 환경 변수를 Render.com에 설정하세요:")
        print("\n```")
        print(f"CAFE24_ACCESS_TOKEN={token_data['access_token']}")
        print(f"CAFE24_REFRESH_TOKEN={token_data['refresh_token']}")
        print(f"CAFE24_CLIENT_ID={token_data.get('client_id', '9bPpABwHB5mtkCEAfIeuNK')}")
        print(f"CAFE24_CLIENT_SECRET={token_data.get('client_secret', 'qtnWtUk2OZzua1SRa7gN3A')}")
        print(f"CAFE24_MALL_ID={token_data['mall_id']}")
        print("```")
        
        print("\n또는 서버에서 직접 인증:")
        print("https://cafe24-automation.onrender.com/auth")
        
    except FileNotFoundError:
        print("ERROR: oauth_token.json 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    upload_token()