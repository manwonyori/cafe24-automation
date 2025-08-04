# 🚀 Cafe24 OAuth 토큰 자동 교환 시스템

## 시스템 소개
Cafe24 OAuth 인증 과정을 자동화하여 복잡한 토큰 교환 과정을 간소화합니다.

## 🎯 주요 기능

### 1. **oauth_auto_exchange.py** - 완전 자동화 시스템
- 인증 코드 입력 받기
- Access Token + Refresh Token 자동 교환
- 토큰 유효성 검증
- Render 환경변수 업데이트 준비
- Production 모드 전환 완료

### 2. **oauth_one_click_setup.py** - 원클릭 설정
- Cafe24 앱 설정 정보 자동 적용
- 브라우저 자동 열기
- GitHub Actions 자동 배포
- API 연결 테스트

## 📋 사용 방법

### 방법 1: 자동 교환 시스템
```bash
cd cafe24
python oauth_auto_exchange.py
```

1. 브라우저가 자동으로 열립니다
2. Cafe24에 로그인하고 권한을 승인합니다
3. 리다이렉트된 URL을 복사해서 붙여넣습니다
4. 나머지는 자동으로 처리됩니다!

### 방법 2: 원클릭 설정
```bash
cd cafe24
python oauth_one_click_setup.py
```

더 간단한 설정 프로세스를 제공합니다.

## 🔧 설정 정보

### Cafe24 앱 설정
- **App URL**: https://www.manwonyori.com
- **Redirect URI**: https://cafe24-automation.onrender.com/callback
- **Window Type**: 새 창 열기 (900x800px)

### 필요한 권한 (Scope)
- ✅ mall.read_product (상품 조회)
- ✅ mall.write_product (상품 수정)
- ✅ mall.read_order (주문 조회)
- ✅ mall.write_order (주문 수정)
- ✅ mall.read_customer (고객 조회)

## 📁 생성되는 파일

### 1. **auto_exchanged_tokens.txt**
Render 환경변수 업데이트용 파일
```
CAFE24_MALL_ID=manwonyori
CAFE24_CLIENT_ID=9bPpABwHB5mtkCEAfIeuNK
CAFE24_CLIENT_SECRET=qtnWtUk2OZzua1SRa7gN3A
CAFE24_ACCESS_TOKEN=[새 토큰]
CAFE24_REFRESH_TOKEN=[새 토큰]
```

### 2. **oauth_token.json** (업데이트)
로컬 설정 파일 자동 업데이트

## 🚀 Render 배포

### 자동 배포 (GitHub Actions)
시스템이 자동으로:
1. GitHub Secrets 업데이트
2. auto-deploy.yml workflow 실행
3. Render에 자동 배포

### 수동 배포
1. `auto_exchanged_tokens.txt` 또는 `render_env_ready.txt` 내용 복사
2. [Render 환경변수 페이지](https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/env) 접속
3. 환경변수 붙여넣기
4. Save Changes → Manual Deploy

## 📊 확인 방법

### API 테스트
```bash
curl https://cafe24-automation.onrender.com/api/test
```

### 대시보드 접속
https://cafe24-automation.onrender.com/

## ⚠️ 주의사항

1. **토큰 만료 시간**
   - Access Token: 2시간
   - Refresh Token: 2주
   
2. **자동 갱신**
   - API 호출 시 자동으로 토큰 갱신
   - 403 에러 시 자동 refresh

3. **보안**
   - Client Secret은 절대 노출하지 마세요
   - 토큰은 환경변수로만 관리

## 🆘 문제 해결

### "인증 코드를 찾을 수 없습니다"
- 리다이렉트된 전체 URL을 복사했는지 확인
- URL에 `?code=` 파라미터가 있는지 확인

### "토큰 교환 실패"
- Client ID/Secret이 올바른지 확인
- Redirect URI가 정확히 일치하는지 확인
- Cafe24 개발자센터에서 앱 상태 확인

### "API 연결 실패"
- 토큰이 만료되지 않았는지 확인
- 네트워크 연결 상태 확인
- Render 배포가 완료되었는지 확인

## 📞 지원
문제가 지속되면:
1. Cafe24 개발자센터 확인
2. Render 로그 확인
3. GitHub Actions 로그 확인