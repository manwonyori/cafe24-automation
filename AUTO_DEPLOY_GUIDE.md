# 🚀 Cafe24 완전 자동 배포 가이드

## 개요

GitHub Actions를 통해 코드 푸시만으로 Cafe24 API 키가 자동으로 Render에 적용되는 완전 자동화 시스템입니다.

## 🔧 초기 설정 (1회만)

### 1. GitHub CLI 설치

**Windows:**
```bash
winget install --id GitHub.cli
```

**Mac:**
```bash
brew install gh
```

### 2. GitHub 인증
```bash
gh auth login
```

### 3. GitHub Secrets 자동 설정
```bash
cd cafe24
python setup_github_secrets.py
```

이 스크립트가 자동으로:
- Cafe24 API 키를 GitHub Secrets에 암호화 저장
- Render API 키 설정
- Deploy Hook URL 설정

### 4. 수동 설정 (선택사항)

GitHub CLI가 없는 경우:

1. https://github.com/[your-username]/cafe24/settings/secrets/actions 접속
2. "New repository secret" 클릭
3. 다음 시크릿 추가:

```
CAFE24_MALL_ID = manwonyori
CAFE24_CLIENT_ID = 9bPpABwHB5mtkCEAfIeuNK
CAFE24_CLIENT_SECRET = qtnWtUk2OZzua1SRa7gN3A
CAFE24_ACCESS_TOKEN = sRPbNFyOBdNts1UI7EerpB
CAFE24_REFRESH_TOKEN = KU6XvhF5H9Ypf6NsIfZPeK
RENDER_API_KEY = [Render API Key]
RENDER_DEPLOY_HOOK_URL = [Render Deploy Hook URL]
```

## 🎯 자동 배포 프로세스

### 코드 푸시 시 자동 실행:

```bash
git add .
git commit -m "Update feature"
git push
```

### 자동으로 수행되는 작업:

1. **GitHub Secrets에서 API 키 읽기** (암호화됨)
2. **Render 환경변수 자동 동기화**
3. **Render 서비스 자동 재배포**
4. **Production 모드 전환 확인**
5. **API 엔드포인트 자동 테스트**
6. **결과 리포트 생성**

### 수동 트리거:

```bash
gh workflow run auto-deploy.yml
```

또는 GitHub Actions 탭에서 "Run workflow" 클릭

## 📊 배포 모니터링

### GitHub Actions에서 확인:
1. https://github.com/[your-username]/cafe24/actions
2. 최신 워크플로우 클릭
3. 실시간 로그 확인

### 배포 단계:
- **Sync Secrets** ✅ - API 키 동기화
- **Test Deployment** ✅ - 자동 테스트
- **Notify** ✅ - 결과 알림

## 🔍 트러블슈팅

### "Render API Key not found"
```bash
# Render API Key 생성
1. https://dashboard.render.com
2. Account Settings → API Keys
3. Create API Key
4. GitHub Secret에 추가
```

### "Deployment failed"
```bash
# 로그 확인
gh run view

# 재시도
gh workflow run auto-deploy.yml
```

### "Still in demo mode"
- GitHub Secrets 확인
- Render 로그 확인
- 5분 대기 후 재확인

## 🎉 장점

1. **완전 자동화**: 코드 푸시만으로 배포
2. **보안**: API 키가 암호화되어 저장
3. **검증**: 자동 테스트로 배포 확인
4. **롤백**: 문제 시 이전 버전으로 자동 복구

## 📝 워크플로우 구조

```yaml
on:
  push:           # 코드 푸시 시
    branches: [master, main]
  workflow_dispatch:  # 수동 실행

jobs:
  sync-secrets:   # API 키 동기화
  test-deployment: # 배포 테스트
  notify:         # 결과 알림
```

## 🚦 상태 확인

배포 후 확인:
```bash
curl https://cafe24-automation.onrender.com/
```

Production 모드 확인:
```json
{
  "mode": "production",  // ✅ 성공!
  "status": "online"
}
```

---

이제 코드를 푸시하면 자동으로 Production 모드로 배포됩니다! 🎊