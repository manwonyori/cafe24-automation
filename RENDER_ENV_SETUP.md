# Render 환경 변수 설정 가이드

## 🔐 필수 환경 변수

Render 대시보드에서 다음 환경 변수를 설정해야 합니다:

### 1. 카페24 API 기본 정보
```
CAFE24_MALL_ID = [실제 몰 ID]  # 예: myshop
CAFE24_CLIENT_ID = [앱 클라이언트 ID]  # 카페24 앱에서 발급
CAFE24_CLIENT_SECRET = [앱 시크릿 키]  # 카페24 앱에서 발급
```

### 2. OAuth 토큰 (선택사항)
```
CAFE24_ACCESS_TOKEN = [액세스 토큰]  # OAuth 인증 후 발급
CAFE24_REFRESH_TOKEN = [리프레시 토큰]  # OAuth 인증 후 발급
```

## 📋 카페24 API 정보 확인 방법

1. **카페24 어드민 접속**
   - https://[몰ID].cafe24.com/admin 로그인

2. **앱스토어 → 개발자센터**
   - 상단 메뉴에서 "앱스토어" 클릭
   - "개발자센터" 선택

3. **앱 생성 또는 확인**
   - "앱 만들기" 또는 기존 앱 선택
   - API 권한 설정:
     - ✅ 상품 읽기/쓰기
     - ✅ 주문 읽기/쓰기
     - ✅ 고객 읽기
     - ✅ 재고 읽기/쓰기

4. **API 정보 복사**
   - Client ID 복사
   - Client Secret 복사
   - Mall ID는 카페24 도메인의 서브도메인 부분

## 🚀 Render에서 환경 변수 설정

1. **Render 대시보드 접속**
   - https://dashboard.render.com

2. **서비스 선택**
   - cafe24-automation 서비스 클릭

3. **Environment 탭**
   - "Environment" 탭 클릭
   - "Add Environment Variable" 클릭

4. **변수 추가**
   ```
   Key: CAFE24_MALL_ID
   Value: [실제 몰 ID]
   
   Key: CAFE24_CLIENT_ID  
   Value: [실제 클라이언트 ID]
   
   Key: CAFE24_CLIENT_SECRET
   Value: [실제 시크릿 키]
   ```

5. **Save Changes**
   - 모든 변수 입력 후 "Save Changes" 클릭
   - 서비스가 자동으로 재시작됩니다

## 🎭 데모 모드

환경 변수가 설정되지 않으면 자동으로 데모 모드로 작동합니다:
- 실제 API 호출 없이 샘플 데이터 반환
- 기능 테스트 및 데모용
- 실제 운영 시에는 반드시 API 정보 설정 필요

## ✅ 설정 확인

환경 변수 설정 후:
1. https://[your-app].onrender.com/health 접속
2. "system_initialized": true 확인
3. https://[your-app].onrender.com/api/products 테스트

## ⚠️ 주의사항

- Client Secret은 절대 공개하지 마세요
- 환경 변수는 암호화되어 저장됩니다
- 변경 시 서비스가 자동 재시작됩니다