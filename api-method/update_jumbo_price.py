#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[인생]점보떡볶이1490g 가격 수정을 위한 Excel 파일 생성
"""
import requests
import pandas as pd
import json
import sys
import io
from datetime import datetime
import os

# UTF-8 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API 서버 URL
base_url = 'https://cafe24-automation.onrender.com'

def search_product():
    """제품 검색하여 상품코드 찾기"""
    print("=== [인생]점보떡볶이1490g 검색 중... ===\n")
    
    # 자연어 명령으로 검색
    command_data = {
        "command": "[인생]점보떡볶이1490g 제품 보여줘"
    }
    
    response = requests.post(f'{base_url}/api/execute', json=command_data)
    
    if response.status_code == 200:
        result = response.json()
        if 'data' in result:
            products = result['data']
            for product in products:
                product_name = product.get('product_name', '')
                if '점보떡볶' in product_name and '1490' in product_name:
                    print(f"✅ 제품 찾음!")
                    print(f"- 상품코드: {product.get('product_no')}")
                    print(f"- 상품명: {product_name}")
                    print(f"- 현재 판매가: {product.get('price', 0):,}원")
                    print(f"- 공급가: {product.get('supply_price', 0):,}원")
                    return product
    
    # 전체 제품 목록에서 검색
    print("\n전체 제품 목록에서 검색 중...")
    response = requests.get(f'{base_url}/api/products')
    
    if response.status_code == 200:
        products = response.json()
        for product in products:
            product_name = str(product.get('product_name', ''))
            if '점보떡볶' in product_name and '1490' in product_name:
                print(f"\n✅ 제품 찾음!")
                print(f"- 상품코드: {product.get('product_no')}")
                print(f"- 상품명: {product_name}")
                print(f"- 현재 판매가: {product.get('price', 0):,}원")
                return product
    
    return None

def create_price_update_csv(product_info):
    """가격 수정용 CSV 파일 생성"""
    if not product_info:
        print("❌ 제품 정보를 찾을 수 없습니다.")
        return None
    
    # CSV 형식에 맞게 데이터 준비
    # excelUploadProductDefault_uplode_product.csv 형식 참고
    data = {
        '상품코드': [product_info.get('product_no', '')],
        '자체 상품코드': [''],  # 비워둠
        '진열상태': ['Y'],
        '판매상태': ['Y'],
        '상품분류 번호': [''],
        '상품분류 신상품영역': [''],
        '상품분류 추천상품영역': [''],
        '상품명': [product_info.get('product_name', '')],
        '영문 상품명': [''],
        '상품명(관리용)': [''],
        '공급사 상품명': [''],
        '모델명': [''],
        '상품 요약설명': [''],
        '상품 간략설명': [''],
        '상품 상세설명': [''],
        '모바일 상품 상세설명 설정': [''],
        '모바일 상품 상세설명': [''],
        '검색어설정': [''],
        '과세구분': ['A'],
        '소비자가': [''],
        '공급가': [product_info.get('supply_price', '')],
        '상품가': [''],
        '판매가': ['13500'],  # 수정할 가격
        '판매가 대체문구 사용': [''],
        '판매가 대체문구': [''],
        '주문수량 제한 기준': [''],
        '최소 주문수량(이상)': [''],
        '최대 주문수량(이하)': [''],
        '적립금': [''],
        '적립금 구분': [''],
        '공통이벤트 정보': [''],
        '성인인증': [''],
        '옵션사용': [''],
        '품목 구성방식': [''],
        '옵션 표시방식': [''],
        '옵션세트명': [''],
        '옵션입력': [''],
        '옵션 스타일': [''],
        '버튼이미지 설정': [''],
        '색상 설정': [''],
        '필수여부': [''],
        '품절표시 문구': [''],
        '추가입력옵션': [''],
        '추가입력옵션 명칭': [''],
        '추가입력옵션 선택/필수여부': [''],
        '입력글자수(자)': [''],
        '이미지등록(상세)': [''],
        '이미지등록(목록)': [''],
        '이미지등록(작은목록)': [''],
        '이미지등록(축소)': [''],
        '이미지등록(추가)': [''],
        '제조사': [''],
        '공급사': [''],
        '브랜드': [''],
        '트렌드': [''],
        '자체분류 코드': [''],
        '제조일자': [''],
        '출시일자': [''],
        '유효기간 사용여부': [''],
        '유효기간': [''],
        '원산지': [''],
        '상품부피(cm)': [''],
        '상품결제안내': [''],
        '상품배송안내': [''],
        '교환/반품안내': [''],
        '서비스문의/안내': [''],
        '배송정보': [''],
        '배송방법': [''],
        '국내/해외배송': [''],
        '배송지역': [''],
        '배송비 선결제 설정': [''],
        '배송기간': [''],
        '배송비 구분': [''],
        '배송비입력': [''],
        '스토어픽업 설정': [''],
        '상품 전체중량(kg)': [''],
        'HS코드': [''],
        '상품 구분(해외통관)': [''],
        '상품소재': [''],
        '영문 상품소재(해외통관)': [''],
        '옷감(해외통관)': [''],
        '검색엔진최적화(SEO) 검색엔진 노출 설정': [''],
        '검색엔진최적화(SEO) Title': [''],
        '검색엔진최적화(SEO) Author': [''],
        '검색엔진최적화(SEO) Description': [''],
        '검색엔진최적화(SEO) Keywords': [''],
        '검색엔진최적화(SEO) 상품 이미지 Alt 텍스트': [''],
        '개별결제수단설정': [''],
        '상품배송유형 코드': [''],
        '메모': [f'가격 수정: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}']
    }
    
    # 데이터프레임 생성
    df = pd.DataFrame(data)
    
    # 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"price_update_jumbo_{timestamp}.csv"
    filepath = os.path.join('static', 'excel_templates', filename)
    
    # CSV 파일 저장 (BOM 포함)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ CSV 파일 생성 완료: {filepath}")
    print(f"- 상품코드: {product_info.get('product_no')}")
    print(f"- 상품명: {product_info.get('product_name')}")
    print(f"- 변경할 가격: 13,500원")
    
    return filepath

def main():
    # 제품 검색
    product = search_product()
    
    if product:
        # CSV 파일 생성
        csv_file = create_price_update_csv(product)
        
        if csv_file:
            print("\n=== 업로드 방법 ===")
            print("1. Cafe24 관리자 페이지 로그인")
            print("2. 상품관리 > 상품일괄등록/수정 메뉴 이동")
            print("3. '상품일괄수정' 탭 선택")
            print("4. 생성된 CSV 파일 업로드")
            print(f"5. 파일 위치: {os.path.abspath(csv_file)}")
            print("\n※ 주의: 상품코드는 반드시 첫 번째 열에 있어야 합니다!")
    else:
        print("❌ [인생]점보떡볶이1490g 제품을 찾을 수 없습니다.")

if __name__ == "__main__":
    main()