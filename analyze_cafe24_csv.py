#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 공식 CSV 템플릿 분석
"""
import pandas as pd
import json

# CSV 파일 읽기
csv_path = "static/excel_templates/manwonyori_20250805_201_f879_producr_template.csv"
df = pd.read_csv(csv_path, encoding='utf-8-sig')

print("=" * 80)
print("Cafe24 공식 상품 템플릿 분석")
print("=" * 80)

# 기본 정보
print(f"\n1. 기본 정보:")
print(f"   - 전체 컬럼 수: {len(df.columns)}")
print(f"   - 전체 상품 수: {len(df)}")

# 주요 필드 분석
print(f"\n2. 핵심 필드 (처음 20개):")
for i, col in enumerate(df.columns[:20]):
    print(f"   {i+1:2}. {col}")

# 상품 데이터 샘플
print(f"\n3. 첫 번째 상품 데이터 (주요 필드):")
if len(df) > 0:
    first_product = df.iloc[0]
    key_fields = [
        '상품코드', '상품명', '진열상태', '판매상태',
        '소비자가', '공급가', '상품가', '판매가',
        '재고수량', '브랜드', '제조사', '공급사'
    ]
    
    for field in key_fields:
        if field in df.columns:
            value = first_product[field]
            print(f"   - {field}: {value}")

# 가격 관련 필드 분석
print(f"\n4. 가격 관련 필드 분석:")
price_fields = [col for col in df.columns if '가' in col or '금' in col or 'price' in col.lower()]
for field in price_fields[:10]:  # 최대 10개만
    print(f"   - {field}")

# 상태 필드 분석
print(f"\n5. 상태 관련 필드:")
status_fields = ['진열상태', '판매상태', '과세구분', '옵션사용']
for field in status_fields:
    if field in df.columns:
        unique_values = df[field].unique()
        print(f"   - {field}: {unique_values[:5]}")  # 최대 5개 값만

# 옵션 관련 필드
print(f"\n6. 옵션/변형 관련 필드:")
option_fields = [col for col in df.columns if '옵션' in col]
for field in option_fields[:5]:
    print(f"   - {field}")

# 이미지 관련 필드
print(f"\n7. 이미지 관련 필드:")
image_fields = [col for col in df.columns if '이미지' in col]
for field in image_fields:
    print(f"   - {field}")

# API 매핑 제안
print(f"\n8. API 필드 매핑 제안:")
mapping = {
    '상품코드': 'product_code',
    '자체 상품코드': 'custom_product_code',
    '상품명': 'product_name',
    '영문 상품명': 'product_name_en',
    '진열상태': 'display (Y/N)',
    '판매상태': 'selling (Y/N)',
    '판매가': 'price',
    '공급가': 'supply_price',
    '소비자가': 'retail_price',
    '재고수량': 'quantity',
    '브랜드': 'brand_code',
    '제조사': 'manufacturer_code',
    '공급사': 'supplier_code'
}

for csv_field, api_field in mapping.items():
    if csv_field in df.columns:
        print(f"   - {csv_field} → {api_field}")

# 결과 저장
result = {
    'total_columns': len(df.columns),
    'total_products': len(df),
    'columns': list(df.columns),
    'key_mappings': mapping
}

with open('cafe24_csv_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n분석 완료! 상세 결과는 cafe24_csv_analysis.json 파일 참조")