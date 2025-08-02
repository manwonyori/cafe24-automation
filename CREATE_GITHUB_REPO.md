# GitHub 저장소 생성 및 업로드 가이드

## 🚀 빠른 실행 (복사해서 실행)

### 1단계: GitHub에서 저장소 생성
1. https://github.com/new 접속
2. Repository name: `cafe24`
3. Description: `카페24 쇼핑몰 완전 자동화 시스템 - 한국어 자연어 명령으로 쇼핑몰 관리`
4. Public 선택
5. **Create repository** 클릭 (README 추가하지 않음)

### 2단계: 로컬에서 GitHub에 푸시

```bash
cd C:\Users\8899y\Documents\cafe24

# 원격 저장소 추가 (YOUR_USERNAME을 실제 GitHub 사용자명으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/cafe24.git

# 브랜치 이름을 main으로 변경
git branch -M main

# GitHub에 푸시
git push -u origin main
```

### 3단계: GitHub 설정

저장소 페이지에서:

1. **Settings** → **Pages**
   - Source: Deploy from a branch
   - Branch: main
   - Folder: /docs
   - Save

2. **About** (우측 상단 톱니바퀴)
   - Website: `https://YOUR_USERNAME.github.io/cafe24`
   - Topics: `cafe24`, `e-commerce`, `automation`, `korean`, `api`

## 📋 전체 명령어 (한 번에 실행)

```bash
# PowerShell에서 실행
cd C:\Users\8899y\Documents\cafe24

# Git 사용자 정보 확인 (필요시 설정)
git config user.name
git config user.email

# 원격 저장소 추가 및 푸시
$username = Read-Host "GitHub 사용자명을 입력하세요"
git remote add origin "https://github.com/$username/cafe24.git"
git branch -M main
git push -u origin main

Write-Host "✅ GitHub 업로드 완료!"
Write-Host "🌐 저장소 URL: https://github.com/$username/cafe24"
```

## 🔧 문제 해결

### 인증 오류 발생 시
```bash
# GitHub Personal Access Token 사용
# 1. https://github.com/settings/tokens 접속
# 2. Generate new token (classic)
# 3. repo 권한 체크
# 4. 토큰 복사

# 푸시할 때 비밀번호 대신 토큰 사용
git push -u origin main
# Username: YOUR_USERNAME
# Password: YOUR_TOKEN
```

### 이미 origin이 있다고 나올 때
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/cafe24.git
```

## ✅ 완료 확인

1. https://github.com/YOUR_USERNAME/cafe24 접속
2. 모든 파일이 업로드되었는지 확인
3. README.md가 잘 표시되는지 확인
4. GitHub Pages가 활성화되었는지 확인

## 🎯 다음 단계

1. **배포 버튼 테스트**
   - README.md의 Deploy 버튼 클릭
   - Render.com에서 배포 진행

2. **릴리스 생성**
   - Releases → Create a new release
   - Tag: v2.0.0
   - Title: 카페24 자동화 시스템 v2.0.0

3. **문서 사이트 확인**
   - https://YOUR_USERNAME.github.io/cafe24