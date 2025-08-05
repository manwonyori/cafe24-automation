#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 문제 진단 - Render 로그 확인 필요
"""

print("=" * 80)
print("REAL PROBLEM DIAGNOSIS")
print("=" * 80)

print("\n환경변수를 여러 번 변경했는데도 500 오류가 계속된다면:")
print("\n1. 환경변수는 문제가 아닙니다")
print("2. 실제 문제는 코드나 모듈 import 오류일 가능성이 높습니다")

print("\n[즉시 확인해야 할 것]")
print("\n1. Render 대시보드에서 Logs 탭 확인:")
print("   - https://dashboard.render.com/")
print("   - 서비스 선택 → Logs 탭")
print("   - 최근 로그에서 Python 오류 메시지 찾기")

print("\n2. 예상되는 오류:")
print("   - ModuleNotFoundError: No module named 'oauth_manager'")
print("   - KeyError: 'CAFE24_ACCESS_TOKEN'")
print("   - ImportError: cannot import name 'Cafe24APIClient'")
print("   - TypeError in API routes")

print("\n3. GitHub 레포지토리 확인:")
print("   - https://github.com/manwonyori/cafe24")
print("   - src 폴더에 필요한 파일들이 있는지 확인:")
print("     - src/oauth_manager.py")
print("     - src/api_client.py")
print("     - src/demo_mode.py")

print("\n[해결 방법]")
print("\n만약 ModuleNotFoundError가 있다면:")
print("1. GitHub에 필요한 파일이 없을 수 있습니다")
print("2. 파일을 GitHub에 push해야 합니다")

print("\n만약 KeyError가 있다면:")
print("1. 환경변수 이름이 잘못되었을 수 있습니다")
print("2. 하지만 이미 여러 번 확인했으므로 가능성 낮음")

print("\n[즉시 실행할 명령]")
print("\nRender Logs에서 찾은 오류 메시지를 알려주세요.")
print("정확한 오류 메시지를 보면 바로 해결할 수 있습니다!")

# GitHub 파일 체크 스크립트
github_check = """
# GitHub 레포지토리 파일 확인 명령:

cd cafe24
git status
git ls-files | grep -E "(oauth_manager|api_client|demo_mode)"

# 만약 파일이 없다면:
git add src/oauth_manager.py src/api_client.py src/demo_mode.py
git commit -m "Add missing API files"
git push
"""

with open("CHECK_GITHUB_FILES.txt", "w") as f:
    f.write(github_check)

print("\n생성된 파일:")
print("- CHECK_GITHUB_FILES.txt (GitHub 파일 확인 명령)")

print("\n" + "=" * 80)
print("Render Logs를 확인하고 정확한 오류 메시지를 알려주세요!")
print("=" * 80)