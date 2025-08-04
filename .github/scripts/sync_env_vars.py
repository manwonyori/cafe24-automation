#!/usr/bin/env python3
"""
Sync environment variables from GitHub Secrets to Render
"""

import os
import requests
import json
import sys
from typing import Dict, List


class RenderEnvSync:
    def __init__(self):
        self.render_api_key = os.environ.get('RENDER_API_KEY')
        if not self.render_api_key:
            raise ValueError("RENDER_API_KEY not found in environment")
            
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.render_api_key}",
            "Content-Type": "application/json"
        }
        
        # Cafe24 credentials from GitHub Secrets
        self.cafe24_vars = {
            "CAFE24_MALL_ID": os.environ.get('CAFE24_MALL_ID'),
            "CAFE24_CLIENT_ID": os.environ.get('CAFE24_CLIENT_ID'),
            "CAFE24_CLIENT_SECRET": os.environ.get('CAFE24_CLIENT_SECRET'),
            "CAFE24_ACCESS_TOKEN": os.environ.get('CAFE24_ACCESS_TOKEN'),
            "CAFE24_REFRESH_TOKEN": os.environ.get('CAFE24_REFRESH_TOKEN'),
            "CAFE24_REDIRECT_URI": "https://cafe24-automation.onrender.com/callback"
        }
        
    def find_service(self) -> str:
        """Find cafe24-automation service ID"""
        print("🔍 Finding Render service...")
        
        response = requests.get(
            f"{self.base_url}/services",
            headers=self.headers
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            sys.exit(1)
            
        services = response.json()
        
        for service in services:
            if 'cafe24' in service.get('name', '').lower():
                print(f"✅ Found service: {service['name']} (ID: {service['id']})")
                return service['id']
                
        print("❌ Service not found")
        sys.exit(1)
        
    def update_env_vars(self, service_id: str) -> bool:
        """Update environment variables"""
        print("\n📝 Updating environment variables...")
        
        # Prepare environment variables
        env_vars = []
        for key, value in self.cafe24_vars.items():
            if value:
                env_vars.append({
                    "key": key,
                    "value": value
                })
                print(f"   - {key}: {'*' * 10}")
            else:
                print(f"   ⚠️  {key}: Missing")
                
        if not env_vars:
            print("❌ No environment variables to update")
            return False
            
        # Update environment variables
        response = requests.put(
            f"{self.base_url}/services/{service_id}/env-vars",
            headers=self.headers,
            json=env_vars
        )
        
        if response.status_code == 200:
            print("✅ Environment variables updated successfully")
            return True
        else:
            print(f"❌ Failed to update: {response.status_code} - {response.text}")
            return False
            
    def get_latest_deployment(self, service_id: str) -> Dict:
        """Get latest deployment info"""
        response = requests.get(
            f"{self.base_url}/services/{service_id}/deploys?limit=1",
            headers=self.headers
        )
        
        if response.status_code == 200:
            deploys = response.json()
            if deploys:
                return deploys[0]
        return None
        
    def run(self):
        """Main sync process"""
        print("🚀 Cafe24 Environment Sync Started")
        print("=" * 50)
        
        # Validate environment variables
        missing_vars = []
        for key, value in self.cafe24_vars.items():
            if not value and key != "CAFE24_REDIRECT_URI":
                missing_vars.append(key)
                
        if missing_vars:
            print(f"⚠️  Warning: Missing variables: {', '.join(missing_vars)}")
            print("   These need to be set in GitHub Secrets")
            
        # Find service
        service_id = self.find_service()
        
        # Update environment variables
        success = self.update_env_vars(service_id)
        
        if success:
            print("\n✅ Sync completed successfully!")
            
            # Get deployment info
            deployment = self.get_latest_deployment(service_id)
            if deployment:
                print(f"\n📊 Latest deployment:")
                print(f"   - Status: {deployment.get('status')}")
                print(f"   - Commit: {deployment.get('commit', {}).get('id', 'N/A')[:7]}")
                
        else:
            print("\n❌ Sync failed")
            sys.exit(1)
            
        print("\n" + "=" * 50)
        print("✨ Done!")


if __name__ == "__main__":
    try:
        syncer = RenderEnvSync()
        syncer.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)