# GitHub 저장소 설정 가이드

## 1. GitHub에서 새 저장소 생성

1. [GitHub.com](https://github.com) 로그인
2. 우측 상단 '+' → 'New repository' 클릭
3. 다음 정보 입력:
   - **Repository name**: `cafe24`
   - **Description**: `카페24 쇼핑몰 완전 자동화 시스템 - 한국어 자연어 명령으로 쇼핑몰 관리`
   - **Public** 선택
   - **Add a README** 체크 해제 (이미 있음)
   - **Add .gitignore** 체크 해제 (이미 있음)
   - **Choose a license**: MIT License

## 2. 로컬 저장소를 GitHub에 연결

```bash
cd C:\Users\8899y\Documents\cafe24

# GitHub 원격 저장소 추가
git remote add origin https://github.com/YOUR_USERNAME/cafe24.git

# 기존 커밋 푸시
git push -u origin master
```

## 3. GitHub 저장소 설정

### Settings → General
- **Default branch**: master
- **Features**: 
  - ✅ Issues
  - ✅ Projects
  - ✅ Wiki

### Settings → Pages
1. **Source**: Deploy from a branch
2. **Branch**: master
3. **Folder**: /docs
4. Save

### Settings → Secrets and variables → Actions
다음 시크릿 추가:
- `DOCKER_USERNAME`: Docker Hub 사용자명
- `DOCKER_PASSWORD`: Docker Hub 비밀번호
- `PRODUCTION_HOST`: 프로덕션 서버 IP
- `PRODUCTION_USER`: 프로덕션 서버 사용자
- `PRODUCTION_SSH_KEY`: 프로덕션 서버 SSH 키
- `SLACK_WEBHOOK`: Slack 알림 웹훅 (선택사항)

## 4. 배포 버튼 URL 업데이트

README.md에서 다음 부분을 실제 GitHub 사용자명으로 변경:

```markdown
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/cafe24)

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/YOUR_USERNAME/cafe24)

[![Deploy to Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/YOUR_USERNAME/cafe24)
```

## 5. 첫 릴리스 생성

1. GitHub 저장소 페이지에서 **Releases** 클릭
2. **Create a new release** 클릭
3. 태그 생성: `v2.0.0`
4. 릴리스 제목: `v2.0.0 - Complete Automation System`
5. 릴리스 노트:

```markdown
## 🎉 카페24 쇼핑몰 완전 자동화 시스템 v2.0.0

### ✨ 주요 기능
- 한국어 자연어 명령 처리
- 완전 자동화된 상품/주문/재고 관리
- 고성능 캐싱 시스템
- Docker 지원
- 원클릭 클라우드 배포

### 🚀 빠른 시작
- Render.com 배포: Deploy 버튼 클릭
- Docker: `docker-compose up -d`
- Python: `pip install -r requirements.txt && python src/main.py`

### 📚 문서
- [설치 가이드](https://YOUR_USERNAME.github.io/cafe24)
- [API 문서](https://YOUR_USERNAME.github.io/cafe24/API)
```

## 6. 프로젝트 토픽 추가

Settings → 상단의 톱니바퀴 아이콘 → Topics:
- `cafe24`
- `e-commerce`
- `automation`
- `korean`
- `api`
- `python`
- `docker`

## 7. 완료 체크리스트

- [ ] GitHub 저장소 생성
- [ ] 로컬 저장소 연결 및 푸시
- [ ] GitHub Pages 활성화
- [ ] 시크릿 설정
- [ ] README.md URL 업데이트
- [ ] 첫 릴리스 생성
- [ ] 프로젝트 토픽 추가

## 🎯 다음 단계

1. **Render.com 배포**: Deploy 버튼 클릭
2. **Docker Hub 자동 빌드**: GitHub 연동
3. **모니터링 설정**: Uptime Robot 등
4. **커뮤니티 구축**: 이슈 템플릿, 기여 가이드