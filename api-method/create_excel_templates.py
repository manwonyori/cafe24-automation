#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
엑셀 템플릿 생성 스크립트
"""
import pandas as pd
import os

# 템플릿 디렉토리
template_dir = 'excel_templates'

# 1. 상품 일괄 등록 템플릿
product_upload_data = {
    '상품코드*': ['예시: P001', 'P002', 'P003'],
    '상품명*': ['[인생] 상품명 예시', '[부산] 상품명 예시', '[최씨남매] 상품명 예시'],
    '판매가*': [10000, 20000, 15000],
    '공급가': [8000, 16000, 12000],
    '재고수량': [100, 50, 200],
    '진열상태': ['T', 'T', 'F'],
    '카테고리': ['식품', '생활', '음료'],
    '브랜드코드': ['B001', 'B002', 'B003'],
    '상품설명': ['상품 설명 입력', '상품 설명 입력', '상품 설명 입력'],
    '중량(g)': [500, 1000, 300],
    '제조사': ['제조사명', '제조사명', '제조사명'],
    '원산지': ['국내산', '국내산', '수입산']
}

# 2. 상품 일괄 수정 템플릿
product_update_data = {
    '상품번호*': ['상품번호 입력', '', ''],
    '상품코드': ['변경할 경우만 입력', '', ''],
    '상품명': ['변경할 경우만 입력', '', ''],
    '판매가': ['변경할 경우만 입력', '', ''],
    '재고수량': ['변경할 경우만 입력', '', ''],
    '진열상태': ['T 또는 F', '', ''],
    '비고': ['수정 사유 입력', '', '']
}

# 3. 재고 일괄 업데이트 템플릿
inventory_update_data = {
    '상품코드*': ['P001', 'P002', 'P003'],
    '현재재고': [100, 50, 200],
    '변경재고*': [150, 30, 250],
    '변경사유': ['입고', '판매', '입고'],
    '메모': ['2024-01-15 입고분', '온라인 판매', '2024-01-15 입고분']
}

# 4. 가격 일괄 수정 템플릿
price_update_data = {
    '상품코드*': ['P001', 'P002', 'P003'],
    '현재가격': [10000, 20000, 15000],
    '변경가격*': [12000, 18000, 15000],
    '할인율(%)': [0, 10, 0],
    '변경일자': ['2024-01-20', '2024-01-20', '2024-01-20'],
    '변경사유': ['원가 상승', '프로모션', '유지']
}

# 엑셀 파일 생성
def create_templates():
    # 1. 상품 일괄 등록
    with pd.ExcelWriter(os.path.join(template_dir, 'product_upload_template.xlsx'), engine='openpyxl') as writer:
        df = pd.DataFrame(product_upload_data)
        df.to_excel(writer, sheet_name='상품등록', index=False)
        
        # 설명 시트 추가
        instructions = pd.DataFrame({
            '항목': ['상품코드', '상품명', '판매가', '진열상태'],
            '설명': [
                '고유한 상품 코드 (중복 불가)',
                '[카테고리] 형식으로 시작하는 상품명',
                '숫자만 입력 (콤마 제외)',
                'T: 진열, F: 미진열'
            ],
            '필수여부': ['필수', '필수', '필수', '선택']
        })
        instructions.to_excel(writer, sheet_name='설명', index=False)
    
    # 2. 상품 일괄 수정
    with pd.ExcelWriter(os.path.join(template_dir, 'product_update_template.xlsx'), engine='openpyxl') as writer:
        df = pd.DataFrame(product_update_data)
        df.to_excel(writer, sheet_name='상품수정', index=False)
    
    # 3. 재고 업데이트
    with pd.ExcelWriter(os.path.join(template_dir, 'inventory_update_template.xlsx'), engine='openpyxl') as writer:
        df = pd.DataFrame(inventory_update_data)
        df.to_excel(writer, sheet_name='재고수정', index=False)
    
    # 4. 가격 수정
    with pd.ExcelWriter(os.path.join(template_dir, 'price_update_template.xlsx'), engine='openpyxl') as writer:
        df = pd.DataFrame(price_update_data)
        df.to_excel(writer, sheet_name='가격수정', index=False)
    
    print("템플릿 생성 완료!")
    print(f"위치: {os.path.abspath(template_dir)}")

if __name__ == "__main__":
    create_templates()