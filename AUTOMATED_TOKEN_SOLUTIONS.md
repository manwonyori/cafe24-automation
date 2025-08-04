# 🔄 자동 토큰 관리 솔루션

## 현재 문제점
- 토큰 갱신 시마다 Render 환경 변수를 수동으로 업데이트해야 함
- oauth_token.json 파일은 서버 재시작 시 사라짐
- 자동 갱신이 환경 변수에 반영되지 않음

## 해결책들

### 1. 🗄️ **Render Disk 사용 (권장)**
```python
# Render의 영구 디스크에 토큰 저장
TOKEN_PATH = '/opt/render/project/.data/oauth_token.json'

# app.py 수정
def get_headers():
    # 1. 영구 디스크에서 토큰 읽기
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'r') as f:
            token_data = json.load(f)
            return token_data['access_token']
    
    # 2. 환경 변수 폴백
    return os.environ.get('CAFE24_ACCESS_TOKEN')
```

**장점**: 
- 서버 재시작해도 유지
- 자동 갱신 즉시 반영
- 추가 서비스 불필요

### 2. 🔐 **PostgreSQL/SQLite 데이터베이스**
```python
# models.py
class OAuthToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String, nullable=False)
    refresh_token = db.Column(db.String, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**장점**: 
- 완전한 영구 저장
- 토큰 히스토리 관리
- 다중 서버 지원

### 3. 🔑 **암호화된 토큰 저장 (간단한 해결책)**
```python
# encrypted_token_manager.py
from cryptography.fernet import Fernet
import base64

class EncryptedTokenManager:
    def __init__(self):
        # 고정된 키 (환경 변수로 관리)
        self.key = os.environ.get('ENCRYPTION_KEY', 'your-32-byte-key-here')
        self.cipher = Fernet(base64.urlsafe_b64encode(self.key.encode()[:32]))
    
    def save_encrypted_token(self, token_data):
        # 토큰을 암호화해서 저장
        encrypted = self.cipher.encrypt(json.dumps(token_data).encode())
        with open('encrypted_token.bin', 'wb') as f:
            f.write(encrypted)
    
    def load_encrypted_token(self):
        # 암호화된 토큰 복호화
        with open('encrypted_token.bin', 'rb') as f:
            encrypted = f.read()
        decrypted = self.cipher.decrypt(encrypted)
        return json.loads(decrypted)
```

### 4. 🌐 **Render API 사용 (자동화)**
```python
# render_env_updater.py
import requests

class RenderEnvUpdater:
    def __init__(self):
        self.api_key = os.environ.get('RENDER_API_KEY')
        self.service_id = os.environ.get('RENDER_SERVICE_ID')
        
    def update_env_vars(self, new_token, refresh_token):
        """Render API로 환경 변수 자동 업데이트"""
        url = f"https://api.render.com/v1/services/{self.service_id}/env-vars"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = [
            {"key": "CAFE24_ACCESS_TOKEN", "value": new_token},
            {"key": "CAFE24_REFRESH_TOKEN", "value": refresh_token}
        ]
        
        response = requests.put(url, json=data, headers=headers)
        return response.status_code == 200
```

### 5. 🔄 **서버 내부 OAuth 재인증 (가장 간단)**
```python
# scheduled_reauth.py
import schedule

def auto_reauth():
    """매일 자동으로 OAuth 재인증"""
    # 서버에서 직접 /auth 엔드포인트 호출
    response = requests.get('http://localhost:5000/auth/refresh')
    if response.status_code == 200:
        print("토큰 자동 갱신 성공")

# 매일 오전 3시에 실행
schedule.every().day.at("03:00").do(auto_reauth)
```

## 🎯 추천 솔루션: Render Disk + 암호화

1. **즉시 적용 가능**
2. **추가 비용 없음**
3. **보안성 확보**
4. **자동 갱신 완벽 지원**

구현하시겠습니까?