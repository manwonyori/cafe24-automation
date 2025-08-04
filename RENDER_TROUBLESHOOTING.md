# Render.com 배포 문제 해결 가이드

## 🔍 일반적인 배포 문제 및 해결 방법

### 1. ❌ **Build Failed (빌드 실패)**

#### 증상
- "Build failed" 에러 메시지
- pip install 중 에러 발생

#### 해결 방법
```bash
# requirements.txt 확인
cd cafe24
pip freeze > requirements_test.txt

# 문제가 되는 패키지 제거 후 재시도
# 예: psutil, cryptography 등이 문제일 수 있음
```

**즉시 해결책**: requirements.txt 수정
```txt
requests>=2.28.0
pandas>=1.5.0
python-dotenv>=0.21.0
flask>=2.3.0
flask-cors>=4.0.0
openpyxl>=3.1.0
# psutil>=5.9.0  # 주석 처리
# cryptography>=40.0.0  # 주석 처리
```

### 2. ❌ **Deploy Failed (배포 실패)**

#### 증상
- "Deploy failed: No module named 'src'"
- ImportError 발생

#### 해결 방법
Python 경로 문제 수정이 필요합니다. `run_web.py` 파일 생성:

```python
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.web_app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

그리고 render.yaml 수정:
```yaml
startCommand: python run_web.py
```

### 3. ❌ **Service Unhealthy (서비스 비정상)**

#### 증상
- Health check failing
- 서비스가 계속 재시작됨

#### 해결 방법
1. 헬스체크 엔드포인트 확인
2. 환경 변수 누락 확인
3. 포트 설정 확인

### 4. ❌ **Environment Variables Missing (환경 변수 누락)**

#### 증상
- "CAFE24_MALL_ID not found" 에러
- API 연결 실패

#### 해결 방법
Render 대시보드에서:
1. Environment → Environment Variables
2. 다음 변수 추가:
   - CAFE24_MALL_ID
   - CAFE24_CLIENT_ID
   - CAFE24_CLIENT_SECRET

### 5. ❌ **Memory Limit Exceeded (메모리 초과)**

#### 증상
- "Process exited with non-zero exit code: 137"
- 서비스가 갑자기 종료됨

#### 해결 방법
무료 플랜의 메모리 제한(512MB) 최적화:
1. 불필요한 패키지 제거
2. 캐시 크기 제한
3. 데이터 처리 최적화

## 🛠️ 즉시 적용 가능한 수정사항

### 1. 간단한 시작 스크립트 생성
`run_web.py` 파일을 생성하여 경로 문제 해결:

```python
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.web_app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

### 2. 최소 requirements.txt
문제가 있다면 최소 버전으로 시작:

```txt
flask==3.0.0
flask-cors==6.0.1
requests==2.31.0
python-dotenv==1.0.0
```

### 3. 간단한 테스트 앱
문제 파악을 위한 최소 앱 (`test_app.py`):

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "running", "message": "Cafe24 API is ready"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

## 📋 체크리스트

배포 전 확인사항:
- [ ] GitHub 저장소가 public인가?
- [ ] render.yaml 파일이 루트에 있는가?
- [ ] requirements.txt가 유효한가?
- [ ] Python 버전이 3.8 이상인가?
- [ ] 환경 변수가 모두 설정되었는가?

## 🚀 빠른 재배포

문제 수정 후:
```bash
git add .
git commit -m "Fix Render deployment issues"
git push origin master
```

Render는 자동으로 재배포를 시작합니다.

## 💡 디버깅 팁

1. **로그 확인**
   - Logs 탭에서 실시간 로그 확인
   - 에러 메시지 찾기

2. **로컬 테스트**
   ```bash
   pip install -r requirements.txt
   python src/web_app.py
   ```

3. **환경 변수 테스트**
   ```bash
   export CAFE24_MALL_ID=test
   export CAFE24_CLIENT_ID=test
   export CAFE24_CLIENT_SECRET=test
   python src/web_app.py
   ```

## 🆘 추가 지원

- Render 상태: https://status.render.com
- Render 커뮤니티: https://community.render.com
- GitHub Issues: https://github.com/manwonyori/cafe24/issues

---

**특정 에러 메시지를 공유해주시면 더 정확한 해결책을 제시할 수 있습니다!**