# 🚀 Render API 키 즉시 설정 가이드

## 1️⃣ Render 대시보드 바로가기
👉 **https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env**

## 2️⃣ 환경 변수 복사 & 붙여넣기

아래 내용을 **정확히** 복사해서 Render에 추가하세요:

### 필수 환경 변수 (5개)

| Key | Value |
|-----|-------|
| **CAFE24_MALL_ID** | `manwonyori` |
| **CAFE24_CLIENT_ID** | `9bPpABwHB5mtkCEAfIeuNK` |
| **CAFE24_CLIENT_SECRET** | `qtnWtUk2OZzua1SRa7gN3A` |
| **CAFE24_ACCESS_TOKEN** | `sRPbNFyOBdNts1UI7EerpB` |
| **CAFE24_REFRESH_TOKEN** | `KU6XvhF5H9Ypf6NsIfZPeK` |

## 3️⃣ 설정 방법 (1분 소요)

1. **위 링크 클릭** → Render 로그인
2. **Environment** 탭 확인
3. **Add Environment Variable** 클릭
4. 위 표의 Key와 Value 입력 (5개 모두)
5. **Save Changes** 클릭

## 4️⃣ 확인 (5분 후)

### 🔗 시스템 상태 확인
https://cafe24-automation.onrender.com/

**변경 전:**
```json
"mode": "demo"
```

**변경 후:**
```json
"mode": "production"
```

## 5️⃣ 바로 테스트

### 실제 상품 조회
```
https://cafe24-automation.onrender.com/api/products
```

### 자연어 명령 (Postman/curl)
```bash
curl -X POST https://cafe24-automation.onrender.com/api/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "상품 목록 보여줘"}'
```

## ⚠️ 주의사항
- 환경 변수는 **대소문자 구분**
- 값에 따옴표 넣지 않기
- Save Changes 후 5분 대기

---
**문제 발생 시**: 환경 변수 스크린샷 찍어서 확인