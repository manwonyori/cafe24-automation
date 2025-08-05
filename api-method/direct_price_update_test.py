#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
직접 가격 수정 테스트
"""
import requests
import json
import sys
import io

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 로컬 서버 URL
base_url = 'http://localhost:5000'

print("=== 직접 가격 수정 테스트 ===\n")

# 1. 로컬 서버에서 제품 검색
print("1. 제품 검색 중...")

# 대시보드 접속
response = requests.get(f'{base_url}/dashboard')
if response.status_code == 200:
    print("✅ 대시보드 접속 성공")

# 마진 대시보드 테스트
response = requests.get(f'{base_url}/margin-dashboard')
if response.status_code == 200:
    print("✅ 마진 대시보드 접속 성공")
    
    # 마진 대시보드의 제품 로드 방식 확인
    print("\n마진 대시보드는 다음과 같이 작동합니다:")
    print("1. 페이지 로드 시 자동으로 제품 목록을 가져옴")
    print("2. 제품명으로 필터링 가능")
    print("3. 개별 제품의 '가격 수정' 버튼 클릭")
    print("4. 새 가격 입력 후 저장")

# 2. 가격 수정 프로세스
print("\n2. 가격 수정 프로세스:")
print("- 마진 대시보드 (http://localhost:5000/margin-dashboard)")
print("- 제품 검색: '점보떡볶이' 입력")
print("- 현재 가격 확인")
print("- '가격 수정' 버튼 클릭")
print("- 13,500원 입력")
print("- 저장")

# 3. 엑셀 업로드 방식
print("\n3. 엑셀 업로드 방식:")
print("- 생성된 엑셀 파일 수정")
print("- 실제 product_no 입력")
print("- 대시보드에서 업로드")

print("\n💡 권장사항:")
print("- 브라우저에서 마진 대시보드 사용이 가장 직관적")
print("- http://localhost:5000/margin-dashboard 접속")
print("- 제품 검색 후 직접 수정")