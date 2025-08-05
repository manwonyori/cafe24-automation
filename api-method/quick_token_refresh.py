#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import os

# 설정 로드
from config import OAUTH_CONFIG

# 토큰 파일 읽기
with open('oauth_token.json', 'r') as f:
    token_data = json.load(f)

# 토큰 갱신
response = requests.post(
    'https://manwonyori.cafe24api.com/api/v2/oauth/token',
    data={
        'grant_type': 'refresh_token',
        'refresh_token': token_data['refresh_token'],
        'client_id': OAUTH_CONFIG['client_id'],
        'client_secret': OAUTH_CONFIG['client_secret']
    }
)

if response.status_code == 200:
    new_token = response.json()
    print("✅ 토큰 갱신 성공!")
    print(f"새 Access Token: ***{new_token['access_token'][-10:]}")
    
    # 토큰 저장
    token_data.update(new_token)
    with open('oauth_token.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print("\n다음 단계:")
    print("1. git add oauth_token.json")
    print("2. git commit -m 'Update OAuth token'")
    print("3. git push")
    print("4. Render가 자동으로 재배포됨")
else:
    print(f"❌ 토큰 갱신 실패: {response.status_code}")
    print(response.text)
