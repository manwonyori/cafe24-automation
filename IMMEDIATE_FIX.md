# 🚨 즉시 Production 모드 전환 (2분 소요)

## 문제: 
API 키는 모두 있지만 Render에 설정되지 않음

## 해결:

### 옵션 1: 복사-붙여넣기 (가장 빠름)

1. **아래 내용 전체 복사:**
```
CAFE24_MALL_ID=manwonyori
CAFE24_CLIENT_ID=9bPpABwHB5mtkCEAfIeuNK
CAFE24_CLIENT_SECRET=qtnWtUk2OZzua1SRa7gN3A
CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback
CAFE24_ACCESS_TOKEN=sRPbNFyOBdNts1UI7EerpB
CAFE24_REFRESH_TOKEN=KU6XvhF5H9Ypf6NsIfZPeK
```

2. **Render 대시보드 열기:**
   - https://dashboard.render.com
   - cafe24-automation 서비스 클릭
   - Environment 탭 클릭

3. **붙여넣기 후 Save Changes**

4. **Manual Deploy → Deploy latest commit**

5. **5분 후 확인:**
   - https://cafe24-automation.onrender.com/
   - "mode": "production" 확인

### 옵션 2: GitHub Actions 트리거

GitHub Secrets가 이미 설정되어 있다면:

```bash
cd cafe24
gh workflow run auto-deploy.yml
```

또는:
- https://github.com/manwonyori/cafe24/actions
- "Run workflow" 클릭

## 왜 자동으로 안 되었나?

1. **Render API Key 부재**: Render를 프로그래밍으로 제어하려면 API Key 필요
2. **웹 인터페이스 제한**: Claude Code는 브라우저를 조작할 수 없음
3. **첫 설정은 수동**: 보안상 첫 API Key 설정은 수동으로 해야 함

## 한 번만 설정하면:
- 이후 모든 업데이트는 자동화
- git push만으로 배포 완료
- API 키 변경도 자동 동기화

---
**지금 바로 옵션 1을 실행하세요!**