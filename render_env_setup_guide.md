# Render 환경변수 설정 가이드

## 🚨 현재 문제
- 토큰이 유효하지 않음 (is_valid: False)
- 제품 목록이 비어있음 (0개)
- GitHub 푸시 후에도 토큰이 반영되지 않음

## 🛠️ 해결 방법: Render 환경변수 직접 설정

### 1. Render 대시보드 접속
- https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env
- 또는 Render 대시보드 > Environment 탭

### 2. 환경변수 추가/수정

다음 변수들을 추가하거나 업데이트:

```
CAFE24_ACCESS_TOKEN = yhep7daQIqcUnu3pBhsyBB
CAFE24_REFRESH_TOKEN = Y39VGzKtMxYnXZMr0yLjfF
CAFE24_CLIENT_ID = 9bPpABwHB5mtkCEAfIeuNK
CAFE24_CLIENT_SECRET = qtnWtUk2OZzua1SRa7gN3A
CAFE24_MALL_ID = manwonyori
```

### 3. 저장 및 재시작
1. "Save Changes" 클릭
2. 서비스가 자동으로 재시작됨 (1-2분 소요)

### 4. 확인
재시작 후:
- https://cafe24-automation.onrender.com/api/debug/token
- is_valid가 true로 변경되었는지 확인

## 📌 중요 사항
- 환경변수는 파일보다 우선순위가 높음
- 토큰은 2시간마다 자동 갱신됨
- 한 번 설정하면 계속 유지됨

## 🎯 설정 후 테스트
1. https://cafe24-automation.onrender.com/margin-dashboard 접속
2. 제품 목록이 로드되는지 확인
3. [인생]점보떡볶이1490g 검색
4. 가격 13,500원으로 수정