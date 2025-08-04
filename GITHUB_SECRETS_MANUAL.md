# GitHub Secrets 수동 설정 가이드

## 📋 복사할 시크릿 값들

아래 내용을 그대로 복사해서 사용하세요:

### 1. CAFE24_MALL_ID
```
manwonyori
```

### 2. CAFE24_CLIENT_ID
```
9bPpABwHB5mtkCEAfIeuNK
```

### 3. CAFE24_CLIENT_SECRET
```
qtnWtUk2OZzua1SRa7gN3A
```

### 4. CAFE24_ACCESS_TOKEN
```
sRPbNFyOBdNts1UI7EerpB
```

### 5. CAFE24_REFRESH_TOKEN
```
KU6XvhF5H9Ypf6NsIfZPeK
```

## 🔧 GitHub에서 설정하기

1. **GitHub 저장소 접속**
   - https://github.com/manwonyori/cafe24

2. **Settings 탭 클릭**
   - 저장소 상단 메뉴에서 Settings

3. **Secrets and variables → Actions**
   - 왼쪽 사이드바에서 선택

4. **New repository secret 클릭**
   - 각 시크릿마다 반복:
   
   **Name**: CAFE24_MALL_ID  
   **Value**: manwonyori
   
   **Name**: CAFE24_CLIENT_ID  
   **Value**: 9bPpABwHB5mtkCEAfIeuNK
   
   **Name**: CAFE24_CLIENT_SECRET  
   **Value**: qtnWtUk2OZzua1SRa7gN3A
   
   **Name**: CAFE24_ACCESS_TOKEN  
   **Value**: sRPbNFyOBdNts1UI7EerpB
   
   **Name**: CAFE24_REFRESH_TOKEN  
   **Value**: KU6XvhF5H9Ypf6NsIfZPeK

5. **Render 관련 시크릿 (선택사항)**

   Render API 자동화를 원하면 추가:
   
   **Name**: RENDER_API_KEY  
   **Value**: [Render Account Settings에서 생성]
   
   **Name**: RENDER_DEPLOY_HOOK_URL  
   **Value**: [Render Service Settings에서 복사]

## ✅ 설정 확인

모든 시크릿 설정 후:

1. Actions 탭으로 이동
2. "Cafe24 Auto Deploy to Render" 워크플로우 선택
3. "Run workflow" 버튼 클릭
4. 자동 배포 시작!

## 🚀 자동 배포 확인

푸시할 때마다 자동으로:
- GitHub Secrets에서 API 키 읽기
- Render에 환경변수 동기화
- Production 모드로 자동 전환
- 배포 완료!

---
생성일: 2025-08-04