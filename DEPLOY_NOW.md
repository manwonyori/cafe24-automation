# 🚀 CAFE24 자동화 시스템 배포 가이드

## 📋 환경변수 (복사해서 Render에 붙여넣기)

```
CAFE24_MALL_ID=manwonyori
CAFE24_CLIENT_ID=9bPpABwHB5mtkCEAfIeuNK
CAFE24_CLIENT_SECRET=qtnWtUk2OZzua1SRa7gN3A
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN=lCr5kG66DtLsmTaorPedtH
CAFE24_REFRESH_TOKEN=KIOmihlDK9roYKGWOo8vAA
ENABLE_AUTO_REFRESH=true
ENABLE_DASHBOARD=true
ENABLE_API_ENDPOINTS=true
PRODUCTION_MODE=true
LOG_LEVEL=INFO
```

## 🔧 배포 단계

### 1단계: Render 대시보드 접속
👉 https://dashboard.render.com/

1. 로그인
2. "cafe24-automation" 서비스 찾기
3. "Environment" 탭 클릭

### 2단계: 환경변수 업데이트
1. 기존 환경변수 모두 삭제
2. 위의 환경변수 전체 복사
3. 붙여넣기
4. "Save Changes" 클릭

### 3단계: 배포
1. "Manual Deploy" 클릭
2. "Deploy latest commit" 선택
3. 배포 진행 상황 확인 (약 5분)

### 4단계: 확인
배포 완료 후 접속:
- 대시보드: https://cafe24-automation.onrender.com/
- API 상태: https://cafe24-automation.onrender.com/api/test

## ✅ 시스템 기능

### 대시보드 기능
- 실시간 주문 모니터링
- 상품 재고 관리
- 고객 정보 조회
- 매출 통계
- 자연어 명령 처리

### API 엔드포인트
- GET /api/products - 상품 목록
- GET /api/orders - 주문 목록
- GET /api/customers - 고객 목록
- GET /api/test - API 테스트

### 자동 기능
- 토큰 자동 갱신 (2시간마다)
- 403 오류 시 자동 재시도
- 실시간 데이터 동기화

## ⚠️ 주의사항
- Access Token은 2시간 유효 (자동 갱신됨)
- Refresh Token은 2주 유효
- 첫 배포 후 5분 정도 기다려주세요

## 🆘 문제 해결
1. 403 오류: 토큰이 자동으로 갱신됩니다
2. 연결 오류: Render 로그 확인
3. 대시보드 오류: 브라우저 캐시 삭제

---
**지금 바로 Render에 배포하세요!**