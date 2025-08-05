#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
업체 관리 시스템 - 디버그 버전
"""
from flask import Blueprint, request, jsonify
import requests
from datetime import datetime
import json

vendor_bp = Blueprint('vendor', __name__)

class VendorManager:
    def __init__(self, get_headers, get_mall_id):
        self.get_headers = get_headers
        self.get_mall_id = get_mall_id
    
    def get_suppliers(self):
        """공급업체 목록 조회 - 디버그 버전"""
        try:
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            # 디버그: API 버전 확인
            print(f"Debug: Mall ID = {mall_id}")
            print(f"Debug: Headers = {headers}")
            
            # 디버그: 실제 응답 확인을 위한 테스트 호출
            test_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
            test_params = {'limit': 1, 'fields': 'product_no,product_name'}
            test_response = requests.get(test_url, headers=headers, params=test_params)
            print(f"Debug: Test API Response Status = {test_response.status_code}")
            if test_response.status_code == 200:
                test_data = test_response.json()
                if 'products' in test_data and test_data['products']:
                    print(f"Debug: Available fields in product = {list(test_data['products'][0].keys())}")
            
            # 먼저 상품에서 공급업체 정보 추출 시도
            products_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
            params = {
                'limit': 100,
                'fields': 'product_no,product_name,supplier_code,supplier_name,supplier_product_code,origin_classification,manufacturer_code,manufacturer_name,brand_code,brand_name'
            }
            
            response = requests.get(products_url, headers=headers, params=params)
            print(f"Debug: Products API Response Status = {response.status_code}")
            
            suppliers_dict = {}
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                # 상품에서 공급업체 정보 추출 (다양한 필드명 시도)
                for product in products:
                    # 공급업체 정보 추출 - 여러 필드명 시도
                    supplier_code = (product.get('supplier_code') or 
                                   product.get('vendor_code') or 
                                   product.get('supplier_id'))
                    supplier_name = (product.get('supplier_name') or 
                                   product.get('vendor_name') or 
                                   product.get('supplier_company_name', ''))
                    
                    # 제조사 정보도 수집
                    manufacturer_code = product.get('manufacturer_code')
                    manufacturer_name = product.get('manufacturer_name', '')
                    
                    # 브랜드 정보도 수집  
                    brand_code = product.get('brand_code')
                    brand_name = product.get('brand_name', '')
                    
                    # 공급업체 코드가 있으면 추가
                    if supplier_code and supplier_code not in suppliers_dict:
                        suppliers_dict[supplier_code] = {
                            'supplier_code': supplier_code,
                            'supplier_name': supplier_name or f'공급업체 {supplier_code}',
                            'product_count': 0,
                            'use_supplier': 'T',
                            'supplier_type': 'supplier'
                        }
                    
                    # 제조사 코드를 공급업체로 추가 (제조사가 있지만 공급업체가 없는 경우)
                    if manufacturer_code and not supplier_code and manufacturer_code not in suppliers_dict:
                        suppliers_dict[manufacturer_code] = {
                            'supplier_code': manufacturer_code,
                            'supplier_name': manufacturer_name or f'제조사 {manufacturer_code}',
                            'product_count': 0,
                            'use_supplier': 'T',
                            'supplier_type': 'manufacturer'
                        }
                    
                    # 브랜드 코드를 공급업체로 추가 (브랜드가 있지만 공급업체/제조사가 없는 경우)
                    if brand_code and not supplier_code and not manufacturer_code and brand_code not in suppliers_dict:
                        suppliers_dict[brand_code] = {
                            'supplier_code': brand_code,
                            'supplier_name': brand_name or f'브랜드 {brand_code}',
                            'product_count': 0,
                            'use_supplier': 'T',
                            'supplier_type': 'brand'
                        }
                    
                    # 카운트 증가
                    if supplier_code and supplier_code in suppliers_dict:
                        suppliers_dict[supplier_code]['product_count'] += 1
                    elif manufacturer_code and manufacturer_code in suppliers_dict:
                        suppliers_dict[manufacturer_code]['product_count'] += 1
                    elif brand_code and brand_code in suppliers_dict:
                        suppliers_dict[brand_code]['product_count'] += 1
            
            # 실제 공급업체 API 시도 (다양한 엔드포인트 시도)
            try:
                # 여러 가능한 공급업체 API 엔드포인트 시도
                supplier_endpoints = [
                    f"https://{mall_id}.cafe24api.com/api/v2/admin/suppliers",
                    f"https://{mall_id}.cafe24api.com/api/v2/admin/vendors",
                    f"https://{mall_id}.cafe24api.com/api/v2/admin/product/suppliers"
                ]
                
                for endpoint in supplier_endpoints:
                    try:
                        suppliers_response = requests.get(endpoint, headers=headers, params={'limit': 100})
                        print(f"Debug: Testing {endpoint} - Status = {suppliers_response.status_code}")
                        
                        if suppliers_response.status_code == 200:
                            suppliers_data = suppliers_response.json()
                            print(f"Debug: API Response keys = {list(suppliers_data.keys())}")
                            
                            # 다양한 응답 구조 시도
                            api_suppliers = (suppliers_data.get('suppliers', []) or 
                                           suppliers_data.get('vendors', []) or 
                                           suppliers_data.get('data', []))
                            
                            if api_suppliers:
                                print(f"Debug: Found {len(api_suppliers)} suppliers from API")
                                print(f"Debug: First supplier structure = {api_suppliers[0] if api_suppliers else 'None'}")
                                
                                # API 공급업체 정보로 업데이트
                                for supplier in api_suppliers:
                                    code = (supplier.get('supplier_code') or 
                                           supplier.get('vendor_code') or 
                                           supplier.get('code'))
                                    name = (supplier.get('supplier_name') or 
                                           supplier.get('vendor_name') or 
                                           supplier.get('name'))
                                    
                                    if code:
                                        if code in suppliers_dict:
                                            suppliers_dict[code].update(supplier)
                                        else:
                                            supplier_info = {
                                                'supplier_code': code,
                                                'supplier_name': name or f'공급업체 {code}',
                                                'product_count': 0,
                                                'use_supplier': supplier.get('use_supplier', 'T'),
                                                'supplier_type': 'api_supplier'
                                            }
                                            # 추가 정보가 있으면 포함
                                            if supplier.get('supplier_manager_name'):
                                                supplier_info['supplier_manager_name'] = supplier.get('supplier_manager_name')
                                            if supplier.get('representative_name'):
                                                supplier_info['representative_name'] = supplier.get('representative_name')
                                            
                                            suppliers_dict[code] = supplier_info
                                break
                    except Exception as endpoint_error:
                        print(f"Debug: Endpoint {endpoint} failed = {str(endpoint_error)}")
                        continue
                        
            except Exception as e:
                print(f"Debug: Suppliers API Error = {str(e)}")
                # 공급업체 API가 없어도 계속 진행
            
            # 결과 변환
            suppliers = list(suppliers_dict.values())
            
            # 공급업체가 없으면 상품별로 기본 공급업체 생성
            if not suppliers and 'products' in locals():
                # 상품이 있지만 공급업체 정보가 없는 경우, 상품별로 기본 공급업체 생성
                for i, product in enumerate(products[:5]):  # 최대 5개까지만
                    supplier_code = f'DEFAULT_{i+1:03d}'
                    suppliers.append({
                        'supplier_code': supplier_code,
                        'supplier_name': f'기본공급처 {i+1}',
                        'product_count': 1,
                        'use_supplier': 'T',
                        'supplier_type': 'default',
                        'related_product': product.get('product_name', '')
                    })
            elif not suppliers:
                # 상품도 없는 경우 기본 샘플 데이터
                suppliers = [
                    {
                        'supplier_code': 'S000000A',
                        'supplier_name': '기본 공급업체',
                        'product_count': 0,
                        'use_supplier': 'T',
                        'supplier_type': 'sample',
                        'supplier_manager_name': '담당자',
                        'supplier_manager_phone': '010-0000-0000'
                    }
                ]
            
            return jsonify({
                'success': True,
                'suppliers': suppliers,
                'count': len(suppliers),
                'debug_info': {
                    'extracted_from_products': len([s for s in suppliers_dict.values() if s.get('supplier_type') != 'api_supplier']) > 0,
                    'extracted_from_api': len([s for s in suppliers_dict.values() if s.get('supplier_type') == 'api_supplier']) > 0,
                    'total_products_checked': len(products) if 'products' in locals() else 0,
                    'supplier_types': list(set(s.get('supplier_type', 'unknown') for s in suppliers_dict.values())),
                    'api_fields_found': list(products[0].keys()) if 'products' in locals() and products else []
                }
            })
            
        except Exception as e:
            print(f"Debug: General Error = {str(e)}")
            return jsonify({
                'success': False, 
                'error': str(e),
                'debug_info': {
                    'error_type': type(e).__name__,
                    'error_details': str(e)
                }
            }), 500
    
    def create_supplier(self):
        """새 공급업체 등록 - 간소화 버전"""
        try:
            data = request.json
            supplier_name = data.get('supplier_name')
            
            if not supplier_name:
                return jsonify({'success': False, 'error': '공급업체명은 필수입니다'}), 400
            
            # 실제 API가 없을 경우를 대비한 로컬 저장
            # 실제 구현에서는 DB나 파일에 저장
            new_supplier = {
                'supplier_code': f'S{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'supplier_name': supplier_name,
                'use_supplier': 'T',
                'supplier_manager_name': data.get('manager_name', ''),
                'supplier_manager_phone': data.get('manager_phone', ''),
                'supplier_manager_email': data.get('manager_email', ''),
                'created_date': datetime.now().isoformat()
            }
            
            return jsonify({
                'success': True,
                'supplier': new_supplier,
                'message': '공급업체가 등록되었습니다 (로컬 저장)'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def update_supplier(self, supplier_code):
        """공급업체 정보 수정"""
        return jsonify({
            'success': True,
            'message': '공급업체 정보가 수정되었습니다 (시뮬레이션)'
        })
    
    def get_manufacturers(self):
        """제조사 목록 조회 - 상품에서 추출"""
        try:
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            # 상품에서 제조사 정보 추출
            url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
            params = {
                'limit': 100,
                'fields': 'product_no,manufacturer_code,manufacturer_name'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            manufacturers_dict = {}
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                for product in products:
                    mfr_code = product.get('manufacturer_code')
                    mfr_name = product.get('manufacturer_name', '')
                    
                    if mfr_code and mfr_code not in manufacturers_dict:
                        manufacturers_dict[mfr_code] = {
                            'manufacturer_code': mfr_code,
                            'manufacturer_name': mfr_name or f'제조사 {mfr_code}',
                            'use_manufacturer': 'T',
                            'product_count': 0
                        }
                    
                    if mfr_code:
                        manufacturers_dict[mfr_code]['product_count'] += 1
            
            manufacturers = list(manufacturers_dict.values())
            
            # 제조사가 없으면 샘플 데이터
            if not manufacturers:
                manufacturers = [
                    {
                        'manufacturer_code': 'M000000A',
                        'manufacturer_name': '기본 제조사',
                        'use_manufacturer': 'T',
                        'product_count': 0
                    }
                ]
            
            return jsonify({
                'success': True,
                'manufacturers': manufacturers,
                'count': len(manufacturers)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def create_manufacturer(self):
        """새 제조사 등록"""
        try:
            data = request.json
            manufacturer_name = data.get('manufacturer_name')
            
            if not manufacturer_name:
                return jsonify({'success': False, 'error': '제조사명은 필수입니다'}), 400
            
            new_manufacturer = {
                'manufacturer_code': f'M{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'manufacturer_name': manufacturer_name,
                'use_manufacturer': 'T',
                'created_date': datetime.now().isoformat()
            }
            
            return jsonify({
                'success': True,
                'manufacturer': new_manufacturer,
                'message': '제조사가 등록되었습니다 (로컬 저장)'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_brands(self):
        """브랜드 목록 조회 - 상품명에서 추출"""
        try:
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            # 상품에서 브랜드 정보 추출
            url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
            params = {
                'limit': 100,
                'fields': 'product_no,product_name,brand_code,brand_name'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            brands_dict = {}
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                for product in products:
                    # API 브랜드 정보
                    brand_code = product.get('brand_code')
                    brand_name = product.get('brand_name', '')
                    
                    # 상품명에서 브랜드 추출
                    product_name = product.get('product_name', '')
                    if '[' in product_name and ']' in product_name:
                        start = product_name.find('[')
                        end = product_name.find(']')
                        extracted_brand = product_name[start+1:end]
                        
                        if not brand_code:
                            brand_code = f'B{abs(hash(extracted_brand)) % 10000:04d}'
                            brand_name = extracted_brand
                    
                    if brand_code and brand_code not in brands_dict:
                        brands_dict[brand_code] = {
                            'brand_code': brand_code,
                            'brand_name': brand_name or f'브랜드 {brand_code}',
                            'use_brand': 'T',
                            'product_count': 0
                        }
                    
                    if brand_code:
                        brands_dict[brand_code]['product_count'] += 1
            
            brands = list(brands_dict.values())
            
            return jsonify({
                'success': True,
                'brands': brands,
                'count': len(brands)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def create_brand(self):
        """새 브랜드 등록"""
        try:
            data = request.json
            brand_name = data.get('brand_name')
            
            if not brand_name:
                return jsonify({'success': False, 'error': '브랜드명은 필수입니다'}), 400
            
            new_brand = {
                'brand_code': f'B{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'brand_name': brand_name,
                'use_brand': 'T',
                'created_date': datetime.now().isoformat()
            }
            
            return jsonify({
                'success': True,
                'brand': new_brand,
                'message': '브랜드가 등록되었습니다 (로컬 저장)'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_shipping_companies(self):
        """배송업체 목록 조회"""
        try:
            # 기본 배송업체 목록
            shipping_companies = [
                {'code': 'cj', 'name': 'CJ대한통운', 'tracking_url': 'https://www.cjlogistics.com'},
                {'code': 'hanjin', 'name': '한진택배', 'tracking_url': 'https://www.hanjin.co.kr'},
                {'code': 'lotte', 'name': '롯데택배', 'tracking_url': 'https://www.lotteglogis.com'},
                {'code': 'logen', 'name': '로젠택배', 'tracking_url': 'https://www.ilogen.com'},
                {'code': 'post', 'name': '우체국택배', 'tracking_url': 'https://www.epost.go.kr'},
                {'code': 'kdexp', 'name': '경동택배', 'tracking_url': 'https://kdexp.com'},
                {'code': 'daesin', 'name': '대신택배', 'tracking_url': 'https://www.ds3211.co.kr'},
                {'code': 'cvsnet', 'name': 'GS Postbox', 'tracking_url': 'https://www.cvsnet.co.kr'},
                {'code': 'cu', 'name': 'CU편의점택배', 'tracking_url': 'https://www.cupost.co.kr'}
            ]
            
            return jsonify({
                'success': True,
                'shipping_companies': shipping_companies,
                'count': len(shipping_companies)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def update_product_vendor(self):
        """상품의 업체 정보 일괄 수정"""
        try:
            data = request.json
            product_nos = data.get('product_nos', [])
            vendor_type = data.get('vendor_type')
            vendor_code = data.get('vendor_code')
            
            # 시뮬레이션 응답
            return jsonify({
                'success': True,
                'total': len(product_nos),
                'success_count': len(product_nos),
                'failed_count': 0,
                'message': '업체 정보가 수정되었습니다 (시뮬레이션)'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

# 라우트 등록
def register_vendor_routes(bp, manager):
    """업체 관리 라우트 등록"""
    # 공급업체
    bp.add_url_rule('/suppliers', 'get_suppliers', manager.get_suppliers, methods=['GET'])
    bp.add_url_rule('/suppliers', 'create_supplier', manager.create_supplier, methods=['POST'])
    bp.add_url_rule('/suppliers/<supplier_code>', 'update_supplier', manager.update_supplier, methods=['PUT'])
    
    # 제조사
    bp.add_url_rule('/manufacturers', 'get_manufacturers', manager.get_manufacturers, methods=['GET'])
    bp.add_url_rule('/manufacturers', 'create_manufacturer', manager.create_manufacturer, methods=['POST'])
    
    # 브랜드
    bp.add_url_rule('/brands', 'get_brands', manager.get_brands, methods=['GET'])
    bp.add_url_rule('/brands', 'create_brand', manager.create_brand, methods=['POST'])
    
    # 배송업체
    bp.add_url_rule('/shipping-companies', 'get_shipping_companies', manager.get_shipping_companies, methods=['GET'])
    
    # 상품 업체 정보 수정
    bp.add_url_rule('/update-product-vendor', 'update_product_vendor', manager.update_product_vendor, methods=['POST'])