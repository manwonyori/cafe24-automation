# Render.com 배포 가이드

## 🚀 빠른 배포 (3분 소요)

### 방법 1: 원클릭 배포 (권장) ✨

1. **배포 버튼 클릭**
   - 아래 버튼을 클릭하여 Render.com으로 이동:
   - https://render.com/deploy?repo=https://github.com/manwonyori/cafe24

2. **GitHub 연동**
   - "Connect GitHub account" 클릭
   - GitHub 계정으로 로그인
   - manwonyori/cafe24 저장소 접근 권한 허용

3. **서비스 이름 설정**
   - Service Name: `cafe24-automation` (또는 원하는 이름)
   - Region: Singapore (아시아 지역 권장)

4. **환경 변수 입력**
   - 다음 정보를 입력하세요:
   ```
   CAFE24_MALL_ID: your_mall_id
   CAFE24_CLIENT_ID: your_client_id  
   CAFE24_CLIENT_SECRET: your_secret
   ```

5. **Create Web Service 클릭**
   - 배포가 자동으로 시작됩니다
   - 약 2-3분 후 서비스가 활성화됩니다

### 방법 2: 수동 배포

1. **Render.com 가입/로그인**
   - https://render.com 접속
   - GitHub으로 로그인 (권장)

2. **New → Web Service**
   - Dashboard에서 "New +" 버튼 클릭
   - "Web Service" 선택

3. **GitHub 저장소 연결**
   - "Connect a GitHub repository" 선택
   - `manwonyori/cafe24` 검색 및 선택
   - "Connect" 클릭

4. **서비스 설정**
   ```
   Name: cafe24-automation
   Region: Singapore
   Branch: master
   Root Directory: (비워둠)
   Build Command: pip install -r requirements.txt
   Start Command: python src/web_app.py
   ```

5. **환경 변수 추가**
   - "Environment" 섹션에서 다음 추가:
   ```
   CAFE24_MALL_ID = your_mall_id
   CAFE24_CLIENT_ID = your_client_id
   CAFE24_CLIENT_SECRET = your_secret
   CAFE24_API_VERSION = 2025-06-01
   CAFE24_CACHE_ENABLED = true
   CAFE24_LOG_LEVEL = INFO
   ```

6. **Create Web Service 클릭**

## 📊 배포 확인

### 1. 빌드 로그 확인
- Dashboard → 서비스 클릭
- "Logs" 탭에서 빌드 진행 상황 확인
- 성공 메시지: "Build successful"

### 2. 서비스 상태 확인
- Status: "Live" 표시 확인
- URL 클릭하여 접속: https://cafe24-automation.onrender.com

### 3. 헬스체크
```bash
curl https://cafe24-automation.onrender.com/health
```

예상 응답:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2024-03-15T10:30:00Z"
}
```

## 🔧 문제 해결

### 빌드 실패 시
1. Python 버전 확인 (3.8+ 필요)
2. requirements.txt 파일 확인
3. 환경 변수 형식 확인

### 서비스 시작 실패 시
1. 환경 변수 누락 확인
2. 로그에서 에러 메시지 확인
3. PORT 환경 변수 자동 설정됨 (수정 불필요)

### 느린 응답 시
- 무료 플랜: 15분 비활성 후 절전 모드
- 첫 요청 시 10-30초 지연 정상
- 유료 플랜으로 업그레이드 시 24/7 활성

## 🎯 배포 후 테스트

### API 엔드포인트 테스트
```bash
# 상품 목록 조회
curl https://your-app.onrender.com/api/products

# 자연어 명령 실행
curl -X POST https://your-app.onrender.com/api/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "오늘 주문 확인"}'
```

### 웹 인터페이스
- 브라우저에서 https://your-app.onrender.com 접속
- API 문서 및 상태 확인

## 🔄 자동 배포 설정

1. **Auto-Deploy 활성화**
   - Settings → Build & Deploy
   - "Auto-Deploy" 켜기
   - master 브랜치에 push 시 자동 재배포

2. **배포 알림**
   - Settings → Notifications
   - 이메일/Slack 알림 설정

## 💡 추가 기능

### Redis 캐시 활성화
- render.yaml에 이미 설정됨
- 무료 Redis 인스턴스 자동 생성
- 성능 10배 향상

### 커스텀 도메인
1. Settings → Custom Domains
2. 도메인 추가 (예: api.manwonyori.com)
3. DNS CNAME 레코드 설정

## 📞 지원

- Render 상태: https://status.render.com
- 문서: https://render.com/docs
- 지원: support@render.com

---

**🎉 축하합니다! 카페24 자동화 시스템이 클라우드에 배포되었습니다!**