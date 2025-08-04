# 🚨 Cafe24 API 403 오류 해결 가이드

## 문제: OAuth 토큰 만료
- **만료일**: 2025-08-02 (이미 만료됨)
- **증상**: 모든 API 호출이 403 Forbidden 반환

## 즉시 해결 방법:

### 1단계: 새 토큰 발급 (5분 소요)

1. **Cafe24 개발자센터 접속**
   - 👉 https://developers.cafe24.com
   - manwonyori 계정으로 로그인

2. **앱 선택**
   - "만원요리 자동화" 또는 해당 앱 클릭

3. **인증 정보 탭**
   - "인증 정보" 또는 "Authentication" 클릭
   - "Access Token 발급" 버튼 클릭

4. **권한 확인**
   다음 권한이 모두 체크되어 있는지 확인:
   - ✅ 상품 조회 (mall.read_product)
   - ✅ 상품 수정 (mall.write_product)
   - ✅ 주문 조회 (mall.read_order)
   - ✅ 주문 수정 (mall.write_order)
   - ✅ 고객 조회 (mall.read_customer)

5. **토큰 발급**
   - "토큰 발급" 클릭
   - 새로운 Access Token과 Refresh Token 복사

### 2단계: 로컬 설정 업데이트

1. **oauth_token.json 파일 수정**
   경로: `C:\Users\8899y\Documents\카페24_프로젝트\01_ACTIVE_PROJECT\config\oauth_token.json`
   
   ```json
   {
     "access_token": "[새 ACCESS TOKEN]",
     "refresh_token": "[새 REFRESH TOKEN]",
     // 나머지는 그대로
   }
   ```

2. **환경변수 파일 생성**
   ```bash
   cd cafe24
   python copy_env_vars.py
   ```

### 3단계: Render 업데이트

1. **Render 환경변수 페이지**
   - 👉 https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env

2. **새 토큰으로 업데이트**
   ```
   CAFE24_ACCESS_TOKEN=[새 ACCESS TOKEN]
   CAFE24_REFRESH_TOKEN=[새 REFRESH TOKEN]
   ```

3. **저장 및 배포**
   - Save Changes 클릭
   - Manual Deploy → Deploy latest commit

### 4단계: 확인 (5분 후)

```bash
# API 테스트
curl https://cafe24-automation.onrender.com/api/products

# 또는 대시보드
https://cafe24-automation.onrender.com/
```

## 자동화 팁:

### GitHub Actions로 자동 동기화
토큰 업데이트 후:
```bash
gh workflow run auto-deploy.yml
```

### 토큰 만료 방지
- Access Token: 2시간 유효
- Refresh Token: 2주 유효
- 자동 갱신 로직이 있지만, Refresh Token도 만료되면 수동 발급 필요

## 문제 지속 시:

1. **앱 권한 재설정**
   - Cafe24 개발자센터에서 앱 권한 다시 확인
   - 필요시 앱 재등록

2. **API 버전 확인**
   - 현재 사용: Cafe24 API v2
   - 최신 버전 확인: https://developers.cafe24.com/docs/api

---
**지금 바로 1단계부터 시작하세요!**