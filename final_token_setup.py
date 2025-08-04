#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 최종 토큰 설정 - 개발자센터 방법
가장 빠르고 확실한 방법입니다
"""

import json
import os
import webbrowser
import requests
from datetime import datetime, timedelta

def final_setup():
    """최종 토큰 설정"""
    
    print("=" * 80)
    print("Cafe24 Final Token Setup - Developer Center Method")
    print("=" * 80)
    
    print("\n[WHY THIS METHOD?]")
    print("- OAuth code expired (valid only 5 minutes)")
    print("- Redirect URI mismatch issues")
    print("- Developer Center method is instant!")
    
    print("\n[OPENING DEVELOPER CENTER...]")
    webbrowser.open("https://developers.cafe24.com")
    
    print("\n[STEP-BY-STEP GUIDE]")
    print("1. Login with your Cafe24 account")
    print("2. Click '내 앱' (My Apps) in top menu")
    print("3. Find and click your app (만원요리 자동화)")
    print("4. Click '인증 정보' (Authentication) tab")
    print("5. Scroll down to '테스트 Access Token' section")
    print("6. Click '토큰 발급' (Issue Token) button")
    print("7. Check ALL permissions:")
    print("   - mall.read_product")
    print("   - mall.write_product")
    print("   - mall.read_order")
    print("   - mall.write_order")
    print("   - mall.read_customer")
    print("8. Click '생성' (Generate)")
    print("9. Copy the tokens shown in popup")
    
    print("\n" + "-" * 60)
    print("PASTE YOUR TOKENS BELOW:")
    print("-" * 60)
    
    # Get tokens
    access_token = input("\nAccess Token: ").strip()
    if not access_token:
        print("\n[ERROR] Access token is required!")
        return False
        
    refresh_token = input("Refresh Token (optional, press Enter to skip): ").strip()
    
    # Load and update config
    config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Update tokens
    config['access_token'] = access_token
    if refresh_token:
        config['refresh_token'] = refresh_token
    config['expires_at'] = (datetime.now() + timedelta(hours=2)).isoformat()
    
    # Save
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("\n[SUCCESS] Tokens saved!")
    
    # Test token
    if test_token(config):
        print("\n[VERIFIED] Token is working!")
        
        # Create final deployment files
        create_final_deployment(config)
        
        # Show complete status
        show_complete_status(config)
        
        return True
    else:
        print("\n[ERROR] Token test failed!")
        return False

def test_token(config):
    """Test token validity"""
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
            data = response.json()
            print(f"[OK] API working! Found {len(data.get('products', []))} products")
            return True
        else:
            print(f"[ERROR] API returned {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

def create_final_deployment(config):
    """Create final deployment files"""
    
    # 1. Render environment file
    env_content = f"""# Cafe24 Production Environment Variables
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Status: READY FOR PRODUCTION

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
    
    with open("FINAL_RENDER_ENV.txt", "w") as f:
        f.write(env_content)
    
    print("\n[CREATED] FINAL_RENDER_ENV.txt")
    
    # 2. Deployment checklist
    checklist = f"""# Cafe24 Automation Deployment Checklist

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## ✅ Completed Setup:
- [x] OAuth tokens obtained from Developer Center
- [x] Tokens tested and verified
- [x] Configuration files updated
- [x] Environment variables prepared

## 📋 Deployment Steps:

### 1. Update Render Environment (5 minutes)
1. Copy ALL contents from FINAL_RENDER_ENV.txt
2. Go to: https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env
3. Replace ALL environment variables
4. Click "Save Changes"
5. Click "Manual Deploy" -> "Deploy latest commit"

### 2. Wait for Deployment (5 minutes)
- Watch progress at Render dashboard
- Wait for "Live" status

### 3. Test Your System
- Dashboard: https://cafe24-automation.onrender.com/
- API Test: https://cafe24-automation.onrender.com/api/test
- Products: https://cafe24-automation.onrender.com/api/products
- Orders: https://cafe24-automation.onrender.com/api/orders

## 🔧 Features Available:
- Real-time order monitoring
- Product inventory management
- Customer data lookup
- Sales statistics
- Natural language commands
- Auto token refresh (every 2 hours)

## ⚠️ Important Notes:
- Access Token expires in 2 hours (auto-refreshed)
- Refresh Token valid for 2 weeks
- All API calls are logged
- 403 errors trigger auto token refresh

## 🆘 Troubleshooting:
If dashboard shows errors after deployment:
1. Check Render logs
2. Verify all environment variables
3. Redeploy if needed
"""
    
    with open("DEPLOYMENT_CHECKLIST.md", "w") as f:
        f.write(checklist)
    
    print("[CREATED] DEPLOYMENT_CHECKLIST.md")

def show_complete_status(config):
    """Show complete system status"""
    print("\n" + "=" * 80)
    print("CAFE24 AUTOMATION SYSTEM - READY FOR DEPLOYMENT!")
    print("=" * 80)
    
    print("\n[SYSTEM STATUS]")
    print(f"Mall ID: {config['mall_id']}")
    print(f"Token Status: ACTIVE")
    print(f"Expires: {config.get('expires_at', 'In 2 hours')}")
    
    print("\n[DEPLOYMENT FILES]")
    print("1. FINAL_RENDER_ENV.txt - Environment variables")
    print("2. DEPLOYMENT_CHECKLIST.md - Step-by-step guide")
    
    print("\n[NEXT STEPS]")
    print("1. Open FINAL_RENDER_ENV.txt")
    print("2. Copy ALL contents")
    print("3. Go to Render dashboard")
    print("4. Update environment variables")
    print("5. Deploy!")
    
    print("\n[URLS]")
    print("Render Dashboard: https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env")
    print("Your App: https://cafe24-automation.onrender.com/")
    
    print("\n" + "=" * 80)
    print("Your Cafe24 automation is ready! Deploy now to start using it.")
    print("=" * 80)

def main():
    """Main function"""
    if final_setup():
        print("\n🎉 SUCCESS! Everything is configured!")
        print("Follow the deployment checklist to go live.")
    else:
        print("\n❌ Setup failed. Please try again.")

if __name__ == "__main__":
    main()