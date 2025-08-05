#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
"""
가격 수정 API 엔드포인트 추가
"""

# app.py에 추가할 엔드포인트 코드
endpoint_code = '''
@app.route('/api/products/<int:product_no>/price', methods=['PUT'])
@handle_errors
def update_product_price(product_no):
    """개별 상품 가격 수정"""
    try:
        data = request.get_json()
        new_price = data.get('price')
        
        if not new_price:
            return jsonify({'success': False, 'error': '가격을 입력하세요'}), 400
        
        # Cafe24 API로 가격 수정
        headers = get_headers()
        mall_id = get_mall_id()
        
        # 옵션 상품 확인
        product_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{product_no}"
        response = requests.get(product_url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({'success': False, 'error': '상품 정보를 가져올 수 없습니다'}), 404
        
        product = response.json().get('product', {})
        has_option = product.get('has_option', 'F') == 'T'
        
        success = False
        
        if has_option:
            # 옵션 상품인 경우 변형 상품 가격 수정
            variants_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{product_no}/variants"
            response = requests.get(variants_url, headers=headers)
            
            if response.status_code == 200:
                variants = response.json().get('variants', [])
                success_count = 0
                
                for variant in variants:
                    variant_code = variant.get('variant_code')
                    variant_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{product_no}/variants/{variant_code}"
                    
                    update_data = {
                        "request": {
                            "variant": {
                                "price": str(new_price)
                            }
                        }
                    }
                    
                    response = requests.put(variant_url, headers=headers, json=update_data)
                    if response.status_code == 200:
                        success_count += 1
                
                success = success_count > 0
        
        # 기본 상품 가격 수정 (옵션 상품이어도 시도)
        update_data = {
            "request": {
                "product": {
                    "price": str(new_price),
                    "retail_price": str(new_price)
                }
            }
        }
        
        response = requests.put(product_url, headers=headers, json=update_data)
        
        if response.status_code == 200 or success:
            return jsonify({
                'success': True,
                'product_no': product_no,
                'new_price': new_price,
                'has_option': has_option
            })
        else:
            return jsonify({
                'success': False,
                'error': 'API 오류',
                'details': response.text[:200]
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bulk-price-update', methods=['POST'])
@handle_errors
def bulk_price_update():
    """대량 가격 수정"""
    try:
        data = request.get_json()
        product_ids = data.get('product_ids', [])
        target_margin = data.get('target_margin')
        
        if not product_ids or not target_margin:
            return jsonify({'success': False, 'error': '필수 정보가 누락되었습니다'}), 400
        
        success_count = 0
        failed_count = 0
        
        for product_id in product_ids:
            # 각 상품 정보 가져오기
            headers = get_headers()
            mall_id = get_mall_id()
            product_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{product_id}"
            
            response = requests.get(product_url, headers=headers)
            if response.status_code == 200:
                product = response.json().get('product', {})
                supply_price = float(product.get('supply_price', 0))
                
                if supply_price > 0:
                    # 목표 마진율로 새 가격 계산
                    new_price = int(supply_price * (1 + target_margin / 100))
                    
                    # 가격 수정 시도
                    update_result = update_product_price_internal(product_id, new_price)
                    
                    if update_result:
                        success_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
        
        return jsonify({
            'success': True,
            'success_count': success_count,
            'failed_count': failed_count
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def update_product_price_internal(product_no, new_price):
    """내부 가격 수정 함수"""
    try:
        headers = get_headers()
        mall_id = get_mall_id()
        
        update_data = {
            "request": {
                "product": {
                    "price": str(new_price)
                }
            }
        }
        
        product_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{product_no}"
        response = requests.put(product_url, headers=headers, json=update_data)
        
        return response.status_code == 200
    except:
        return False
'''

print("=== 가격 수정 API 엔드포인트 코드 ===")
print("\napp.py에 다음 코드를 추가하세요:\n")
print(endpoint_code)

print("\n\n=== 사용 방법 ===")
print("1. 개별 상품 가격 수정:")
print("   PUT /api/products/{product_no}/price")
print("   Body: {\"price\": \"13500\"}")
print("\n2. 대량 가격 수정:")
print("   POST /api/bulk-price-update")
print("   Body: {\"product_ids\": [209, 210], \"target_margin\": 25}")
print("\n3. 마진율 대시보드에서:")
print("   - 상품 선택 후 '가격 일괄 수정' 버튼 클릭")
print("   - 목표 마진율 입력")
print("   - '가격 수정 실행' 클릭")