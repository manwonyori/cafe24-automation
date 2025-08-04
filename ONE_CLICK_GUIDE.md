# 🚀 만원요리 최씨남매 Cafe24 원클릭 배포 가이드

## 🎯 원클릭 자동 배포

### 방법 1: 완전 자동화 (추천)
```bash
cd cafe24
python one_click_deploy.py
```

이 명령 하나로:
- ✅ GitHub CLI 자동 설치
- ✅ GitHub 자동 인증
- ✅ API 키 자동 추출 및 GitHub Secrets 설정
- ✅ 배포 워크플로우 자동 실행
- ✅ Production 모드 전환 확인
- ✅ API 테스트 자동 실행

### 방법 2: 실시간 모니터링
```bash
# 심플 버전 (추천)
python simple_sync_monitor.py

# 고급 버전 (rich UI)
python sync_monitor.py
```

모니터링 기능:
- 📊 실시간 동기화 상태 표시
- 🔄 자동 재시도 (실패 시)
- 📈 배포 진행상황 추적
- ⚡ 5분마다 자동 동기화

## 📋 수동 설정 (필요시)

### GitHub Secrets 설정
1. https://github.com/manwonyori/cafe24/settings/secrets/actions
2. 다음 시크릿 추가:

```
CAFE24_MALL_ID=manwonyori
CAFE24_CLIENT_ID=9bPpABwHB5mtkCEAfIeuNK
CAFE24_CLIENT_SECRET=qtnWtUk2OZzua1SRa7gN3A
CAFE24_ACCESS_TOKEN=sRPbNFyOBdNts1UI7EerpB
CAFE24_REFRESH_TOKEN=KU6XvhF5H9Ypf6NsIfZPeK
```

### Render 추가 설정 (선택)
```
RENDER_API_KEY=[Render API Key]
RENDER_DEPLOY_HOOK_URL=[Deploy Hook URL]
```

## 🔍 동작 확인

### 1. 배포 상태
```bash
# GitHub Actions 확인
gh run list

# 또는 브라우저
https://github.com/manwonyori/cafe24/actions
```

### 2. Production 모드 확인
```bash
curl https://cafe24-automation.onrender.com/
```

응답:
```json
{
  "mode": "production",  // ✅ 성공!
  "status": "online"
}
```

### 3. 대시보드 접속
https://cafe24-automation.onrender.com/

## 🛠️ 트러블슈팅

### "GitHub CLI not found"
```bash
# Windows
winget install --id GitHub.cli

# Mac
brew install gh

# 수동 설치
https://cli.github.com/
```

### "Not authenticated"
```bash
gh auth login
```

### "Still in demo mode"
1. GitHub Secrets 확인
2. 5분 대기 (Render 배포 시간)
3. 모니터링 스크립트 실행

## 📊 시스템 구조

```
one_click_deploy.py
    ├── 설정 파일 자동 탐색
    ├── GitHub CLI 설치/인증
    ├── Secrets 자동 생성
    ├── 워크플로우 트리거
    └── 배포 검증

sync_monitor.py
    ├── 실시간 상태 모니터링
    ├── 자동 재시도 로직
    ├── 에러 추적 및 복구
    └── 시각적 대시보드
```

## 🎉 완료!

이제 코드 변경 시:
```bash
git push
```

자동으로:
- GitHub Actions 실행
- API 키 동기화
- Render 재배포
- Production 모드 활성화

**진정한 원클릭 배포가 실현되었습니다!** 🚀

---
생성일: 2025-01-17
버전: 3.0 (Complete Automation)