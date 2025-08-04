#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카페24 OAuth 토큰 자동 관리 시스템
- 환경변수에서 client_secret 읽기  
- 자동 갱신 백그라운드 스케줄러
- 토큰 만료 전 자동 갱신
"""
import json
import requests
import os
import threading
import time
from datetime import datetime, timedelta
import schedule

class Cafe24AutoTokenManager:
    def __init__(self, token_file=None):
        if token_file is None:
            self.token_file = 'oauth_token.json'
        else:
            self.token_file = token_file
        self.token_data = self.load_token()
        self.client_secret = None
        self.refresh_thread = None
        self.running = False
        
    def load_token(self):
        """토큰 파일 로드"""
        try:
            with open(self.token_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def save_token(self):
        """토큰 파일 저장"""
        with open(self.token_file, 'w', encoding='utf-8') as f:
            json.dump(self.token_data, f, ensure_ascii=False, indent=2)
    
    def get_client_secret(self):
        """환경변수 또는 설정파일에서 client_secret 가져오기"""
        # 1. 환경변수에서 시도
        secret = os.environ.get('CAFE24_CLIENT_SECRET')
        if secret:
            return secret
            
        # 2. 토큰 파일에 저장된 값 사용
        if self.token_data and 'client_secret' in self.token_data:
            return self.token_data['client_secret']
            
        return None
    
    def refresh_token(self):
        """리프레시 토큰으로 액세스 토큰 갱신"""
        if not self.token_data:
            print("[FAIL] 토큰 데이터가 없습니다.")
            return False
            
        # 리프레시 토큰 만료 확인
        refresh_expires = datetime.fromisoformat(
            self.token_data['refresh_token_expires_at'].replace('.000', '')
        )
        
        if datetime.now() > refresh_expires:
            print("[FAIL] 리프레시 토큰도 만료되었습니다. 재인증이 필요합니다.")
            return False
        
        # client_secret 가져오기
        client_secret = self.get_client_secret()
        if not client_secret:
            print("[FAIL] Client Secret을 찾을 수 없습니다.")
            return False
        
        print(f"🔄 토큰 자동 갱신 중... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        
        # 토큰 갱신 요청
        try:
            response = requests.post(
                f"https://{self.token_data['mall_id']}.cafe24api.com/api/v2/oauth/token",
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': self.token_data['refresh_token']
                },
                auth=(self.token_data['client_id'], client_secret)
            )
            
            if response.status_code == 200:
                new_token = response.json()
                
                # 토큰 업데이트
                now = datetime.now()
                self.token_data['access_token'] = new_token['access_token']
                self.token_data['expires_at'] = (
                    now + timedelta(seconds=new_token.get('expires_in', 7200))
                ).isoformat() + '.000'
                self.token_data['refresh_token'] = new_token['refresh_token']
                self.token_data['refresh_token_expires_at'] = (
                    now + timedelta(seconds=new_token.get('refresh_token_expires_in', 1209600))
                ).isoformat() + '.000'
                self.token_data['issued_at'] = now.isoformat() + '.000'
                
                self.save_token()
                print("[OK] 토큰 자동 갱신 성공!")
                return True
                
            else:
                print(f"[FAIL] 토큰 갱신 실패: {response.status_code}")
                print(f"응답: {response.text}")
                return False
                
        except Exception as e:
            print(f"[FAIL] 토큰 갱신 오류: {e}")
            return False
    
    def check_and_refresh(self):
        """토큰 상태 확인 후 필요시 갱신"""
        if not self.token_data:
            return
            
        expires_at = datetime.fromisoformat(self.token_data['expires_at'].replace('.000', ''))
        now = datetime.now()
        
        # 30분 여유를 두고 갱신
        if now > (expires_at - timedelta(minutes=30)):
            self.refresh_token()
    
    def start_auto_refresh(self):
        """백그라운드 자동 갱신 시작"""
        self.running = True
        
        # 스케줄 설정: 30분마다 체크
        schedule.every(30).minutes.do(self.check_and_refresh)
        print(f"✓ 자동 토큰 갱신 설정: 30분마다 실행")
        
        # 즉시 한 번 체크
        self.check_and_refresh()
        
        def run_schedule():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 스케줄 체크
        
        self.refresh_thread = threading.Thread(target=run_schedule, daemon=True)
        self.refresh_thread.start()
        print("[OK] 자동 토큰 갱신 스케줄러 시작")
    
    def stop_auto_refresh(self):
        """백그라운드 자동 갱신 중지"""
        self.running = False
        if self.refresh_thread:
            self.refresh_thread.join()
        print("⏹️ 자동 토큰 갱신 스케줄러 중지")
    
    def get_valid_token(self):
        """유효한 토큰 반환 (필요시 갱신)"""
        if not self.token_data:
            return None
            
        expires_at = datetime.fromisoformat(self.token_data['expires_at'].replace('.000', ''))
        now = datetime.now()
        
        # 5분 여유를 두고 체크
        if now > (expires_at - timedelta(minutes=5)):
            if self.refresh_token():
                return self.token_data['access_token']
            return None
        
        return self.token_data['access_token']

# 싱글톤 인스턴스
_token_manager = None

def get_token_manager():
    """토큰 매니저 싱글톤 인스턴스 반환"""
    global _token_manager
    if _token_manager is None:
        _token_manager = Cafe24AutoTokenManager()
    return _token_manager