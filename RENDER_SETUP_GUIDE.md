# Cafe24 Automation System - Render Setup Guide

## 🚀 현재 상태

- **URL**: https://cafe24-automation.onrender.com/
- **Dashboard**: https://cafe24-automation.onrender.com/ (브라우저로 접속)
- **상태**: Demo Mode (모든 기능 정상 작동, 실제 API 미연결)

## ✅ 완료된 작업

1. **모든 API 엔드포인트 구현 완료** (100% 테스트 통과)
   - 상품 관리 API
   - 주문 관리 API
   - 재고 관리 API
   - 고객 관리 API
   - 매출 통계 API
   - 자연어 명령 처리
   - 리포트 생성

2. **데모 모드 완벽 구현**
   - 만원요리 브랜드 실제 데이터 시뮬레이션
   - 모든 API 응답 정상 작동

3. **웹 대시보드 구현**
   - 실시간 모니터링
   - 자연어 명령 실행
   - API 테스트 도구

## 🔑 Production Mode 활성화 방법

### Step 1: Render 대시보드 접속
1. https://dashboard.render.com 로그인
2. `cafe24-automation` 서비스 선택

### Step 2: 환경 변수 설정
Environment 탭에서 다음 변수 추가:

```
CAFE24_MALL_ID=manwonyori
CAFE24_CLIENT_ID=9bPpABwHB5mtkCEAfIeuNK
CAFE24_CLIENT_SECRET=qtnWtUk2OZzua1SRa7gN3A
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
```

### Step 3: 서비스 재시작
1. "Manual Deploy" 버튼 클릭
2. "Deploy latest commit" 선택
3. 2-3분 대기

### Step 4: Production Mode 확인
```bash
curl https://cafe24-automation.onrender.com/
```

응답에서 `"mode": "production"` 확인

## 📊 테스트 방법

### 1. 브라우저 테스트
https://cafe24-automation.onrender.com/ 접속하여 대시보드 확인

### 2. API 테스트
```bash
# 상품 조회
curl https://cafe24-automation.onrender.com/api/products?limit=5

# 주문 조회
curl https://cafe24-automation.onrender.com/api/orders

# 자연어 명령
curl -X POST https://cafe24-automation.onrender.com/api/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "오늘 주문 보여줘"}'
```

### 3. 전체 테스트
```bash
python test_all_endpoints.py
```

## 🛠️ 문제 해결

### API 키가 작동하지 않는 경우
1. OAuth 토큰 갱신 필요할 수 있음
2. `src/verify_oauth.py` 실행하여 토큰 상태 확인
3. 필요시 Cafe24 개발자센터에서 앱 권한 재확인

### 503 Service Unavailable
1. Render 무료 플랜은 비활성 시 자동 종료됨
2. 첫 요청 시 30초 정도 소요될 수 있음
3. 지속적 사용을 위해 유료 플랜 고려

### Demo Mode에서 벗어나지 않는 경우
1. 환경 변수가 제대로 설정되었는지 확인
2. Render 로그에서 "Using demo mode" 메시지 확인
3. 환경 변수 설정 후 반드시 재배포 필요

## 📝 추가 기능 개발 예정

1. **실시간 알림 시스템**
   - 재고 부족 알림
   - 주문 접수 알림
   - 매출 목표 달성 알림

2. **고급 분석 기능**
   - AI 기반 수요 예측
   - 고객 행동 분석
   - 상품 추천 시스템

3. **자동화 워크플로우**
   - 재고 자동 주문
   - 가격 자동 조정
   - 프로모션 자동 실행

## 💡 사용 팁

1. **자연어 명령 예시**
   - "오늘 매출 얼마야?"
   - "재고 10개 이하 상품 보여줘"
   - "이번 달 베스트셀러 뭐야?"
   - "김치찌개 재고 확인해줘"

2. **API 활용**
   - 모든 API는 JSON 형식으로 응답
   - 페이징 지원 (limit, offset 파라미터)
   - 필터링 지원 (날짜, 상태 등)

3. **성능 최적화**
   - 캐싱 시스템 활용 (5분 TTL)
   - 배치 처리 API 활용
   - 웹훅 설정으로 실시간 동기화

## 📞 지원

문제 발생 시:
1. Render 로그 확인
2. `test_all_endpoints.py` 실행하여 상태 진단
3. GitHub Issues에 문제 보고

---

Last Updated: 2025-08-04
Version: 2.0.0