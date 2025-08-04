#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
가격 수정용 엑셀 파일 생성
"""
import pandas as pd
import requests
import json
from datetime import datetime
import os

def create_price_update_excel():
    """마진율 기준 가격 수정용 엑셀 파일 생성"""
    
    # 토큰 읽기
    with open('oauth_token.json', 'r', encoding='utf-8') as f:
        token_data = json.load(f)
    
    # API 호출로 현재 상품 정보 가져오기
    headers = {
        'Authorization': f'Bearer {token_data["access_token"]}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': '2025-06-01'
    }
    
    mall_id = token_data['mall_id']
    url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
    params = {
        'limit': 100,
        'fields': 'product_no,product_name,price,supply_price,retail_price,product_code'
    }
    
    print("상품 정보를 가져오는 중...")
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"상품 정보 조회 실패: {response.status_code}")
        return
    
    products = response.json().get('products', [])
    
    # 엑셀 데이터 준비
    excel_data = []
    
    for product in products:
        product_no = product.get('product_no')
        product_name = product.get('product_name', '')
        current_price = float(product.get('price', 0))
        supply_price = float(product.get('supply_price', 0))
        retail_price = float(product.get('retail_price', 0))
        product_code = product.get('product_code', '')
        
        # 현재 마진율 계산
        current_margin = 0
        if supply_price > 0:
            current_margin = ((current_price - supply_price) / supply_price) * 100
        
        # 목표 마진율별 가격 계산 (예시)
        target_20_price = int(supply_price * 1.20) if supply_price > 0 else current_price
        target_25_price = int(supply_price * 1.25) if supply_price > 0 else current_price
        target_30_price = int(supply_price * 1.30) if supply_price > 0 else current_price
        
        excel_data.append({
            'product_no': product_no,
            'product_code': product_code,
            'product_name': product_name,
            'current_price': int(current_price),
            'supply_price': int(supply_price),
            'current_margin_rate': round(current_margin, 2),
            'new_price': int(current_price),  # 사용자가 수정할 칸
            'target_margin_rate': '',  # 사용자가 입력할 칸
            'price_20_margin': target_20_price,
            'price_25_margin': target_25_price,
            'price_30_margin': target_30_price,
            'memo': ''
        })
    
    # 데이터프레임 생성
    df = pd.DataFrame(excel_data)
    
    # static 디렉토리 확인/생성
    static_dir = os.path.join('static', 'excel_templates')
    os.makedirs(static_dir, exist_ok=True)
    
    # 엑셀 파일 생성
    filename = f'price_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    filepath = os.path.join(static_dir, filename)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # 메인 시트: 가격 수정 데이터
        df.to_excel(writer, sheet_name='가격수정', index=False)
        
        # 설명 시트
        instructions = pd.DataFrame({
            '컬럼명': ['product_no', 'new_price', 'target_margin_rate', 'price_20_margin', 'price_25_margin', 'price_30_margin'],
            '설명': [
                '상품번호 (수정하지 말 것)',
                '새로운 판매가 (이 값을 수정하세요)',
                '목표 마진율 (참고용)',
                '20% 마진 기준 가격 (참고용)',
                '25% 마진 기준 가격 (참고용)',
                '30% 마진 기준 가격 (참고용)'
            ],
            '사용법': [
                '변경 금지',
                '원하는 가격 입력',
                '목표 마진율 입력 (선택)',
                '참고용 - 수정하지 말 것',
                '참고용 - 수정하지 말 것',
                '참고용 - 수정하지 말 것'
            ]
        })
        instructions.to_excel(writer, sheet_name='사용법', index=False)
        
        # 마진율 계산 가이드
        margin_guide = pd.DataFrame({
            '마진율': ['10%', '15%', '20%', '25%', '30%', '35%', '40%'],
            '계산공식': [
                '공급가 × 1.10',
                '공급가 × 1.15', 
                '공급가 × 1.20',
                '공급가 × 1.25',
                '공급가 × 1.30',
                '공급가 × 1.35',
                '공급가 × 1.40'
            ],
            '예시(공급가 10,000원)': [11000, 11500, 12000, 12500, 13000, 13500, 14000]
        })
        margin_guide.to_excel(writer, sheet_name='마진율가이드', index=False)
    
    print(f"✓ 가격 수정용 엑셀 파일 생성 완료!")
    print(f"파일 위치: {filepath}")
    print(f"총 {len(excel_data)}개 상품 포함")
    print(f"\n사용법:")
    print(f"1. {filename} 파일을 다운로드")
    print(f"2. 'new_price' 컬럼에 새로운 가격 입력")
    print(f"3. Cafe24 관리자 > 상품관리 > 상품일괄등록에서 업로드")
    
    return filepath

if __name__ == "__main__":
    create_price_update_excel()