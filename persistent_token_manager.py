#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
영구 토큰 관리자 - Render 디스크에 토큰 저장
"""
import os
import json
import shutil
from datetime import datetime
from pathlib import Path

class PersistentTokenManager:
    def __init__(self):
        # Render 환경에서는 /opt/render/project/.data 사용
        # 로컬에서는 현재 디렉토리 사용
        if os.environ.get('RENDER'):
            self.token_dir = Path('/opt/render/project/.data')
        else:
            self.token_dir = Path('.data')
        
        self.token_dir.mkdir(exist_ok=True)
        self.token_path = self.token_dir / 'oauth_token.json'
        self.backup_path = self.token_dir / 'oauth_token_backup.json'
        
    def save_token(self, token_data):
        """토큰을 영구 저장소에 저장"""
        try:
            # 기존 토큰 백업
            if self.token_path.exists():
                shutil.copy(self.token_path, self.backup_path)
            
            # 새 토큰 저장
            with open(self.token_path, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, ensure_ascii=False, indent=2)
            
            print(f"[OK] 토큰이 영구 저장소에 저장됨: {self.token_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] 토큰 저장 실패: {str(e)}")
            # 백업에서 복구
            if self.backup_path.exists():
                shutil.copy(self.backup_path, self.token_path)
            return False
    
    def load_token(self):
        """영구 저장소에서 토큰 로드"""
        try:
            if self.token_path.exists():
                with open(self.token_path, 'r', encoding='utf-8') as f:
                    token_data = json.load(f)
                
                # 만료 시간 확인
                expires_at = datetime.fromisoformat(
                    token_data['expires_at'].replace('.000', '')
                )
                
                if datetime.now() < expires_at:
                    print(f"[OK] 유효한 토큰 로드됨")
                    return token_data
                else:
                    print(f"[WARN] 토큰이 만료됨")
                    return None
            else:
                print(f"[INFO] 저장된 토큰 없음")
                return None
                
        except Exception as e:
            print(f"[ERROR] 토큰 로드 실패: {str(e)}")
            return None
    
    def get_token(self):
        """토큰 가져오기 (우선순위: 영구저장소 > 환경변수 > 로컬파일)"""
        # 1. 영구 저장소
        token_data = self.load_token()
        if token_data:
            return token_data.get('access_token')
        
        # 2. 환경 변수
        env_token = os.environ.get('CAFE24_ACCESS_TOKEN')
        if env_token:
            print("[INFO] 환경 변수에서 토큰 사용")
            return env_token
        
        # 3. 로컬 파일 (폴백)
        try:
            with open('oauth_token.json', 'r', encoding='utf-8') as f:
                local_data = json.load(f)
                # 영구 저장소에 복사
                self.save_token(local_data)
                return local_data.get('access_token')
        except:
            pass
        
        return None
    
    def update_token_on_refresh(self, new_token_data):
        """토큰 갱신 시 자동 저장"""
        # 영구 저장소에 저장
        if self.save_token(new_token_data):
            # 로컬 파일도 업데이트 (개발 환경용)
            try:
                with open('oauth_token.json', 'w', encoding='utf-8') as f:
                    json.dump(new_token_data, f, ensure_ascii=False, indent=2)
            except:
                pass
            
            return True
        return False

# 싱글톤 인스턴스
persistent_token_manager = PersistentTokenManager()