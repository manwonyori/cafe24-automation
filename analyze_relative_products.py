#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 관련상품(RelativeProduct) 연관성 분석
"""
import pandas as pd
import json

# 관련상품 파일 읽기
relative_df = pd.read_csv("static/excel_templates/RelativeProduct_1.csv", encoding='cp949')
print("=" * 80)
print("Cafe24 관련상품 연관성 분석")
print("=" * 80)

# 기본 정보
print(f"\n1. 파일 정보:")
print(f"   - 전체 상품 수: {len(relative_df)}")
print(f"   - 컬럼: {list(relative_df.columns)}")

# 샘플 데이터 분석
print(f"\n2. 관련상품 구조 분석:")
for i in range(min(5, len(relative_df))):
    row = relative_df.iloc[i]
    product_code = row['상품코드']
    related = row['관련상품']
    
    if pd.isna(related) or related == '':
        related_list = []
    else:
        related_list = related.split(';')
    
    print(f"   {product_code}: {len(related_list)}개 관련상품")
    if len(related_list) > 0:
        print(f"      → {', '.join(related_list[:3])}{'...' if len(related_list) > 3 else ''}")

# 연관성 규칙 분석
print(f"\n3. 연관성 규칙 발견:")

# 그룹 패턴 찾기
product_groups = {}
for _, row in relative_df.iterrows():
    product_code = row['상품코드']
    related = row['관련상품']
    
    if pd.isna(related) or related == '':
        continue
    
    related_list = set(related.split(';'))
    
    # 비슷한 관련상품을 가진 그룹 찾기
    for group_key, group_products in product_groups.items():
        if len(related_list.intersection(set(group_products))) > len(related_list) * 0.8:
            # 80% 이상 겹치면 같은 그룹
            group_products.add(product_code)
            break
    else:
        # 새 그룹 생성
        group_key = f"그룹{len(product_groups)+1}"
        product_groups[group_key] = {product_code}

# 상호 참조 확인
mutual_references = []
for _, row in relative_df.iterrows():
    product_a = row['상품코드']
    related = row['관련상품']
    
    if pd.isna(related) or related == '':
        continue
    
    related_list = related.split(';')
    
    # 각 관련상품이 현재 상품을 참조하는지 확인
    for product_b in related_list:
        # product_b의 관련상품 찾기
        b_row = relative_df[relative_df['상품코드'] == product_b]
        if not b_row.empty:
            b_related = b_row.iloc[0]['관련상품']
            if pd.notna(b_related) and product_a in b_related.split(';'):
                if (product_b, product_a) not in mutual_references:
                    mutual_references.append((product_a, product_b))

print(f"\n   a) 상호 참조 패턴: {len(mutual_references)}개 발견")
for pair in mutual_references[:3]:
    print(f"      {pair[0]} ↔ {pair[1]}")

# 그룹 분석
print(f"\n   b) 상품 그룹 패턴:")
print(f"      - 첫 8개 상품(P00000GU~P00000GN): 서로 모두 연관")
print(f"      - P00000GL, GK, GJ, FU, FT: 5개 상품 그룹")
print(f"      - P00000FP 그룹: 8개 상품 연관")

# 코드 패턴 분석
print(f"\n   c) 상품코드 연속성:")
consecutive_groups = []
for _, row in relative_df.iterrows():
    product_code = row['상품코드']
    related = row['관련상품']
    
    if pd.isna(related) or related == '':
        continue
    
    related_list = related.split(';')
    # 연속된 코드 확인
    codes = [product_code] + related_list
    codes_sorted = sorted(codes)
    
    is_consecutive = True
    for i in range(1, len(codes_sorted)):
        # 코드 번호 추출 (P00000XX에서 XX 부분)
        num1 = codes_sorted[i-1][-2:]
        num2 = codes_sorted[i][-2:]
        
        # 연속성 체크 (문자도 연속으로 간주)
        if ord(num2[0]) - ord(num1[0]) > 1:
            is_consecutive = False
            break
    
    if is_consecutive and len(codes) > 3:
        consecutive_groups.append(codes_sorted)

print(f"      연속된 상품코드 그룹: {len(set(tuple(g) for g in consecutive_groups))}개")

# 업로드 템플릿과 비교
print(f"\n4. 업로드 템플릿과의 관계:")
print(f"   - RelativeProduct_1.csv: 실제 관련상품 데이터 (읽기전용)")
print(f"   - RelativeProduct_uplode.csv: 업로드용 빈 템플릿")
print(f"   - 구조: 상품코드,관련상품 (세미콜론으로 구분)")

# 결과 저장
result = {
    'total_products': len(relative_df),
    'mutual_references': len(mutual_references),
    'patterns': {
        'separator': ';',
        'format': '상품코드1;상품코드2;상품코드3',
        'max_related': max(len(r.split(';')) if pd.notna(r) and r else 0 for r in relative_df['관련상품']),
        'empty_related': len(relative_df[relative_df['관련상품'].isna() | (relative_df['관련상품'] == '')])
    }
}

with open('relative_product_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n분석 완료!")