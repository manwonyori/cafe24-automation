#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final deployment fix - Get fresh tokens and update Render
"""
import json
import requests
import base64
from datetime import datetime, timedelta
import webbrowser
import time

def get_fresh_authorization():
    """Get fresh authorization code"""
    print("=" * 80)
    print("FINAL DEPLOYMENT FIX - Getting Fresh Tokens")
    print("=" * 80)
    
    # Configuration
    config = {
        'mall_id': 'manwonyori',
        'client_id': '9bPpABwHB5mtkCEAfIeuNK',
        'client_secret': 'qtnWtUk2OZzua1SRa7gN3A',
        'redirect_uri': 'https://cafe24-automation.onrender.com/callback'
    }
    
    # Generate authorization URL
    auth_url = f"https://{config['mall_id']}.cafe24api.com/api/v2/oauth/authorize"
    params = {
        'response_type': 'code',
        'client_id': config['client_id'],
        'redirect_uri': config['redirect_uri'],
        'scope': 'mall.read_product,mall.write_product,mall.read_order,mall.write_order,mall.read_customer'
    }
    
    auth_url_full = f"{auth_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    print(f"\n1. AUTHORIZATION URL:")
    print(f"   {auth_url_full}")
    print("\n2. STEPS:")
    print("   a) Click the URL above or copy it to your browser")
    print("   b) Login to Cafe24 and authorize the app")
    print("   c) Copy the 'code' from the redirect URL")
    print("   d) Paste it below")
    
    # Open browser automatically
    try:
        webbrowser.open(auth_url_full)
        print("\n   ✅ Browser opened automatically")
    except:
        print("\n   ⚠️ Please open the URL manually")
    
    # Get authorization code from user
    print("\n" + "-" * 60)
    auth_code = input("Enter the authorization code from the redirect URL: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return None
    
    print(f"\n✅ Received code: {auth_code}")
    
    # Exchange code for tokens
    return exchange_code_for_tokens(config, auth_code)

def exchange_code_for_tokens(config, auth_code):
    """Exchange authorization code for access tokens"""
    print("\n" + "=" * 60)
    print("EXCHANGING CODE FOR TOKENS")
    print("=" * 60)
    
    token_url = f"https://{config['mall_id']}.cafe24api.com/api/v2/oauth/token"
    
    # Basic Auth
    auth_header = base64.b64encode(f"{config['client_id']}:{config['client_secret']}".encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': config['redirect_uri']
    }
    
    try:
        response = requests.post(token_url, headers=headers, data=data, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            
            print("✅ TOKEN EXCHANGE SUCCESSFUL!")
            print(f"   Access Token: {token_data['access_token'][:30]}...")
            print(f"   Refresh Token: {token_data.get('refresh_token', 'N/A')[:30]}...")
            print(f"   Expires In: {token_data.get('expires_in', 7200)} seconds")
            
            # Create complete token configuration
            full_config = {
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token', ''),
                'expires_at': (datetime.now() + timedelta(seconds=token_data.get('expires_in', 7200))).isoformat() + '.000',
                'refresh_token_expires_at': (datetime.now() + timedelta(seconds=token_data.get('refresh_token_expires_in', 1209600))).isoformat() + '.000',
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'mall_id': config['mall_id'],
                'user_id': config['mall_id'],
                'scopes': [
                    'mall.read_product',
                    'mall.write_product', 
                    'mall.read_order',
                    'mall.write_order',
                    'mall.read_customer'
                ],
                'issued_at': datetime.now().isoformat() + '.000',
                'shop_no': '1'
            }
            
            # Save local token file
            with open('oauth_token.json', 'w', encoding='utf-8') as f:
                json.dump(full_config, f, indent=2, ensure_ascii=False)
            
            print("✅ Local token file updated")
            
            # Test API connection
            if test_api_connection(full_config):
                create_render_deployment_files(full_config)
                return full_config
            else:
                print("❌ API test failed")
                return None
                
        else:
            print(f"❌ TOKEN EXCHANGE FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception during token exchange: {e}")
        return None

def test_api_connection(config):
    """Test API connection with new tokens"""
    print("\n" + "=" * 60)
    print("TESTING API CONNECTION")
    print("=" * 60)
    
    test_url = f"https://{config['mall_id']}.cafe24api.com/api/v2/admin/products?limit=3"
    headers = {
        'Authorization': f'Bearer {config["access_token"]}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': '2025-06-01'
    }
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"✅ API CONNECTION SUCCESSFUL!")
            print(f"   Found {len(products)} products")
            for i, product in enumerate(products[:3], 1):
                print(f"   {i}. {product.get('product_name', 'Unknown')}")
            return True
        else:
            print(f"❌ API TEST FAILED: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ API TEST ERROR: {e}")
        return False

def create_render_deployment_files(config):
    """Create deployment files for Render"""
    print("\n" + "=" * 60)
    print("CREATING DEPLOYMENT FILES")
    print("=" * 60)
    
    # Render environment variables
    env_content = f"""CAFE24_MALL_ID={config['mall_id']}
