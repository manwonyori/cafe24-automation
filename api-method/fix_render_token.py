#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render 서버 토큰 문제 해결
"""
import requests
import json
import sys
import io
import os

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=== Render 서버 토큰 문제 해결 가이드 ===\n")

# 1. 현재 로컬 토큰 확인
print("1. 로컬 토큰 파일 확인:")
token_file = 'oauth_token.json'
if os.path.exists(token_file):
    with open(token_file, 'r', encoding='utf-8') as f:
        local_token = json.load(f)
    print(f"✅ 로컬 토큰 파일 존재")
    print(f"- Access Token: ***{local_token.get('access_token', '')[-10:]}")
    print(f"- Mall ID: {local_token.get('mall_id')}")
    print(f"- 발급일: {local_token.get('issued_at')}")
else:
    print("❌ 로컬 토큰 파일 없음")

# 2. 토큰 갱신 API 호출
print("\n2. 토큰 갱신 방법:")
print("-"*30)

# 방법 1: 로컬에서 토큰 갱신
print("\n방법 1: 로컬에서 토큰 갱신 후 Render에 업데이트")
print("```python")
print("# 로컬에서 실행")
print("python refresh_token.py")
print("# 또는")
print("python manual_refresh_token.py")
print("```")

# 방법 2: Render 환경변수 직접 설정
print("\n방법 2: Render 대시보드에서 환경변수 업데이트")
print("1. https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env 접속")
print("2. 다음 환경변수 확인/추가:")
print("   - CAFE24_ACCESS_TOKEN")
print("   - CAFE24_REFRESH_TOKEN")
print("   - CAFE24_CLIENT_ID")
print("   - CAFE24_CLIENT_SECRET")

# 방법 3: API를 통한 토큰 갱신
print("\n방법 3: API를 통한 직접 토큰 갱신")
base_url = 'https://cafe24-automation.onrender.com'
print(f"POST {base_url}/api/refresh-token")

# 3. 빠른 해결책
print("\n\n3. 🚀 빠른 해결책:")
print("-"*30)
print("1. 로컬에서 토큰 갱신:")
print("   python refresh_token.py")
print("\n2. Render 서버 재시작:")
print("   - Render 대시보드에서 'Manual Deploy' > 'Deploy latest commit'")
print("\n3. 또는 환경변수에 직접 토큰 추가:")
print("   - Render 대시보드 > Environment")

# 4. 테스트용 토큰 갱신 스크립트
print("\n\n4. 토큰 갱신 스크립트:")
print("-"*30)
with open('quick_token_refresh.py', 'w', encoding='utf-8') as f:
    f.write('''#!/usr/bin/env python3
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
    
    print("\\n다음 단계:")
    print("1. git add oauth_token.json")
    print("2. git commit -m 'Update OAuth token'")
    print("3. git push")
    print("4. Render가 자동으로 재배포됨")
else:
    print(f"❌ 토큰 갱신 실패: {response.status_code}")
    print(response.text)
''')

print("✅ quick_token_refresh.py 생성됨")
print("\n실행: python quick_token_refresh.py")

# 5. 현재 상태 요약
print("\n\n5. 현재 상태 요약:")
print("-"*30)
print("❌ Render 서버의 OAuth 토큰이 유효하지 않음")
print("❌ 이로 인해 Cafe24 API 호출 실패")
print("❌ 제품 목록을 가져올 수 없음")
print("\n✅ 해결책: 토큰 갱신 후 재배포")