#!/bin/bash

# Render 수동 배포 트리거 스크립트
# Service ID: srv-d27vit95pdvs7381g3eg

echo "🚀 Render 수동 배포 시작..."

# Render API를 통한 수동 배포 트리거
# 참고: Deploy Hook URL이 필요합니다. Render 대시보드에서 확인하세요.
# https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/settings

# Deploy Hook 사용 예시:
# curl -X POST "https://api.render.com/deploy/srv-d27vit95pdvs7381g3eg?key=YOUR_DEPLOY_HOOK_KEY"

echo "📌 Deploy Hook 설정 방법:"
echo "1. Render 대시보드 접속: https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg/settings"
echo "2. Settings > Deploy Hooks 섹션 이동"
echo "3. 'Generate Deploy Hook' 클릭"
echo "4. 생성된 URL을 복사하여 아래 명령어 사용:"
echo ""
echo "curl -X POST \"YOUR_DEPLOY_HOOK_URL\""
echo ""
echo "또는 Render 대시보드에서 직접 배포:"
echo "https://dashboard.render.com/web/srv-d27vit95pdvs7381g3eg"