#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 API 형식에 정확히 맞춘 엑셀 템플릿 생성
"""
import pandas as pd
import os

# 템플릿 디렉토리
template_dir = 'static/excel_templates'

# Cafe24 API 필드 매핑
# 1. 상품 등록 템플릿 (POST /api/v2/admin/products)
product_create_data = {
    # 필수 필드
    'product_name': ['[인생] 상품명 예시', '[부산] 상품명 예시', '[최씨남매] 상품명 예시'],
    'price': [10000, 20000, 15000],  # 판매가 (필수)
    'display': ['T', 'T', 'F'],  # 진열상태 (필수) T/F
    'selling': ['T', 'T', 'T'],  # 판매상태 (필수) T/F
    
    # 선택 필드 (자주 사용)
    'product_code': ['P001', 'P002', 'P003'],  # 상품코드
    'custom_product_code': ['CUST001', 'CUST002', 'CUST003'],  # 자체상품코드
    'model_name': ['MODEL001', 'MODEL002', 'MODEL003'],  # 모델명
    'supply_price': [8000, 16000, 12000],  # 공급가
    'retail_price': [12000, 24000, 18000],  # 소비자가
    'summary_description': ['상품 요약 설명', '상품 요약 설명', '상품 요약 설명'],  # 상품 요약설명
    'quantity': [100, 50, 200],  # 재고수량
    'weight': ['500', '1000', '300'],  # 상품중량(g)
    'brand_code': ['B000000A', 'B000000B', 'B000000C'],  # 브랜드코드
    'manufacturer_code': ['M000000A', 'M000000B', 'M000000C'],  # 제조사코드
    'supplier_code': ['S000000A', 'S000000B', 'S000000C'],  # 공급사코드
    'made_in_code': ['KR', 'KR', 'CN'],  # 원산지코드
    'tax_type': ['A', 'A', 'A'],  # 세금타입 (A:과세, B:면세, C:영세)
    'use_naverpay': ['T', 'T', 'F'],  # 네이버페이 사용여부
    'product_tag': ['인생,프리미엄', '부산,특산품', '최씨남매,인기'],  # 상품태그
    'shipping_fee_by_product': ['T', 'F', 'F'],  # 개별배송비 사용여부
    'shipping_fee_type': ['T', 'T', 'T']  # 배송비타입 (T:배송비무료, R:고정배송비 등)
}

# 2. 상품 수정 템플릿 (PUT /api/v2/admin/products/{product_no})
product_update_data = {
    'product_no': ['상품번호 필수', '', ''],  # 필수
    'product_name': ['수정할 상품명', '', ''],
    'price': ['수정할 가격', '', ''],
    'display': ['T 또는 F', '', ''],
    'selling': ['T 또는 F', '', ''],
    'quantity': ['수정할 재고', '', ''],
    'supply_price': ['수정할 공급가', '', ''],
    'summary_description': ['수정할 설명', '', ''],
    'product_tag': ['수정할 태그', '', '']
}

# 3. 재고 수정 템플릿 (PUT /api/v2/admin/products/{product_no}/variants/quantity)
inventory_update_data = {
    'product_no': ['1234', '5678', '9012'],  # 상품번호 (필수)
    'variant_code': ['', '', ''],  # 품목코드 (옵션상품인 경우)
    'quantity': [150, 30, 250],  # 변경할 재고수량 (필수)
    'safety_quantity': [10, 5, 20],  # 안전재고
    'use_inventory': ['T', 'T', 'T']  # 재고관리 사용여부
}

# 4. 가격 일괄 수정 템플릿
price_update_data = {
    'product_no': ['1234', '5678', '9012'],  # 상품번호 (필수)
    'price': [12000, 18000, 15000],  # 판매가 (필수)
    'retail_price': [15000, 22000, 18000],  # 소비자가
    'supply_price': [9000, 14000, 12000],  # 공급가
    'price_content': ['가격 인상', '프로모션 할인', '정상가'],  # 가격설명
    'price_update_date': ['2024-01-20', '2024-01-20', '2024-01-20']  # 가격수정일
}

# 엑셀 파일 생성
def create_cafe24_templates():
    # 1. 상품 등록 템플릿
    with pd.ExcelWriter(os.path.join(template_dir, 'cafe24_product_create.xlsx'), engine='openpyxl') as writer:
        df = pd.DataFrame(product_create_data)
        df.to_excel(writer, sheet_name='상품등록', index=False)
        
        # API 필드 설명
        field_desc = pd.DataFrame({
            'API필드명': ['product_name', 'price', 'display', 'selling', 'product_code', 'quantity', 'brand_code'],
            '한글명': ['상품명', '판매가', '진열상태', '판매상태', '상품코드', '재고수량', '브랜드코드'],
            '필수여부': ['필수', '필수', '필수', '필수', '선택', '선택', '선택'],
            '형식': ['문자열', '숫자', 'T/F', 'T/F', '문자열', '숫자', '문자열'],
            '설명': [
                '[카테고리] 형식 권장',
                '숫자만 입력',
                'T:진열, F:미진열',
                'T:판매중, F:판매안함',
                '중복 불가',
                '0 이상의 정수',
                'Cafe24 브랜드코드'
            ]
        })
        field_desc.to_excel(writer, sheet_name='필드설명', index=False)
    
    # 2. 상품 수정 템플릿
    with pd.ExcelWriter(os.path.join(template_dir, 'cafe24_product_update.xlsx'), engine='openpyxl') as writer:
        df = pd.DataFrame(product_update_data)
        df.to_excel(writer, sheet_name='상품수정', index=False)
    
    # 3. 재고 수정 템플릿
    with pd.ExcelWriter(os.path.join(template_dir, 'cafe24_inventory_update.xlsx'), engine='openpyxl') as writer:
        df = pd.DataFrame(inventory_update_data)
        df.to_excel(writer, sheet_name='재고수정', index=False)
    
    # 4. 가격 수정 템플릿
    with pd.ExcelWriter(os.path.join(template_dir, 'cafe24_price_update.xlsx'), engine='openpyxl') as writer:
        df = pd.DataFrame(price_update_data)
        df.to_excel(writer, sheet_name='가격수정', index=False)
    
    print("Cafe24 API 형식 템플릿 생성 완료!")
    print(f"위치: {os.path.abspath(template_dir)}")
    print("\n생성된 파일:")
    print("- cafe24_product_create.xlsx (상품 등록)")
    print("- cafe24_product_update.xlsx (상품 수정)")
    print("- cafe24_inventory_update.xlsx (재고 수정)")
    print("- cafe24_price_update.xlsx (가격 수정)")

if __name__ == "__main__":
    create_cafe24_templates()