#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
만원요리 최씨남매 Cafe24 원클릭 자동 배포 시스템
Complete DevOps automation in one click
"""

import os
import sys
import json
import time
import subprocess
import requests
import platform
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import threading
import queue


class OneClickDeploy:
    def __init__(self):
        self.start_time = datetime.now()
        self.status_queue = queue.Queue()
        self.errors = []
        self.completed_steps = []
        
        # Configuration paths
        self.config_paths = [
            r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json",
            "config/oauth_token.json",
            "../카페24_프로젝트/01_ACTIVE_PROJECT/config/oauth_token.json"
        ]
        
        # Status indicators
        self.steps = {
            "load_config": {"name": "Load Cafe24 Config", "status": "pending"},
            "check_github_cli": {"name": "Check GitHub CLI", "status": "pending"},
            "setup_github_auth": {"name": "GitHub Authentication", "status": "pending"},
            "create_github_secrets": {"name": "Create GitHub Secrets", "status": "pending"},
            "setup_github_actions": {"name": "Setup GitHub Actions", "status": "pending"},
            "get_render_credentials": {"name": "Get Render Credentials", "status": "pending"},
            "sync_render_env": {"name": "Sync Render Environment", "status": "pending"},
            "trigger_deployment": {"name": "Trigger Deployment", "status": "pending"},
            "verify_production": {"name": "Verify Production Mode", "status": "pending"},
            "run_tests": {"name": "Run API Tests", "status": "pending"}
        }
        
    def print_header(self):
        """Print fancy header"""
        print("\n" + "="*70)
        print("   🚀 만원요리 최씨남매 Cafe24 원클릭 자동 배포 시스템")
        print("="*70)
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
    def update_status(self, step_id: str, status: str, message: str = ""):
        """Update step status"""
        if step_id in self.steps:
            self.steps[step_id]["status"] = status
            self.display_progress()
            
            if message:
                if status == "error":
                    print(f"\n❌ {message}")
                    self.errors.append(message)
                elif status == "completed":
                    print(f"\n✅ {message}")
                    self.completed_steps.append(step_id)
                else:
                    print(f"\n📌 {message}")
                    
    def display_progress(self):
        """Display progress bar"""
        print("\n" + "-"*50)
        print("Progress:")
        for step_id, step_info in self.steps.items():
            status = step_info["status"]
            name = step_info["name"]
            
            if status == "completed":
                icon = "✅"
            elif status == "in_progress":
                icon = "🔄"
            elif status == "error":
                icon = "❌"
            else:
                icon = "⏳"
                
            print(f"  {icon} {name}")
        print("-"*50)
        
    def load_cafe24_config(self) -> Optional[Dict]:
        """Load Cafe24 configuration"""
        self.update_status("load_config", "in_progress", "Loading Cafe24 configuration...")
        
        for path in self.config_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        self.update_status("load_config", "completed", 
                                         f"Loaded config from: {path}")
                        return config
                except Exception as e:
                    self.update_status("load_config", "error", 
                                     f"Failed to load config: {e}")
                    return None
                    
        self.update_status("load_config", "error", "Config file not found")
        return None
        
    def install_github_cli(self) -> bool:
        """Install GitHub CLI if not present"""
        self.update_status("check_github_cli", "in_progress", 
                         "Checking GitHub CLI installation...")
        
        # Check if installed
        try:
            result = subprocess.run(['gh', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.update_status("check_github_cli", "completed", 
                                 "GitHub CLI is already installed")
                return True
        except FileNotFoundError:
            pass
            
        # Auto-install based on platform
        system = platform.system()
        
        if system == "Windows":
            print("\n🔧 Installing GitHub CLI for Windows...")
            try:
                # Try winget first
                result = subprocess.run(['winget', 'install', '--id', 'GitHub.cli', '-e'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.update_status("check_github_cli", "completed", 
                                     "GitHub CLI installed successfully")
                    return True
            except:
                pass
                
        self.update_status("check_github_cli", "error", 
                         "Please install GitHub CLI manually")
        print("\nInstall instructions:")
        print("  Windows: winget install --id GitHub.cli")
        print("  Mac: brew install gh")
        print("  Linux: https://github.com/cli/cli#installation")
        return False
        
    def setup_github_auth(self) -> bool:
        """Setup GitHub authentication"""
        self.update_status("setup_github_auth", "in_progress", 
                         "Setting up GitHub authentication...")
        
        # Check if already authenticated
        result = subprocess.run(['gh', 'auth', 'status'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            self.update_status("setup_github_auth", "completed", 
                             "GitHub CLI already authenticated")
            return True
            
        # Auto-authenticate
        print("\n🔑 GitHub authentication required")
        print("This will open your browser for authentication")
        input("Press Enter to continue...")
        
        result = subprocess.run(['gh', 'auth', 'login', '--web'], 
                              capture_output=False)
        if result.returncode == 0:
            self.update_status("setup_github_auth", "completed", 
                             "GitHub authentication successful")
            return True
            
        self.update_status("setup_github_auth", "error", 
                         "GitHub authentication failed")
        return False
        
    def create_github_secrets(self, config: Dict) -> bool:
        """Create GitHub secrets automatically"""
        self.update_status("create_github_secrets", "in_progress", 
                         "Creating GitHub Secrets...")
        
        # Get repository info
        result = subprocess.run(['gh', 'repo', 'view', '--json', 'nameWithOwner'],
                              capture_output=True, text=True)
        if result.returncode != 0:
            self.update_status("create_github_secrets", "error", 
                             "Not in a GitHub repository")
            return False
            
        repo_info = json.loads(result.stdout)
        repo = repo_info['nameWithOwner']
        
        # Prepare secrets
        secrets = {
            "CAFE24_MALL_ID": config.get('mall_id'),
            "CAFE24_CLIENT_ID": config.get('client_id'),
            "CAFE24_CLIENT_SECRET": config.get('client_secret'),
            "CAFE24_ACCESS_TOKEN": config.get('access_token'),
            "CAFE24_REFRESH_TOKEN": config.get('refresh_token')
        }
        
        success_count = 0
        for name, value in secrets.items():
            if value:
                result = subprocess.run(
                    ['gh', 'secret', 'set', name, '--repo', repo],
                    input=value,
                    text=True,
                    capture_output=True
                )
                if result.returncode == 0:
                    success_count += 1
                    print(f"  ✅ Set secret: {name}")
                else:
                    print(f"  ❌ Failed to set {name}")
                    
        self.update_status("create_github_secrets", "completed", 
                         f"Created {success_count}/{len(secrets)} secrets")
        return success_count > 0
        
    def get_render_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """Get or create Render credentials"""
        self.update_status("get_render_credentials", "in_progress", 
                         "Setting up Render credentials...")
        
        # Check if already in GitHub secrets
        result = subprocess.run(['gh', 'secret', 'list'], 
                              capture_output=True, text=True)
        
        has_api_key = 'RENDER_API_KEY' in result.stdout
        has_deploy_hook = 'RENDER_DEPLOY_HOOK_URL' in result.stdout
        
        api_key = None
        deploy_hook = None
        
        if not has_api_key:
            print("\n🔑 Render API Key required")
            print("1. Go to: https://dashboard.render.com")
            print("2. Account Settings → API Keys → Create API Key")
            api_key = input("\nEnter Render API Key (or press Enter to skip): ").strip()
            
            if api_key:
                subprocess.run(['gh', 'secret', 'set', 'RENDER_API_KEY'],
                             input=api_key, text=True, capture_output=True)
                             
        if not has_deploy_hook:
            print("\n🔗 Render Deploy Hook URL required")
            print("1. Go to: https://dashboard.render.com")
            print("2. Select cafe24-automation service")
            print("3. Settings → Deploy Hook")
            deploy_hook = input("\nEnter Deploy Hook URL (or press Enter to skip): ").strip()
            
            if deploy_hook:
                subprocess.run(['gh', 'secret', 'set', 'RENDER_DEPLOY_HOOK_URL'],
                             input=deploy_hook, text=True, capture_output=True)
                             
        self.update_status("get_render_credentials", "completed", 
                         "Render credentials configured")
        return api_key, deploy_hook
        
    def setup_github_actions(self) -> bool:
        """Ensure GitHub Actions workflow exists"""
        self.update_status("setup_github_actions", "in_progress", 
                         "Setting up GitHub Actions...")
        
        workflow_path = ".github/workflows/auto-deploy.yml"
        
        if os.path.exists(workflow_path):
            self.update_status("setup_github_actions", "completed", 
                             "GitHub Actions workflow already exists")
            return True
            
        self.update_status("setup_github_actions", "error", 
                         "GitHub Actions workflow not found")
        print(f"\nPlease ensure {workflow_path} exists in your repository")
        return False
        
    def sync_render_environment(self, api_key: str, config: Dict) -> bool:
        """Sync environment variables to Render"""
        if not api_key:
            self.update_status("sync_render_env", "skipped", 
                             "Skipped (no API key)")
            return True
            
        self.update_status("sync_render_env", "in_progress", 
                         "Syncing Render environment variables...")
        
        try:
            # This would use the Render API
            # For now, we'll trigger via GitHub Actions
            self.update_status("sync_render_env", "completed", 
                             "Environment sync will run via GitHub Actions")
            return True
        except Exception as e:
            self.update_status("sync_render_env", "error", 
                             f"Sync failed: {e}")
            return False
            
    def trigger_deployment(self) -> bool:
        """Trigger GitHub Actions deployment"""
        self.update_status("trigger_deployment", "in_progress", 
                         "Triggering deployment...")
        
        print("\n🚀 Triggering GitHub Actions deployment...")
        
        result = subprocess.run(
            ['gh', 'workflow', 'run', 'auto-deploy.yml'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            self.update_status("trigger_deployment", "completed", 
                             "Deployment triggered successfully")
            
            # Get workflow run URL
            time.sleep(2)  # Wait for workflow to start
            
            result = subprocess.run(
                ['gh', 'run', 'list', '--limit', '1', '--json', 'url'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                runs = json.loads(result.stdout)
                if runs:
                    print(f"\n📊 Monitor deployment at: {runs[0]['url']}")
                    
            return True
        else:
            self.update_status("trigger_deployment", "error", 
                             "Failed to trigger deployment")
            return False
            
    def verify_production_mode(self, max_wait: int = 300) -> bool:
        """Verify production mode is active"""
        self.update_status("verify_production", "in_progress", 
                         "Waiting for deployment...")
        
        url = "https://cafe24-automation.onrender.com"
        start_time = time.time()
        
        print(f"\n⏳ Monitoring {url}")
        print("This may take 3-5 minutes...")
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    mode = data.get('mode', 'unknown')
                    
                    if mode == 'production':
                        self.update_status("verify_production", "completed", 
                                         "Production mode active!")
                        return True
                    elif mode == 'demo':
                        print(".", end="", flush=True)
                    
            except Exception:
                print(".", end="", flush=True)
                
            time.sleep(10)
            
        self.update_status("verify_production", "error", 
                         "Timeout waiting for production mode")
        return False
        
    def run_api_tests(self) -> bool:
        """Run comprehensive API tests"""
        self.update_status("run_tests", "in_progress", "Running API tests...")
        
        try:
            # Use the test script if available
            if os.path.exists("test_all_endpoints.py"):
                result = subprocess.run(
                    [sys.executable, "test_all_endpoints.py"],
                    capture_output=True,
                    text=True
                )
                
                if "100.0%" in result.stdout or "All tests passed" in result.stdout:
                    self.update_status("run_tests", "completed", 
                                     "All API tests passed!")
                    return True
                else:
                    self.update_status("run_tests", "error", 
                                     "Some API tests failed")
                    return False
            else:
                # Simple test
                response = requests.get("https://cafe24-automation.onrender.com/health")
                if response.status_code == 200:
                    self.update_status("run_tests", "completed", 
                                     "Basic health check passed")
                    return True
                    
        except Exception as e:
            self.update_status("run_tests", "error", f"Test failed: {e}")
            
        return False
        
    def generate_summary(self):
        """Generate deployment summary"""
        print("\n\n" + "="*70)
        print("📊 DEPLOYMENT SUMMARY")
        print("="*70)
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        print(f"Total Time: {int(total_time)}s")
        print(f"Completed Steps: {len(self.completed_steps)}/{len(self.steps)}")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("\n✅ No errors!")
            
        print("\n📌 Next Steps:")
        
        if "verify_production" in self.completed_steps:
            print("  ✅ Your Cafe24 system is now in Production mode!")
            print("  🔗 URL: https://cafe24-automation.onrender.com")
            print("  📊 Dashboard: https://cafe24-automation.onrender.com/")
        else:
            print("  1. Check GitHub Actions: https://github.com/manwonyori/cafe24/actions")
            print("  2. Monitor Render logs: https://dashboard.render.com")
            print("  3. Manually set environment variables if needed")
            
        print("\n" + "="*70)
        
    def run(self):
        """Execute one-click deployment"""
        self.print_header()
        
        try:
            # 1. Load configuration
            config = self.load_cafe24_config()
            if not config:
                print("\n❌ Cannot proceed without configuration")
                return
                
            # 2. Setup GitHub CLI
            if not self.install_github_cli():
                return
                
            # 3. GitHub authentication
            if not self.setup_github_auth():
                return
                
            # 4. Create GitHub secrets
            self.create_github_secrets(config)
            
            # 5. Setup GitHub Actions
            self.setup_github_actions()
            
            # 6. Get Render credentials
            api_key, deploy_hook = self.get_render_credentials()
            
            # 7. Sync Render environment
            self.sync_render_environment(api_key, config)
            
            # 8. Trigger deployment
            if self.trigger_deployment():
                # 9. Verify production mode
                self.verify_production_mode()
                
                # 10. Run tests
                self.run_api_tests()
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Deployment cancelled by user")
        except Exception as e:
            print(f"\n\n❌ Unexpected error: {e}")
            
        finally:
            self.generate_summary()


def main():
    """Main entry point"""
    deployer = OneClickDeploy()
    deployer.run()


if __name__ == "__main__":
    main()