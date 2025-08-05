#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수동 토큰 갱신
"""
import json
import requests
from datetime import datetime, timedelta

# 토큰 파일 읽기
with open('oauth_token.json', 'r', encoding='utf-8') as f:
    token_data = json.load(f)

print(f"Current token expires at: {token_data['expires_at']}")
print(f"Mall ID: {token_data['mall_id']}")
print(f"Client ID: {token_data['client_id']}")

# 갱신 요청
refresh_url = f"https://{token_data['mall_id']}.cafe24api.com/api/v2/oauth/token"

refresh_data = {
    'grant_type': 'refresh_token',
    'refresh_token': token_data['refresh_token']
}

# client_id와 client_secret으로 인증
auth = (token_data['client_id'], token_data['client_secret'])

print(f"\n갱신 요청 중...")
response = requests.post(refresh_url, data=refresh_data, auth=auth)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    new_token_info = response.json()
    
    # 토큰 데이터 업데이트
    now = datetime.now()
    token_data['access_token'] = new_token_info['access_token']
    token_data['refresh_token'] = new_token_info['refresh_token']
    token_data['expires_at'] = (now + timedelta(seconds=new_token_info.get('expires_in', 7200))).isoformat() + '.000'
    token_data['refresh_token_expires_at'] = (now + timedelta(seconds=new_token_info.get('refresh_token_expires_in', 1209600))).isoformat() + '.000'
    token_data['issued_at'] = now.isoformat() + '.000'
    
    # 파일에 저장
    with open('oauth_token.json', 'w', encoding='utf-8') as f:
        json.dump(token_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 토큰 갱신 성공!")
    print(f"새 토큰: ***{new_token_info['access_token'][-10:]}")
    print(f"만료 시간: {token_data['expires_at']}")
    
    # 환경 변수 업데이트 안내
    print(f"\n다음 환경 변수를 Render에 업데이트하세요:")
    print(f"CAFE24_ACCESS_TOKEN={new_token_info['access_token']}")
    print(f"CAFE24_REFRESH_TOKEN={new_token_info['refresh_token']}")
else:
    print(f"\n❌ 토큰 갱신 실패")
    print("새로운 인증이 필요합니다.")