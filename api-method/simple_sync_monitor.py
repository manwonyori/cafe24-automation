#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 API Key 동기화 모니터 (Simple Version)
No external dependencies required
"""

import os
import json
import time
import subprocess
import requests
from datetime import datetime


class SimpleSyncMonitor:
    def __init__(self):
        self.config = None
        self.status = {
            "config": False,
            "github": False,
            "render": False,
            "production": False
        }
        self.start_time = datetime.now()
        
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self):
        """Print header"""
        print("=" * 60)
        print("   Cafe24 API Key Sync Monitor")
        print("=" * 60)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
    def load_config(self):
        """Load Cafe24 configuration"""
        paths = [
            r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json",
            "config/oauth_token.json"
        ]
        
        for path in paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self.config = json.load(f)
                        self.status["config"] = True
                        print(f"\n[OK] Config loaded from: {path}")
                        return True
                except Exception as e:
                    print(f"\n[ERROR] Failed to load config: {e}")
                    
        print("\n[ERROR] Config file not found")
        return False
        
    def check_github_secrets(self):
        """Check GitHub secrets"""
        print("\n[CHECK] GitHub Secrets...")
        
        try:
            result = subprocess.run(
                ['gh', 'secret', 'list'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                required = ['CAFE24_MALL_ID', 'CAFE24_CLIENT_ID', 
                          'CAFE24_CLIENT_SECRET', 'CAFE24_ACCESS_TOKEN']
                
                missing = []
                for secret in required:
                    if secret in result.stdout:
                        print(f"  [OK] {secret}")
                    else:
                        print(f"  [MISSING] {secret}")
                        missing.append(secret)
                        
                self.status["github"] = len(missing) == 0
                return len(missing) == 0
                
        except Exception as e:
            print(f"  [ERROR] GitHub CLI error: {e}")
            return False
            
    def sync_github_secrets(self):
        """Sync secrets to GitHub"""
        print("\n[SYNC] Syncing to GitHub...")
        
        if not self.config:
            print("  [ERROR] No config loaded")
            return False
            
        secrets = {
            "CAFE24_MALL_ID": self.config.get('mall_id'),
            "CAFE24_CLIENT_ID": self.config.get('client_id'),
            "CAFE24_CLIENT_SECRET": self.config.get('client_secret'),
            "CAFE24_ACCESS_TOKEN": self.config.get('access_token'),
            "CAFE24_REFRESH_TOKEN": self.config.get('refresh_token')
        }
        
        success = 0
        for name, value in secrets.items():
            if value:
                try:
                    result = subprocess.run(
                        ['gh', 'secret', 'set', name],
                        input=value,
                        text=True,
                        capture_output=True
                    )
                    if result.returncode == 0:
                        print(f"  [OK] Set {name}")
                        success += 1
                    else:
                        print(f"  [FAIL] {name}")
                except Exception as e:
                    print(f"  [ERROR] {name}: {e}")
                    
        return success == len(secrets)
        
    def check_render_status(self):
        """Check Render deployment status"""
        print("\n[CHECK] Render Status...")
        
        try:
            response = requests.get(
                "https://cafe24-automation.onrender.com/",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                mode = data.get('mode', 'unknown')
                status = data.get('status', 'unknown')
                
                print(f"  Status: {status}")
                print(f"  Mode: {mode}")
                
                self.status["render"] = True
                self.status["production"] = (mode == 'production')
                
                return True
            else:
                print(f"  [ERROR] Status code: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("  [ERROR] Timeout - service may be starting")
        except Exception as e:
            print(f"  [ERROR] {e}")
            
        return False
        
    def trigger_deployment(self):
        """Trigger GitHub Actions deployment"""
        print("\n[DEPLOY] Triggering deployment...")
        
        try:
            result = subprocess.run(
                ['gh', 'workflow', 'run', 'auto-deploy.yml'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("  [OK] Deployment triggered")
                
                # Get workflow URL
                time.sleep(2)
                result = subprocess.run(
                    ['gh', 'run', 'list', '--limit', '1', '--json', 'url'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    runs = json.loads(result.stdout)
                    if runs:
                        print(f"  [URL] {runs[0]['url']}")
                        
                return True
            else:
                print(f"  [ERROR] {result.stderr}")
                
        except Exception as e:
            print(f"  [ERROR] {e}")
            
        return False
        
    def display_status(self):
        """Display current status"""
        print("\n" + "-" * 40)
        print("CURRENT STATUS:")
        print("-" * 40)
        
        icons = {
            True: "[OK]",
            False: "[X]"
        }
        
        print(f"Config Loaded:  {icons[self.status['config']]}")
        print(f"GitHub Secrets: {icons[self.status['github']]}")
        print(f"Render Online:  {icons[self.status['render']]}")
        print(f"Production:     {icons[self.status['production']]}")
        
        print("-" * 40)
        
        elapsed = (datetime.now() - self.start_time).seconds
        print(f"Running for: {elapsed}s")
        
    def auto_sync_once(self):
        """Run one sync cycle"""
        print("\n[AUTO-SYNC] Starting sync cycle...")
        
        # 1. Load config
        if not self.status["config"]:
            if not self.load_config():
                return False
                
        # 2. Check/sync GitHub
        if not self.check_github_secrets():
            self.sync_github_secrets()
            
        # 3. Check Render
        self.check_render_status()
        
        # 4. Trigger deployment if needed
        if not self.status["production"] and self.status["github"]:
            answer = input("\nDeploy to production? (y/n): ")
            if answer.lower() == 'y':
                self.trigger_deployment()
                
        return True
        
    def monitor_continuous(self):
        """Continuous monitoring mode"""
        print("\n[MONITOR] Starting continuous monitoring...")
        print("Press Ctrl+C to stop\n")
        
        cycle = 0
        while True:
            try:
                cycle += 1
                self.clear_screen()
                self.print_header()
                
                print(f"\nCycle #{cycle}")
                
                # Check status
                self.check_render_status()
                
                # Display
                self.display_status()
                
                # Auto-sync every 5 cycles (5 minutes)
                if cycle % 5 == 0:
                    self.auto_sync_once()
                    
                # Wait
                print("\nNext check in 60 seconds...")
                time.sleep(60)
                
            except KeyboardInterrupt:
                print("\n\n[STOP] Monitoring stopped")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}")
                time.sleep(60)
                
    def run(self):
        """Main run method"""
        self.print_header()
        
        print("\nSelect mode:")
        print("1. One-time sync")
        print("2. Continuous monitoring")
        print("3. Check status only")
        
        choice = input("\nChoice (1-3): ")
        
        if choice == '1':
            self.auto_sync_once()
            self.display_status()
        elif choice == '2':
            self.monitor_continuous()
        elif choice == '3':
            self.load_config()
            self.check_github_secrets()
            self.check_render_status()
            self.display_status()
        else:
            print("Invalid choice")


def main():
    monitor = SimpleSyncMonitor()
    monitor.run()


if __name__ == "__main__":
    main()