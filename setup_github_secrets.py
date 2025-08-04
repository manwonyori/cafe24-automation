#!/usr/bin/env python3
"""
Setup GitHub Secrets for Cafe24 automation
Requires GitHub CLI (gh) to be installed and authenticated
"""

import os
import json
import subprocess
import sys
from typing import Dict


def load_cafe24_config() -> Dict:
    """Load Cafe24 configuration"""
    config_paths = [
        r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json",
        "config/oauth_token.json",
        "../카페24_프로젝트/01_ACTIVE_PROJECT/config/oauth_token.json"
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            print(f"[OK] Found config at: {path}")
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
    raise FileNotFoundError("Cafe24 config file not found")


def check_gh_cli():
    """Check if GitHub CLI is installed"""
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] GitHub CLI is installed")
            return True
    except FileNotFoundError:
        pass
        
    print("[ERROR] GitHub CLI not found")
    print("\nInstall GitHub CLI:")
    print("  Windows: winget install --id GitHub.cli")
    print("  Mac: brew install gh")
    print("  Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md")
    return False


def check_gh_auth():
    """Check if GitHub CLI is authenticated"""
    result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
    if result.returncode == 0:
        print("[OK] GitHub CLI is authenticated")
        return True
        
    print("[ERROR] GitHub CLI not authenticated")
    print("\nRun: gh auth login")
    return False


def set_github_secret(name: str, value: str, repo: str = None):
    """Set a GitHub secret"""
    cmd = ['gh', 'secret', 'set', name]
    if repo:
        cmd.extend(['--repo', repo])
        
    try:
        # Use input pipe to avoid command line exposure
        result = subprocess.run(
            cmd,
            input=value,
            text=True,
            capture_output=True
        )
        
        if result.returncode == 0:
            print(f"[OK] Set secret: {name}")
            return True
        else:
            print(f"[ERROR] Failed to set {name}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error setting {name}: {e}")
        return False


def get_render_deploy_hook():
    """Get Render deploy hook URL"""
    print("\n[INFO] Render Deploy Hook URL 설정")
    print("1. https://dashboard.render.com 접속")
    print("2. cafe24-automation 서비스 선택")
    print("3. Settings 탭 → Deploy Hook")
    print("4. URL 복사 (https://api.render.com/deploy/srv-...)")
    
    hook_url = input("\nRender Deploy Hook URL 입력: ").strip()
    return hook_url if hook_url else None


def get_render_api_key():
    """Get Render API key"""
    print("\n[INFO] Render API Key 설정")
    print("1. https://dashboard.render.com 접속")
    print("2. Account Settings → API Keys")
    print("3. Create API Key")
    
    api_key = input("\nRender API Key 입력: ").strip()
    return api_key if api_key else None


def main():
    print("[SETUP] GitHub Secrets 자동 설정")
    print("=" * 60)
    
    # Check prerequisites
    if not check_gh_cli():
        return
        
    if not check_gh_auth():
        return
        
    # Get current repository
    result = subprocess.run(
        ['gh', 'repo', 'view', '--json', 'nameWithOwner'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("[ERROR] Not in a GitHub repository")
        return
        
    repo_info = json.loads(result.stdout)
    repo = repo_info['nameWithOwner']
    print(f"\n[REPO] Repository: {repo}")
    
    # Load Cafe24 config
    print("\n[LOAD] Loading Cafe24 configuration...")
    try:
        config = load_cafe24_config()
    except FileNotFoundError:
        print("[ERROR] Config file not found")
        return
        
    # Prepare secrets
    secrets = {
        "CAFE24_MALL_ID": config.get('mall_id'),
        "CAFE24_CLIENT_ID": config.get('client_id'),
        "CAFE24_CLIENT_SECRET": config.get('client_secret'),
        "CAFE24_ACCESS_TOKEN": config.get('access_token'),
        "CAFE24_REFRESH_TOKEN": config.get('refresh_token')
    }
    
    # Get Render credentials
    render_hook = get_render_deploy_hook()
    if render_hook:
        secrets["RENDER_DEPLOY_HOOK_URL"] = render_hook
        
    render_api_key = get_render_api_key()
    if render_api_key:
        secrets["RENDER_API_KEY"] = render_api_key
        
    # Set secrets
    print("\n[SETUP] Setting GitHub Secrets...")
    success_count = 0
    
    for name, value in secrets.items():
        if value:
            if set_github_secret(name, value, repo):
                success_count += 1
        else:
            print(f"[SKIP] Skipped {name} (no value)")
            
    print(f"\n[DONE] Set {success_count}/{len(secrets)} secrets")
    
    # Create workflow trigger
    if success_count > 0:
        print("\n[NEXT] Next steps:")
        print("1. Commit and push the workflow files:")
        print("   git add .github/")
        print("   git commit -m 'Add GitHub Actions automation'")
        print("   git push")
        print("\n2. The workflow will automatically run on push")
        print("3. Check Actions tab on GitHub for progress")
        
        # Generate manual command
        print("\n[TIP] Or trigger manually:")
        print("   gh workflow run auto-deploy.yml")
        
    print("\n[COMPLETE] Done!")


if __name__ == "__main__":
    main()