#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[인생]점보떡볶이1490g 가격 수정 - 엑셀 방식
"""
import pandas as pd
import requests
import json
from datetime import datetime
import sys
import io

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=== [인생]점보떡볶이1490g 가격 수정 작업 ===\n")

# 1. 엑셀 템플릿 생성
print("1. 가격 수정용 엑셀 템플릿 생성 중...")

# 템플릿 데이터 - Cafe24 API 형식에 맞춤
data = {
    'product_no': ['P000000X'],  # 실제 상품번호로 변경 필요
    'product_code': ['JUMBO1490'],  # 실제 상품코드
    'product_name': ['[인생]점보떡볶이1490g'],
    'price': [13500],  # 새 판매가
    'supply_price': [10000],  # 공급가 (예시)
    'custom_product_code': [''],
    'display': ['T'],
    'selling': ['T'],
    'summary_description': [''],
    'simple_description': [''],
    'product_tag': [''],
    'use_naverpay': ['T'],
    'naverpay_type': ['C']
}

# DataFrame 생성
df = pd.DataFrame(data)

# 엑셀 파일로 저장
filename = f'price_update_jumbo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
filepath = f'static/excel_templates/{filename}'

# 폴더가 없으면 생성
import os
os.makedirs('static/excel_templates', exist_ok=True)

# 엑셀 파일 저장
with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Products', index=False)
    
    # 워크시트 가져오기
    worksheet = writer.sheets['Products']
    
    # 헤더 스타일 설정
    from openpyxl.styles import Font, PatternFill, Alignment
    
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    # 헤더에 스타일 적용
    for cell in worksheet[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
    
    # 열 너비 자동 조정
    for column in worksheet.columns:
        max_length = 0
        column = [cell for cell in column]
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

print(f"✅ 엑셀 파일 생성 완료: {filepath}")

# 2. 가격 수정 시뮬레이션
print("\n2. 가격 변경 시뮬레이션:")
print(f"- 제품명: [인생]점보떡볶이1490g")
print(f"- 현재 가격: (API에서 조회 필요)")
print(f"- 변경 가격: 13,500원")
print(f"- 공급가: 10,000원 (예시)")
print(f"- 예상 마진율: {((13500 - 10000) / 13500 * 100):.1f}%")

# 3. 업로드 가이드
print("\n3. 엑셀 업로드 방법:")
print("- 방법 1: 대시보드에서 '가격 일괄 수정' 메뉴 사용")
print("- 방법 2: API 엔드포인트 /api/upload/price 사용")
print("- 방법 3: 마진 대시보드에서 직접 수정")

# 4. 실제 상품번호 확인 필요
print("\n⚠️ 주의사항:")
print("- 실제 상품번호(product_no) 확인 필요")
print("- Cafe24 관리자에서 상품번호 확인 후 엑셀 수정")
print("- 업로드 전 백업 권장")

print(f"\n📁 생성된 파일 위치: {os.path.abspath(filepath)}")