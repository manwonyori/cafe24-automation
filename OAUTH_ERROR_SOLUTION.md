# 🚨 Cafe24 OAuth Client ID 오류 해결

## 문제
```
API 인증에 실패하였습니다.
파라메터 client_id를 추가해주세요.
```

## 해결 방법

### 방법 1: 개발자센터에서 직접 토큰 발급 (권장) ✅

가장 쉽고 빠른 방법입니다:

```bash
cd cafe24
python get_token_from_dev_center.py
```

1. 브라우저가 열리면 Cafe24 개발자센터 로그인
2. "내 앱" → "만원요리 자동화" 클릭
3. "인증 정보" 탭 클릭
4. 하단의 "테스트 Access Token" 섹션
5. "토큰 발급" 버튼 클릭
6. 모든 권한 체크 → "생성"
7. 생성된 토큰을 스크립트에 입력

### 방법 2: 올바른 OAuth URL 사용

정확한 URL (인코딩 완료):
```
https://manwonyori.cafe24api.com/api/v2/oauth/authorize?response_type=code&client_id=9bPpABwHB5mtkCEAfIeuNK&redirect_uri=https%3A%2F%2Fcafe24-automation.onrender.com%2Fcallback&scope=mall.read_product%2Cmall.write_product%2Cmall.read_order%2Cmall.write_order%2Cmall.read_customer&state=test123
```

### 방법 3: Cafe24 앱 설정 확인

1. https://developers.cafe24.com 접속
2. 앱 설정에서 확인:
   - Client ID: `9bPpABwHB5mtkCEAfIeuNK`
   - Redirect URI: `https://cafe24-automation.onrender.com/callback`
   - 상태: 활성화

## 🔧 즉시 해결 스크립트

```bash
# 개발자센터 방법 (가장 쉬움)
python get_token_from_dev_center.py
```

이 스크립트는:
- 개발자센터를 자동으로 엽니다
- 단계별 안내를 제공합니다
- 토큰을 자동으로 저장합니다
- Render 배포를 준비합니다

## 📝 수동 토큰 입력

이미 토큰이 있다면 `token_template.json` 파일을 수정:

```json
{
  "mall_id": "manwonyori",
  "client_id": "9bPpABwHB5mtkCEAfIeuNK",
  "client_secret": "qtnWtUk2OZzua1SRa7gN3A",
  "access_token": "여기에_토큰_입력",
  "refresh_token": "여기에_리프레시_토큰_입력"
}
```

## ✅ 확인 사항

1. **Client ID가 올바른가?**
   - 현재: `9bPpABwHB5mtkCEAfIeuNK`

2. **Redirect URI가 일치하는가?**
   - 설정된 URI: `https://cafe24-automation.onrender.com/callback`

3. **앱이 활성화되어 있는가?**
   - Cafe24 개발자센터에서 확인

## 🚀 다음 단계

토큰을 받은 후:
1. `dev_center_tokens.txt` 파일 내용 복사
2. Render 환경변수 업데이트
3. 배포 및 테스트

## 🆘 여전히 안 되면

1. Cafe24 고객센터 문의
2. 앱 재등록 고려
3. 다른 브라우저 시도