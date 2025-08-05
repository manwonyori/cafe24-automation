#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct OAuth Code Exchange
Using the authorization code you provided
"""

import json
import requests
import base64
from datetime import datetime, timedelta

# Your authorization code
AUTH_CODE = "A1PPUpyzBZTv8QlKPHvNQA"

def exchange_code():
    """Exchange authorization code for tokens"""
    
    print("=" * 60)
    print("Direct OAuth Code Exchange")
    print("=" * 60)
    
    # Load config
    config_path = r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    mall_id = config['mall_id']
    client_id = config['client_id']
    client_secret = config['client_secret']
    
    print(f"\nMall ID: {mall_id}")
    print(f"Client ID: {client_id[:20]}...")
    print(f"Auth Code: {AUTH_CODE}")
    
    # Token exchange
    token_url = f"https://{mall_id}.cafe24api.com/api/v2/oauth/token"
    
    # Basic Auth
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    # Try different redirect URI variations
    redirect_uris = [
        'https://cafe24-automation.onrender.com/callback',
        'https://cafe24-automation.onrender.com/callback/',
        'https://www.manwonyori.com',
        'https://www.manwonyori.com/'
    ]
    
    for redirect_uri in redirect_uris:
        print(f"\nTrying redirect_uri: {redirect_uri}")
        
        data = {
            'grant_type': 'authorization_code',
            'code': AUTH_CODE,
            'redirect_uri': redirect_uri
        }
        
        try:
            response = requests.post(token_url, headers=headers, data=data)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                print("\n[SUCCESS] Token Exchange Complete!")
                print(f"Access Token: {token_data['access_token'][:30]}...")
                print(f"Refresh Token: {token_data.get('refresh_token', 'N/A')[:30]}...")
                
                # Save tokens
                config['access_token'] = token_data['access_token']
                config['refresh_token'] = token_data.get('refresh_token', '')
                config['expires_at'] = (datetime.now() + timedelta(seconds=token_data.get('expires_in', 7200))).isoformat()
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                print("\n[SAVED] Configuration updated!")
                
                # Create Render env file
                create_render_env(config)
                return True
                
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")
    
    print("\n[FAILED] Could not exchange code with any redirect URI")
    print("\nAlternative: Get token from Developer Center")
    print("1. Go to https://developers.cafe24.com")
    print("2. My Apps -> Your App -> Authentication")
    print("3. Test Access Token -> Issue Token")
    print("4. Copy the token and run: python simple_token_setup.py")
    
    return False

def create_render_env(config):
    """Create Render environment file"""
    env_content = f"""# Cafe24 Environment Variables - READY TO DEPLOY!
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CAFE24_MALL_ID={config['mall_id']}
CAFE24_CLIENT_ID={config['client_id']}
CAFE24_CLIENT_SECRET={config['client_secret']}
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={config['access_token']}
CAFE24_REFRESH_TOKEN={config.get('refresh_token', '')}
"""
    
    with open("render_env_ready_to_deploy.txt", "w") as f:
        f.write(env_content)
    
    print("\n[CREATED] render_env_ready_to_deploy.txt")
    print("\nDEPLOY NOW:")
    print("1. Copy contents of render_env_ready_to_deploy.txt")
    print("2. Go to: https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env")
    print("3. Update ALL environment variables")
    print("4. Save Changes")
    print("5. Manual Deploy -> Deploy latest commit")
    print("\nYour system will be ready in 5 minutes!")

if __name__ == "__main__":
    exchange_code()