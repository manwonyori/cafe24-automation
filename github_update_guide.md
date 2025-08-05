# GitHub 업데이트 가이드

## 가격 수정 후 GitHub 반영 절차

### 1. 변경된 파일 확인
```bash
cd cafe24
git status
```

### 2. 변경사항 추가
```bash
# 모든 변경사항 추가
git add .

# 또는 특정 파일만
git add oauth_token.json
git add [변경된 파일명]
```

### 3. 커밋
```bash
git commit -m "Update product price: [인생]점보떡볶이1490g to 13,500원"
```

### 4. GitHub에 푸시
```bash
git push origin master
```

### 5. Render 자동 배포
- GitHub 푸시 후 Render가 자동으로 재배포
- 약 2-3분 소요
- https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg 에서 확인

## 주의사항
- 가격 수정은 Cafe24 API를 통해 실시간 반영됨
- 데이터베이스나 설정 파일이 변경되었을 수 있으므로 확인 필요
- 토큰 파일이 변경되었다면 함께 커밋