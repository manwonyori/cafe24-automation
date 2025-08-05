#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
업체 관리 시스템
- 공급업체 관리
- 배송업체 관리  
- 제조사 관리
- 브랜드 관리
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
        """공급업체 목록 조회"""
        try:
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            url = f"https://{mall_id}.cafe24api.com/api/v2/admin/suppliers"
            params = {
                'limit': 100,
                'offset': 0
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                suppliers = data.get('suppliers', [])
                
                # 상품 수 계산을 위해 각 공급업체별 상품 조회
                for supplier in suppliers:
                    supplier_code = supplier.get('supplier_code')
                    product_count = self._get_product_count_by_supplier(supplier_code)
                    supplier['product_count'] = product_count
                
                return jsonify({
                    'success': True,
                    'suppliers': suppliers,
                    'count': len(suppliers)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 오류: {response.status_code}',
                    'message': response.text
                }), response.status_code
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def create_supplier(self):
        """새 공급업체 등록"""
        try:
            data = request.json
            supplier_name = data.get('supplier_name')
            
            if not supplier_name:
                return jsonify({'success': False, 'error': '공급업체명은 필수입니다'}), 400
            
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            url = f"https://{mall_id}.cafe24api.com/api/v2/admin/suppliers"
            
            supplier_data = {
                'supplier': {
                    'supplier_name': supplier_name,
                    'use_supplier': 'T',
                    'supplier_manager_name': data.get('manager_name', ''),
                    'supplier_manager_phone': data.get('manager_phone', ''),
                    'supplier_manager_email': data.get('manager_email', ''),
                    'company_registration_no': data.get('registration_no', ''),
                    'supplier_address': data.get('address', ''),
                    'supplier_memo': data.get('memo', '')
                }
            }
            
            response = requests.post(url, headers=headers, json=supplier_data)
            
            if response.status_code == 201:
                data = response.json()
                return jsonify({
                    'success': True,
                    'supplier': data.get('supplier', {}),
                    'message': '공급업체가 성공적으로 등록되었습니다'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 오류: {response.status_code}',
                    'message': response.text
                }), response.status_code
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def update_supplier(self, supplier_code):
        """공급업체 정보 수정"""
        try:
            data = request.json
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            url = f"https://{mall_id}.cafe24api.com/api/v2/admin/suppliers/{supplier_code}"
            
            update_data = {'supplier': {}}
            
            # 수정 가능한 필드만 추가
            if 'supplier_name' in data:
                update_data['supplier']['supplier_name'] = data['supplier_name']
            if 'manager_name' in data:
                update_data['supplier']['supplier_manager_name'] = data['manager_name']
            if 'manager_phone' in data:
                update_data['supplier']['supplier_manager_phone'] = data['manager_phone']
            if 'manager_email' in data:
                update_data['supplier']['supplier_manager_email'] = data['manager_email']
            if 'address' in data:
                update_data['supplier']['supplier_address'] = data['address']
            if 'memo' in data:
                update_data['supplier']['supplier_memo'] = data['memo']
            
            response = requests.put(url, headers=headers, json=update_data)
            
            if response.status_code == 200:
                return jsonify({
                    'success': True,
                    'message': '공급업체 정보가 수정되었습니다'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 오류: {response.status_code}',
                    'message': response.text
                }), response.status_code
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_manufacturers(self):
        """제조사 목록 조회"""
        try:
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            url = f"https://{mall_id}.cafe24api.com/api/v2/admin/manufacturers"
            params = {
                'limit': 100,
                'offset': 0
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return jsonify({
                    'success': True,
                    'manufacturers': data.get('manufacturers', []),
                    'count': data.get('count', 0)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 오류: {response.status_code}'
                }), response.status_code
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def create_manufacturer(self):
        """새 제조사 등록"""
        try:
            data = request.json
            manufacturer_name = data.get('manufacturer_name')
            
            if not manufacturer_name:
                return jsonify({'success': False, 'error': '제조사명은 필수입니다'}), 400
            
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            url = f"https://{mall_id}.cafe24api.com/api/v2/admin/manufacturers"
            
            manufacturer_data = {
                'manufacturer': {
                    'manufacturer_name': manufacturer_name,
                    'use_manufacturer': 'T',
                    'president_name': data.get('president_name', ''),
                    'phone': data.get('phone', ''),
                    'homepage_url': data.get('homepage_url', ''),
                    'email': data.get('email', ''),
                    'address': data.get('address', '')
                }
            }
            
            response = requests.post(url, headers=headers, json=manufacturer_data)
            
            if response.status_code == 201:
                data = response.json()
                return jsonify({
                    'success': True,
                    'manufacturer': data.get('manufacturer', {}),
                    'message': '제조사가 성공적으로 등록되었습니다'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 오류: {response.status_code}',
                    'message': response.text
                }), response.status_code
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_brands(self):
        """브랜드 목록 조회"""
        try:
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            url = f"https://{mall_id}.cafe24api.com/api/v2/admin/brands"
            params = {
                'limit': 100,
                'offset': 0
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return jsonify({
                    'success': True,
                    'brands': data.get('brands', []),
                    'count': data.get('count', 0)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 오류: {response.status_code}'
                }), response.status_code
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def create_brand(self):
        """새 브랜드 등록"""
        try:
            data = request.json
            brand_name = data.get('brand_name')
            
            if not brand_name:
                return jsonify({'success': False, 'error': '브랜드명은 필수입니다'}), 400
            
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            url = f"https://{mall_id}.cafe24api.com/api/v2/admin/brands"
            
            brand_data = {
                'brand': {
                    'brand_name': brand_name,
                    'use_brand': 'T'
                }
            }
            
            response = requests.post(url, headers=headers, json=brand_data)
            
            if response.status_code == 201:
                data = response.json()
                return jsonify({
                    'success': True,
                    'brand': data.get('brand', {}),
                    'message': '브랜드가 성공적으로 등록되었습니다'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 오류: {response.status_code}',
                    'message': response.text
                }), response.status_code
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_shipping_companies(self):
        """배송업체 목록 조회"""
        try:
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            # Cafe24에서는 배송업체를 별도로 관리하지 않고 배송 설정에서 관리
            # 기본 배송업체 목록 제공
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
    
    def _get_product_count_by_supplier(self, supplier_code):
        """특정 공급업체의 상품 수 조회"""
        try:
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/count"
            params = {
                'supplier_code': supplier_code
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('count', 0)
            else:
                return 0
                
        except:
            return 0
    
    def update_product_vendor(self):
        """상품의 업체 정보 일괄 수정"""
        try:
            data = request.json
            product_nos = data.get('product_nos', [])
            vendor_type = data.get('vendor_type')  # 'supplier', 'manufacturer', 'brand'
            vendor_code = data.get('vendor_code')
            
            if not product_nos or not vendor_type or not vendor_code:
                return jsonify({'success': False, 'error': '필수 파라미터가 누락되었습니다'}), 400
            
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            results = []
            success_count = 0
            failed_count = 0
            
            for product_no in product_nos:
                try:
                    url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{product_no}"
                    
                    update_data = {'product': {}}
                    
                    if vendor_type == 'supplier':
                        update_data['product']['supplier_code'] = vendor_code
                    elif vendor_type == 'manufacturer':
                        update_data['product']['manufacturer_code'] = vendor_code
                    elif vendor_type == 'brand':
                        update_data['product']['brand_code'] = vendor_code
                    
                    response = requests.put(url, headers=headers, json=update_data)
                    
                    if response.status_code == 200:
                        success_count += 1
                        results.append({
                            'product_no': product_no,
                            'status': 'success'
                        })
                    else:
                        failed_count += 1
                        results.append({
                            'product_no': product_no,
                            'status': 'failed',
                            'error': response.text
                        })
                        
                except Exception as e:
                    failed_count += 1
                    results.append({
                        'product_no': product_no,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return jsonify({
                'success': True,
                'total': len(product_nos),
                'success_count': success_count,
                'failed_count': failed_count,
                'results': results
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