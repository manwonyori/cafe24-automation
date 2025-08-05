#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카페24 토큰 갱신 도우미
만료된 토큰을 자동으로 갱신하는 스크립트
"""
import os
import json
import requests
from datetime import datetime, timedelta
import pytz

# 한국 시간대
KST = pytz.timezone('Asia/Seoul')

def refresh_cafe24_token():
    """토큰 갱신 실행"""
    print("[카페24 토큰 갱신 시작]")
    print("=" * 50)
    
    # 현재 토큰 파일 읽기
    token_file = 'oauth_token.json'
    
    if not os.path.exists(token_file):
        print(f"[오류] 토큰 파일을 찾을 수 없습니다: {token_file}")
        return False
    
    try:
        with open(token_file, 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        
        print(f"[정보] 현재 토큰 정보:")
        print(f"  - Mall ID: {token_data.get('mall_id')}")
        print(f"  - Client ID: {token_data.get('client_id')}")
        print(f"  - 만료 시간: {token_data.get('expires_at')}")
        
        # 토큰 갱신 요청
        refresh_token = token_data.get('refresh_token')
        client_id = token_data.get('client_id')
        client_secret = token_data.get('client_secret')
        mall_id = token_data.get('mall_id')
        
        if not all([refresh_token, client_id, client_secret, mall_id]):
            print("[오류] 필수 정보가 누락되었습니다.")
            return False
        
        # 토큰 갱신 API 호출
        refresh_url = f"https://{mall_id}.cafe24api.com/api/v2/oauth/token"
        
        refresh_data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        print("[진행] 토큰 갱신 요청 중...")
        
        response = requests.post(refresh_url, data=refresh_data, timeout=10)
        
        if response.status_code == 200:
            new_token_data = response.json()
            print("[성공] 새 토큰을 받았습니다.")
            
            # 새 토큰 정보 업데이트
            now = datetime.now()
            expires_in = new_token_data.get('expires_in', 7200)  # 기본값 2시간
            
            updated_token_data = {
                **token_data,  # 기존 정보 유지
                'access_token': new_token_data['access_token'],
                'refresh_token': new_token_data.get('refresh_token', refresh_token),
                'expires_at': (now + timedelta(seconds=expires_in)).isoformat(),
                'refresh_token_expires_at': (now + timedelta(days=14)).isoformat(),
                'issued_at': now.isoformat()
            }
            
            # 토큰 파일 저장
            with open(token_file, 'w', encoding='utf-8') as f:
                json.dump(updated_token_data, f, ensure_ascii=False, indent=2)
            
            print(f"[완료] 토큰이 갱신되었습니다.")
            print(f"  - 새 액세스 토큰: ***{updated_token_data['access_token'][-10:]}")
            print(f"  - 새 만료 시간: {updated_token_data['expires_at']}")
            
            return True
        else:
            print(f"[실패] 토큰 갱신 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"[오류] 토큰 갱신 중 오류 발생: {str(e)}")
        return False

def check_token_status():
    """토큰 상태 확인"""
    print("\n[토큰 상태 확인]")
    print("-" * 30)
    
    token_file = 'oauth_token.json'
    
    if not os.path.exists(token_file):
        print("[오류] 토큰 파일이 없습니다.")
        return False
    
    try:
        with open(token_file, 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        
        expires_at_str = token_data.get('expires_at', '')
        
        if expires_at_str:
            # 시간 파싱
            try:
                expires_at = datetime.fromisoformat(expires_at_str.replace('.000', ''))
                now = datetime.now()
                time_left = expires_at - now
                
                if time_left.total_seconds() > 0:
                    print(f"[정상] 토큰이 유효합니다.")
                    print(f"  남은 시간: {time_left}")
                    return True
                else:
                    print(f"[만료] 토큰이 만료되었습니다.")
                    print(f"  만료 시간: {expires_at}")
                    return False
            except:
                print("[오류] 토큰 시간 정보를 파싱할 수 없습니다.")
                return False
        else:
            print("[경고] 만료 시간 정보가 없습니다.")
            return False
            
    except Exception as e:
        print(f"[오류] 토큰 상태 확인 실패: {str(e)}")
        return False

def main():
    """메인 함수"""
    print("=" * 50)
    print("카페24 토큰 갱신 도우미")
    print("=" * 50)
    
    # 1. 현재 토큰 상태 확인
    is_valid = check_token_status()
    
    # 2. 필요시 토큰 갱신
    if not is_valid:
        print("\n[결정] 토큰 갱신이 필요합니다.")
        success = refresh_cafe24_token()
        
        if success:
            print("\n[최종] 토큰 갱신이 완료되었습니다!")
            check_token_status()  # 갱신 후 상태 재확인
        else:
            print("\n[최종] 토큰 갱신에 실패했습니다.")
            print("수동으로 새 토큰을 발급받아야 합니다.")
    else:
        print("\n[최종] 토큰이 유효합니다. 갱신이 불필요합니다.")

if __name__ == '__main__':
    main()