CAFE24_CLIENT_ID={config['client_id']}
CAFE24_CLIENT_SECRET={config['client_secret']}
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={config['access_token']}
CAFE24_REFRESH_TOKEN={config['refresh_token']}
CAFE24_API_VERSION=2025-06-01
ENABLE_AUTO_REFRESH=true
ENABLE_DASHBOARD=true
ENABLE_API_ENDPOINTS=true
PRODUCTION_MODE=true
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
PORT=5000"""

    with open('RENDER_ENV_VARS_FINAL.txt', 'w') as f:
        f.write(env_content)
    
    print("✅ Created RENDER_ENV_VARS_FINAL.txt")
    
    # Deployment instructions
    instructions = f"""
# FINAL DEPLOYMENT INSTRUCTIONS

## 🚀 Your system is ready! Follow these steps:

### 1. Update Render Environment Variables
- Go to: https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env
- DELETE all existing environment variables  
- Copy ALL contents from RENDER_ENV_VARS_FINAL.txt
- Paste into Render environment variables
- Click "Save Changes"

### 2. Deploy
- Go to: https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg
- Click "Manual Deploy" 
- Select "Deploy latest commit"
- Wait for deployment to complete (~5 minutes)

### 3. Test Your System
After deployment, test these URLs:

✅ Status: https://cafe24-automation.onrender.com/api/status
✅ Products: https://cafe24-automation.onrender.com/api/products?limit=5  
✅ Orders: https://cafe24-automation.onrender.com/api/orders/today

### 4. Success Indicators
- All URLs return JSON data (not errors)
- Products API shows your actual products
- Orders API shows today's orders

## 🎉 SYSTEM IS READY!

Token expires: {config['expires_at']}
Next refresh: Automatic every hour
System status: PRODUCTION READY

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open('DEPLOYMENT_SUCCESS_GUIDE.txt', 'w') as f:
        f.write(instructions)
    
    print("✅ Created DEPLOYMENT_SUCCESS_GUIDE.txt")
    
    print("\n" + "=" * 80)
    print("🎉 SUCCESS! ALL FILES CREATED!")
    print("=" * 80)
    print("Next Steps:")
    print("1. Check RENDER_ENV_VARS_FINAL.txt for environment variables")
    print("2. Follow DEPLOYMENT_SUCCESS_GUIDE.txt for deployment")
    print("3. Your system will be live in ~5 minutes after deployment!")
    print("=" * 80)

def main():
    """Main execution"""
    try:
        config = get_fresh_authorization()
        if config:
            print(f"\n✅ SUCCESS! Your Cafe24 automation system is ready!")
            print(f"Token valid until: {config['expires_at']}")
        else:
            print(f"\n❌ Failed to get fresh tokens. Please try again.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()