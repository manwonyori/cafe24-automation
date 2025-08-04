# Render 환경변수 즉시 설정 가이드

## 🚀 빠른 설정 (5분 소요)

### 1단계: 환경변수 복사
아래 내용을 **전체 복사**하세요:

```
CAFE24_MALL_ID=manwonyori
CAFE24_CLIENT_ID=9bPpABwHB5mtkCEAfIeuNK
CAFE24_CLIENT_SECRET=qtnWtUk2OZzua1SRa7gN3A
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN=sRPbNFyOBdNts1UI7EerpB
CAFE24_REFRESH_TOKEN=KU6XvhF5H9Ypf6NsIfZPeK
```

### 2단계: Render 대시보드 접속
1. https://dashboard.render.com 로그인
2. Services 탭에서 `cafe24-automation` 클릭

### 3단계: 환경변수 설정
1. **Environment** 탭 클릭
2. 환경변수 입력 필드에 위에서 복사한 내용을 **붙여넣기**
3. **Save Changes** 버튼 클릭 (우측 상단의 보라색 버튼)

### 4단계: 재배포
1. **Manual Deploy** 버튼 클릭 (우측 상단)
2. **Deploy latest commit** 선택
3. 배포 시작 확인 (2-5분 소요)

### 5단계: Production 모드 확인
배포 완료 후 브라우저로 접속:
https://cafe24-automation.onrender.com/

대시보드 상단에 **"시스템 모드: production"** 표시 확인

## ✅ 설정 완료 후 확인사항

### API로 확인
```bash
curl https://cafe24-automation.onrender.com/
```

응답:
```json
{
  "mode": "production",  // ← 이것이 표시되면 성공!
  "status": "online"
}
```

### 브라우저로 확인
1. https://cafe24-automation.onrender.com/ 접속
2. 대시보드에서 실제 데이터 표시 확인
3. 자연어 명령 테스트: "상품 목록 보여줘"

## 🔍 문제 해결

### "여전히 Demo 모드입니다"
1. Environment 탭에서 환경변수가 모두 입력되었는지 확인
2. Save Changes를 클릭했는지 확인
3. Manual Deploy를 실행했는지 확인
4. 5분 정도 기다린 후 재확인

### "503 Service Unavailable"
- 정상입니다! 배포 중이므로 5분 정도 기다려주세요
- https://dashboard.render.com 에서 배포 진행상황 확인 가능

### "토큰이 만료되었습니다"
- 시스템이 자동으로 토큰을 갱신합니다
- 문제가 지속되면 새 토큰 발급 필요

## 🎯 자동화 스크립트 사용

Python이 설치되어 있다면:
```bash
cd cafe24
python copy_env_vars.py
```

이 명령으로 `render_env_vars.txt` 파일이 생성되며, 
이 파일의 내용을 복사해서 사용할 수도 있습니다.

## 📱 모바일에서 설정하기

1. Render 모바일 웹 접속 (앱 불필요)
2. 로그인 후 cafe24-automation 서비스 선택
3. Environment 탭에서 환경변수 입력
4. Save Changes → Deploy

## 🎉 완료!

환경변수 설정이 완료되면:
- **Demo Mode** → **Production Mode** 전환
- 실제 Cafe24 쇼핑몰 데이터 연동
- 모든 API 기능 활성화

---
생성일: 2025-08-04
자동 생성 도구: `python copy_env_vars.py`