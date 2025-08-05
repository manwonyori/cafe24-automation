#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 OAuth 빠른 테스트
테스트 쇼핑몰: manwonyori.cafe24.com
"""

import webbrowser
import json
import os

def show_oauth_test_info():
    """OAuth 테스트 정보 표시"""
    
    print("=" * 60)
    print("Cafe24 OAuth Test Information")
    print("=" * 60)
    
    print("\n[TEST SHOP]")
    print("Shop URL: https://manwonyori.cafe24.com")
    print("Mall ID: manwonyori")
    
    print("\n[OAUTH SETTINGS]")
    print("Redirect URI: https://cafe24-automation.onrender.com/callback")
    
    # 설정 파일 확인
    config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        print(f"\nClient ID: {config.get('client_id', 'Not found')[:10]}...")
        print(f"Client Secret: {config.get('client_secret', 'Not found')[:10]}...")
        
        # OAuth URL 생성
        client_id = config.get('client_id')
        if client_id:
            auth_url = f"https://manwonyori.cafe24api.com/api/v2/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri=https://cafe24-automation.onrender.com/callback&scope=mall.read_product,mall.write_product,mall.read_order,mall.write_order,mall.read_customer"
            
            print("\n[OAUTH URL]")
            print("Click here to start OAuth flow:")
            print("-" * 60)
            print(auth_url)
            print("-" * 60)
            
            print("\n[QUICK START]")
            print("1. Opening browser in 3 seconds...")
            print("2. Login to Cafe24 admin")
            print("3. Approve permissions")
            print("4. Copy the redirected URL")
            print("5. Run: python oauth_auto_exchange.py")
            
            import time
            time.sleep(3)
            webbrowser.open(auth_url)
            
            print("\n[BROWSER OPENED]")
            print("After approval, you'll be redirected to:")
            print("https://cafe24-automation.onrender.com/callback?code=YOUR_CODE")
            
    else:
        print("\n[ERROR] Config file not found")
        print("Please run initial setup first")
        
    print("\n[TEST NOTES]")
    print("- Test shop works regardless of app pricing")
    print("- All permissions can be tested")
    print("- Sample data is available in test shop")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    show_oauth_test_info()