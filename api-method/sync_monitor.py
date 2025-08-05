#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 API Key 실시간 동기화 모니터링 시스템
Real-time synchronization monitoring with auto-retry
"""

import os
import json
import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, Optional, List
import threading
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn


class SyncMonitor:
    def __init__(self):
        self.console = Console()
        self.config_path = self._find_config()
        self.sync_status = {
            "config_loaded": False,
            "github_secrets": False,
            "render_env": False,
            "deployment": False,
            "production_mode": False
        }
        self.retry_counts = {key: 0 for key in self.sync_status}
        self.max_retries = 3
        self.last_sync = None
        self.errors = []
        
    def _find_config(self) -> Optional[str]:
        """Find Cafe24 config file"""
        paths = [
            r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json",
            "config/oauth_token.json",
            "../카페24_프로젝트/01_ACTIVE_PROJECT/config/oauth_token.json"
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        return None
        
    def load_config(self) -> Optional[Dict]:
        """Load configuration with retry"""
        for attempt in range(self.max_retries):
            try:
                if self.config_path and os.path.exists(self.config_path):
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        self.sync_status["config_loaded"] = True
                        return config
            except Exception as e:
                self.errors.append(f"Config load error: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
                
        return None
        
    def check_github_secrets(self) -> bool:
        """Check GitHub secrets status"""
        try:
            result = subprocess.run(
                ['gh', 'secret', 'list'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                secrets = result.stdout
                required = ['CAFE24_MALL_ID', 'CAFE24_CLIENT_ID', 
                          'CAFE24_CLIENT_SECRET', 'CAFE24_ACCESS_TOKEN']
                
                missing = [s for s in required if s not in secrets]
                
                if not missing:
                    self.sync_status["github_secrets"] = True
                    return True
                else:
                    self.errors.append(f"Missing secrets: {', '.join(missing)}")
                    
        except Exception as e:
            self.errors.append(f"GitHub check error: {e}")
            
        return False
        
    def sync_github_secrets(self, config: Dict) -> bool:
        """Sync secrets to GitHub with retry"""
        secrets = {
            "CAFE24_MALL_ID": config.get('mall_id'),
            "CAFE24_CLIENT_ID": config.get('client_id'),
            "CAFE24_CLIENT_SECRET": config.get('client_secret'),
            "CAFE24_ACCESS_TOKEN": config.get('access_token'),
            "CAFE24_REFRESH_TOKEN": config.get('refresh_token')
        }
        
        success_count = 0
        for name, value in secrets.items():
            if not value:
                continue
                
            for attempt in range(self.max_retries):
                try:
                    result = subprocess.run(
                        ['gh', 'secret', 'set', name],
                        input=value,
                        text=True,
                        capture_output=True
                    )
                    
                    if result.returncode == 0:
                        success_count += 1
                        break
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        self.errors.append(f"Failed to set {name}: {e}")
                    time.sleep(2 ** attempt)
                    
        self.sync_status["github_secrets"] = success_count == len(secrets)
        return self.sync_status["github_secrets"]
        
    def check_render_sync(self) -> bool:
        """Check Render environment sync status"""
        try:
            response = requests.get("https://cafe24-automation.onrender.com/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                mode = data.get('mode', 'unknown')
                
                if mode == 'production':
                    self.sync_status["render_env"] = True
                    self.sync_status["production_mode"] = True
                    return True
                elif mode == 'demo':
                    self.sync_status["render_env"] = True
                    self.sync_status["production_mode"] = False
                    
        except Exception as e:
            self.errors.append(f"Render check error: {e}")
            
        return False
        
    def trigger_github_workflow(self) -> bool:
        """Trigger GitHub Actions workflow"""
        try:
            result = subprocess.run(
                ['gh', 'workflow', 'run', 'auto-deploy.yml'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.sync_status["deployment"] = True
                return True
                
        except Exception as e:
            self.errors.append(f"Workflow trigger error: {e}")
            
        return False
        
    def create_status_table(self) -> Table:
        """Create status table for display"""
        table = Table(title="Sync Status", show_header=True)
        table.add_column("Component", style="cyan", width=20)
        table.add_column("Status", width=15)
        table.add_column("Details", style="dim", width=30)
        
        # Config status
        config_status = "✅ Loaded" if self.sync_status["config_loaded"] else "❌ Not Found"
        table.add_row("Config File", config_status, self.config_path or "Not found")
        
        # GitHub Secrets
        github_status = "✅ Synced" if self.sync_status["github_secrets"] else "⏳ Pending"
        table.add_row("GitHub Secrets", github_status, "5 secrets required")
        
        # Render Environment
        render_status = "✅ Synced" if self.sync_status["render_env"] else "⏳ Pending"
        table.add_row("Render Environment", render_status, "6 environment variables")
        
        # Deployment
        deploy_status = "✅ Triggered" if self.sync_status["deployment"] else "⏳ Waiting"
        table.add_row("Deployment", deploy_status, "GitHub Actions workflow")
        
        # Production Mode
        prod_status = "✅ Active" if self.sync_status["production_mode"] else "❌ Demo Mode"
        table.add_row("Production Mode", prod_status, "https://cafe24-automation.onrender.com")
        
        return table
        
    def create_error_panel(self) -> Optional[Panel]:
        """Create error panel if errors exist"""
        if not self.errors:
            return None
            
        error_text = "\n".join(f"• {error}" for error in self.errors[-5:])
        return Panel(error_text, title="Recent Errors", style="red")
        
    def auto_sync(self):
        """Automatic synchronization with retry logic"""
        self.console.print("[bold green]Starting Auto-Sync Monitor...[/bold green]")
        
        # Load config
        config = self.load_config()
        if not config:
            self.console.print("[bold red]Failed to load configuration![/bold red]")
            return
            
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            # Check GitHub secrets
            task1 = progress.add_task("Checking GitHub secrets...", total=None)
            if not self.check_github_secrets():
                progress.update(task1, description="Syncing GitHub secrets...")
                self.sync_github_secrets(config)
            progress.update(task1, completed=True)
            
            # Trigger deployment if needed
            if not self.sync_status["production_mode"]:
                task2 = progress.add_task("Triggering deployment...", total=None)
                self.trigger_github_workflow()
                progress.update(task2, completed=True)
                
                # Wait for deployment
                task3 = progress.add_task("Waiting for deployment...", total=100)
                for i in range(100):
                    time.sleep(3)
                    progress.update(task3, advance=1)
                    if self.check_render_sync():
                        break
                        
        self.last_sync = datetime.now()
        
    def monitor_loop(self):
        """Main monitoring loop"""
        with Live(self.create_status_table(), refresh_per_second=1) as live:
            while True:
                try:
                    # Update status
                    if self.last_sync:
                        time_since = (datetime.now() - self.last_sync).seconds
                        if time_since > 300:  # Re-sync every 5 minutes
                            self.auto_sync()
                            
                    # Update display
                    table = self.create_status_table()
                    
                    if self.errors:
                        error_panel = self.create_error_panel()
                        live.update(Panel.fit([table, error_panel]))
                    else:
                        live.update(table)
                        
                    # Check status
                    self.check_render_sync()
                    
                    time.sleep(5)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.errors.append(f"Monitor error: {e}")
                    
    def run(self):
        """Run the monitor"""
        self.console.print(Panel.fit(
            "[bold cyan]Cafe24 API Key Sync Monitor[/bold cyan]\n"
            "Real-time synchronization status with auto-retry\n"
            "Press Ctrl+C to exit",
            border_style="cyan"
        ))
        
        # Initial sync
        self.auto_sync()
        
        # Start monitoring
        self.monitor_loop()
        
        self.console.print("\n[bold yellow]Monitor stopped[/bold yellow]")


def main():
    """Main entry point"""
    # Check if rich is installed
    try:
        import rich
    except ImportError:
        print("Installing required packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "rich"])
        
    monitor = SyncMonitor()
    monitor.run()


if __name__ == "__main__":
    main()