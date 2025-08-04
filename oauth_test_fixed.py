#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 OAuth 테스트 - URL 인코딩 수정
"""

import webbrowser
import json
import os
from urllib.parse import urlencode, quote

def generate_oauth_url():
    """올바른 OAuth URL 생성"""
    
    print("=" * 60)
    print("Cafe24 OAuth URL Generator (Fixed)")
    print("=" * 60)
    
    # 설정 로드
    config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    mall_id = config['mall_id']
    client_id = config['client_id']
    client_secret = config['client_secret']
    
    print(f"\n[Configuration]")
    print(f"Mall ID: {mall_id}")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:10]}...")
    
    # OAuth 파라미터
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': 'https://cafe24-automation.onrender.com/callback',
        'scope': 'mall.read_product,mall.write_product,mall.read_order,mall.write_order,mall.read_customer',
        'state': 'test123'
    }
    
    # URL 생성 (올바른 인코딩)
    base_url = f"https://{mall_id}.cafe24api.com/api/v2/oauth/authorize"
    query_string = urlencode(params, safe='')
    auth_url = f"{base_url}?{query_string}"
    
    print("\n[Generated OAuth URL]")
    print("-" * 80)
    print(auth_url)
    print("-" * 80)
    
    # 대체 URL (수동 구성)
    manual_url = f"https://{mall_id}.cafe24api.com/api/v2/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri=https%3A%2F%2Fcafe24-automation.onrender.com%2Fcallback&scope=mall.read_product%2Cmall.write_product%2Cmall.read_order%2Cmall.write_order%2Cmall.read_customer&state=test123"
    
    print("\n[Alternative URL (Manual encoding)]")
    print("-" * 80)
    print(manual_url)
    print("-" * 80)
    
    # Cafe24 개발자센터 방법
    print("\n[Alternative Method - Cafe24 Developer Center]")
    print("1. Go to: https://developers.cafe24.com")
    print("2. Login with your Cafe24 account")
    print("3. Select your app: 만원요리 자동화")
    print("4. Go to 'Test' or 'Playground' section")
    print("5. Click 'Get Access Token' button")
    print("6. Copy the generated token")
    
    # 선택
    print("\nChoose method:")
    print("1. Open OAuth URL (automatic encoding)")
    print("2. Open OAuth URL (manual encoding)")
    print("3. Open Cafe24 Developer Center")
    
    choice = input("\nSelect (1/2/3): ").strip()
    
    if choice == "1":
        print("\nOpening OAuth URL...")
        webbrowser.open(auth_url)
    elif choice == "2":
        print("\nOpening manual URL...")
        webbrowser.open(manual_url)
    elif choice == "3":
        print("\nOpening Developer Center...")
        webbrowser.open("https://developers.cafe24.com")
    
    print("\n[Next Steps]")
    print("1. Login to Cafe24 admin")
    print("2. Approve permissions")
    print("3. Copy the redirected URL with code parameter")
    print("4. Run: python oauth_auto_exchange.py")
    
    # 토큰 파일 생성
    create_token_template(config)

def create_token_template(config):
    """토큰 템플릿 파일 생성"""
    template = {
        "mall_id": config['mall_id'],
        "client_id": config['client_id'],
        "client_secret": config['client_secret'],
        "redirect_uri": "https://cafe24-automation.onrender.com/callback",
        "access_token": "PASTE_YOUR_ACCESS_TOKEN_HERE",
        "refresh_token": "PASTE_YOUR_REFRESH_TOKEN_HERE"
    }
    
    with open("token_template.json", "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print("\n[Token Template Created]")
    print("File: token_template.json")
    print("Update this file with tokens from Developer Center if needed")

if __name__ == "__main__":
    generate_oauth_url()