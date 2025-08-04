# Cafe24 테스트 쇼핑몰 정보

## 쇼핑몰 정보
- **테스트 쇼핑몰 URL**: https://manwonyori.cafe24.com
- **Mall ID**: manwonyori
- **앱 URL**: https://www.manwonyori.com
- **Redirect URI**: https://cafe24-automation.onrender.com/callback

## ✅ 설정 확인 사항

### 1. Redirect URI
```
https://cafe24-automation.onrender.com/callback
```
**정확합니다!** 이 URI로 OAuth 인증 후 리다이렉트됩니다.

### 2. 테스트 쇼핑몰
```
manwonyori.cafe24.com
```
**정확합니다!** 테스트 쇼핑몰이 올바르게 설정되어 있습니다.

## 🧪 테스트 실행 방법

### 빠른 테스트
```bash
cd cafe24
python quick_test_oauth.py
```

### OAuth 인증 플로우
1. 브라우저가 자동으로 열립니다
2. Cafe24 관리자로 로그인
3. 권한 승인
4. 리다이렉트된 URL 복사
5. `oauth_auto_exchange.py` 실행

## 📋 권한 (Scope)
테스트 시 다음 권한을 모두 사용할 수 있습니다:
- ✅ mall.read_product (상품 조회)
- ✅ mall.write_product (상품 수정)  
- ✅ mall.read_order (주문 조회)
- ✅ mall.write_order (주문 수정)
- ✅ mall.read_customer (고객 조회)

## 🔍 테스트 쇼핑몰 특징
- **무료 테스트**: 앱 가격과 무관하게 테스트 가능
- **모든 권한 사용**: 제한 없이 모든 API 테스트 가능
- **샘플 데이터**: 테스트용 상품, 주문 데이터 제공
- **별도 생성 가능**: 기존 샘플 쇼핑몰이 있어도 추가 생성 가능

## 🚀 실제 운영 전환 시
1. 실제 쇼핑몰 Mall ID로 변경
2. 앱 승인 및 결제 진행
3. Production 환경 변수 업데이트

## ⚠️ 주의사항
- 테스트 쇼핑몰 데이터는 실제 쇼핑몰에 영향 없음
- OAuth 토큰은 2시간마다 갱신 필요
- Refresh Token은 2주간 유효