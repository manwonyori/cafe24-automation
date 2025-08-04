#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 환경변수 복사 도구
Render 대시보드에 쉽게 붙여넣기 위한 환경변수 생성
"""

import os
import json


def load_config():
    """설정 파일 로드"""
    config_paths = [
        r"C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json",
        "config/oauth_token.json",
        "../카페24_프로젝트/01_ACTIVE_PROJECT/config/oauth_token.json"
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
    return None


def generate_env_vars(config):
    """환경변수 문자열 생성"""
    env_vars = f"""CAFE24_MALL_ID={config['mall_id']}
CAFE24_CLIENT_ID={config['client_id']}
CAFE24_CLIENT_SECRET={config['client_secret']}
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN={config['access_token']}
CAFE24_REFRESH_TOKEN={config['refresh_token']}"""
    
    return env_vars


def main():
    print("=" * 60)
    print("Cafe24 환경변수 복사 도구")
    print("=" * 60)
    
    # 설정 로드
    config = load_config()
    
    if not config:
        print("\n[ERROR] 설정 파일을 찾을 수 없습니다.")
        return
        
    # 환경변수 생성
    env_vars = generate_env_vars(config)
    
    print("\n[OK] 환경변수 생성 완료!")
    print("\n" + "-" * 60)
    print(env_vars)
    print("-" * 60)
    
    # 파일로 저장
    with open("render_env_vars.txt", "w") as f:
        f.write(env_vars)
    print("\n[SAVED] render_env_vars.txt 파일로 저장되었습니다!")
        
    print("\n[GUIDE] Render 설정 방법:")
    print("1. https://dashboard.render.com 로그인")
    print("2. cafe24-automation 서비스 선택")
    print("3. Environment 탭 클릭")
    print("4. 위 환경변수를 붙여넣기 (Ctrl+V)")
    print("5. Save Changes 클릭")
    print("6. Manual Deploy > Deploy latest commit")
    print("\n[INFO] 2-5분 후 Production 모드가 활성화됩니다!")
    
    # .env 파일도 생성
    with open(".env.render", "w") as f:
        f.write("# Render 환경변수 설정\n")
        f.write("# 이 내용을 Render Environment 탭에 복사하세요\n\n")
        f.write(env_vars)
        
    print("\n[TIP] 추가로 .env.render 파일도 생성되었습니다.")


if __name__ == "__main__":
    main()