#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
보안 API 키 관리자
"""
import os
import json
from cryptography.fernet import Fernet
from pathlib import Path
import hashlib

class SecureAPIManager:
    def __init__(self):
        self.config_dir = Path('config')
        self.config_dir.mkdir(exist_ok=True)
        self.key_file = self.config_dir / '.api_key'
        self.encrypted_file = self.config_dir / 'encrypted_apis.json'
        
    def _get_or_create_key(self):
        """암호화 키 생성 또는 로드"""
        if self.key_file.exists():
            return self.key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)
            # 파일 권한 설정 (Windows에서는 제한적)
            if os.name != 'nt':
                os.chmod(self.key_file, 0o600)
            return key
    
    def encrypt_api_key(self, api_key, service_name):
        """API 키 암호화 및 저장"""
        key = self._get_or_create_key()
        f = Fernet(key)
        
        # API 키 암호화
        encrypted_key = f.encrypt(api_key.encode()).decode()
        
        # 기존 암호화된 키들 로드
        encrypted_data = {}
        if self.encrypted_file.exists():
            with open(self.encrypted_file, 'r') as file:
                encrypted_data = json.load(file)
        
        # 새 키 추가
        encrypted_data[service_name] = {
            'encrypted_key': encrypted_key,
            'key_hash': hashlib.sha256(api_key.encode()).hexdigest()[:8],
            'added_at': os.path.getmtime(self.encrypted_file) if self.encrypted_file.exists() else None
        }
        
        # 저장
        with open(self.encrypted_file, 'w') as file:
            json.dump(encrypted_data, file, indent=2)
        
        print(f"[OK] {service_name} API key encrypted successfully.")
        return True
    
    def get_api_key(self, service_name):
        """암호화된 API 키 복호화"""
        if not self.encrypted_file.exists():
            return None
            
        key = self._get_or_create_key()
        f = Fernet(key)
        
        with open(self.encrypted_file, 'r') as file:
            encrypted_data = json.load(file)
        
        if service_name not in encrypted_data:
            return None
        
        encrypted_key = encrypted_data[service_name]['encrypted_key']
        decrypted_key = f.decrypt(encrypted_key.encode()).decode()
        
        return decrypted_key

# 사용 예시
if __name__ == "__main__":
    # API 키 암호화 예시 (실제 사용시 별도 스크립트로 실행)
    # manager = SecureAPIManager()
    # manager.encrypt_api_key("your-api-key-here", "service-name")
    pass