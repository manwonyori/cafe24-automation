#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Product API with ALL Cafe24 features
완전한 상품 API 구현 - 모든 기능 포함
"""
from flask import Blueprint, request, jsonify, send_file
import requests
from datetime import datetime
import json
import pandas as pd
import io
from urllib.parse import quote

products_bp = Blueprint('products', __name__)

class ProductAPI:
    def __init__(self, get_headers, get_mall_id):
        self.get_headers = get_headers
        self.get_mall_id = get_mall_id
        self.base_url = None
        
    def _get_base_url(self):
        if not self.base_url:
            self.base_url = f"https://{self.get_mall_id()}.cafe24api.com/api/v2/admin/products"
        return self.base_url
    
    def get_products_advanced(self):
        """고급 필터링, 정렬, 페이지네이션을 포함한 상품 목록 조회"""
        try:
            headers = self.get_headers()
            url = self._get_base_url()
            
            # 모든 가능한 파라미터 수집
            params = {}
            
            # 1. 페이지네이션 파라미터
            limit = request.args.get('limit', 100, type=int)
            # 전체보기인 경우 최대값 설정
            if limit >= 9999:
                limit = 10000  # Cafe24 API 최대 한도
            params['limit'] = limit
            params['offset'] = request.args.get('offset', 0, type=int)
            
            # 2. 필드 선택 (성능 최적화)
            fields = request.args.get('fields')
            if not fields:
                # 기본 필드셋 - 모든 주요 필드 포함
                fields = ','.join([
                    'product_no', 'product_code', 'custom_product_code',
                    'product_name', 'eng_product_name', 'model_name',
                    'price', 'retail_price', 'supply_price',
                    'display', 'selling', 'product_condition',
                    'product_used_month', 'summary_description', 'simple_description',
                    'product_tag', 'use_naverpay', 'naverpay_type',
                    'quantity', 'tax_type', 'tax_rate',
                    'price_content', 'buy_limit_by_product',
                    'buy_limit_type', 'buy_unit_type', 'buy_unit',
                    'order_quantity_limit_type', 'minimum_quantity', 'maximum_quantity',
                    'points_by_product', 'points_setting_by_product',
                    'points_amount', 'except_member_points',
                    'adult_certification', 'detail_image', 'list_image',
                    'tiny_image', 'small_image', 'has_option',
                    'option_type', 'manufacturer_code', 'supplier_code',
                    'brand_code', 'trend_code', 'product_weight',
                    'expiration_date', 'expiration_date_start', 'expiration_date_end',
                    'exposure_priority', 'exposure_limit_type',
                    'exposure_limit_start_date', 'exposure_limit_end_date',
                    'relative_product_name', 'shipping_fee_by_product',
                    'shipping_method', 'shipping_period',
                    'shipping_scope', 'shipping_area', 'shipping_fee_type',
                    'shipping_rates', 'updated_date', 'created_date',
                    'english_product_material', 'product_material',
                    'cloth_fabric', 'made_in_code', 'additional_information',
                    'show_purchase_list', 'related_product', 'product_category',
                    'repurchase_restriction', 'single_purchase_restriction',
                    'buy_member_id_limit', 'buy_ip_limit',
                    'buy_limit_period', 'buy_limit_look_period',
                    'buy_limit_by_first_purchase', 'buy_limit_by_age'
                ])
            params['fields'] = fields
            
            # 3. 가격 필터링
            if request.args.get('price_min'):
                params['price_min'] = request.args.get('price_min', type=int)
            if request.args.get('price_max'):
                params['price_max'] = request.args.get('price_max', type=int)
            
            # 4. 재고 필터링
            if request.args.get('stock_min'):
                params['quantity_min'] = request.args.get('stock_min', type=int)
            if request.args.get('stock_max'):
                params['quantity_max'] = request.args.get('stock_max', type=int)
            
            # 5. 날짜 필터링
            if request.args.get('created_start'):
                params['created_start_date'] = request.args.get('created_start')
            if request.args.get('created_end'):
                params['created_end_date'] = request.args.get('created_end')
            if request.args.get('updated_start'):
                params['updated_start_date'] = request.args.get('updated_start')
            if request.args.get('updated_end'):
                params['updated_end_date'] = request.args.get('updated_end')
            
            # 6. 브랜드 필터링 (쉼표로 구분된 다중 값)
            if request.args.get('brand_codes'):
                params['brand_code'] = request.args.get('brand_codes')
            
            # 7. 제조사/공급사 필터링
            if request.args.get('manufacturer_codes'):
                params['manufacturer_code'] = request.args.get('manufacturer_codes')
            if request.args.get('supplier_codes'):
                params['supplier_code'] = request.args.get('supplier_codes')
            
            # 8. 진열 상태 필터링
            if request.args.get('display'):
                params['display'] = request.args.get('display')  # T/F
            if request.args.get('selling'):
                params['selling'] = request.args.get('selling')  # T/F
            
            # 9. 카테고리 필터링
            if request.args.get('category_no'):
                params['category'] = request.args.get('category_no')
            
            # 10. 상품 코드로 검색 (쉼표로 구분)
            if request.args.get('product_codes'):
                params['product_code'] = request.args.get('product_codes')
            
            # 11. 검색어 (상품명)
            search_keyword = request.args.get('search')
            
            # 12. 멀티샵 설정
            if request.args.get('shop_no'):
                params['shop_no'] = request.args.get('shop_no')
            
            # API 호출
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                # 검색어 필터링 (API에서 직접 지원하지 않는 경우)
                if search_keyword:
                    search_lower = search_keyword.lower()
                    products = [p for p in products if search_lower in p.get('product_name', '').lower()]
                
                # 정렬 옵션 적용
                sort_by = request.args.get('sort_by', 'created_date')
                sort_order = request.args.get('sort_order', 'desc')
                
                if sort_by == 'price':
                    products.sort(key=lambda x: float(x.get('price', 0)), reverse=(sort_order == 'desc'))
                elif sort_by == 'name':
                    products.sort(key=lambda x: x.get('product_name', ''), reverse=(sort_order == 'desc'))
                elif sort_by == 'stock':
                    products.sort(key=lambda x: int(x.get('quantity', 0)), reverse=(sort_order == 'desc'))
                elif sort_by == 'created_date':
                    products.sort(key=lambda x: x.get('created_date', ''), reverse=(sort_order == 'desc'))
                elif sort_by == 'updated_date':
                    products.sort(key=lambda x: x.get('updated_date', ''), reverse=(sort_order == 'desc'))
                
                # 통계 정보 추가
                stats = {
                    'total_products': len(products),
                    'total_value': sum(float(p.get('price', 0)) * int(p.get('quantity', 0)) for p in products),
                    'out_of_stock': len([p for p in products if int(p.get('quantity', 0)) == 0]),
                    'low_stock': len([p for p in products if 0 < int(p.get('quantity', 0)) < 10]),
                    'displayed': len([p for p in products if p.get('display') == 'T']),
                    'hidden': len([p for p in products if p.get('display') == 'F'])
                }
                
                return jsonify({
                    'success': True,
                    'products': products,
                    'count': len(products),
                    'stats': stats,
                    'pagination': {
                        'offset': params['offset'],
                        'limit': params['limit'],
                        'has_more': len(products) == params['limit']
                    },
                    'filters_applied': {k: v for k, v in params.items() if k not in ['fields', 'limit', 'offset']}
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 오류: {response.status_code}',
                    'message': response.text
                }), response.status_code
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def search_products(self):
        """고급 검색 기능"""
        try:
            headers = self.get_headers()
            url = self._get_base_url()
            
            # 검색 쿼리
            query = request.json.get('query', '')
            filters = request.json.get('filters', {})
            
            # 검색 파라미터 구성
            params = {
                'limit': filters.get('limit', 100),
                'offset': filters.get('offset', 0),
                'fields': 'product_no,product_code,product_name,price,quantity,display,detail_image,brand_code,category'
            }
            
            # 필터 적용
            if filters.get('price_range'):
                params['price_min'] = filters['price_range'].get('min')
                params['price_max'] = filters['price_range'].get('max')
            
            if filters.get('categories'):
                params['category'] = ','.join(str(c) for c in filters['categories'])
            
            if filters.get('brands'):
                params['brand_code'] = ','.join(filters['brands'])
            
            if filters.get('in_stock_only'):
                params['quantity_min'] = 1
            
            # API 호출
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                # 텍스트 검색 (상품명, 코드, 태그)
                if query:
                    query_lower = query.lower()
                    filtered_products = []
                    for product in products:
                        if (query_lower in product.get('product_name', '').lower() or
                            query_lower in product.get('product_code', '').lower() or
                            query_lower in product.get('product_tag', '').lower()):
                            filtered_products.append(product)
                    products = filtered_products
                
                # 검색 결과 랭킹 (관련성 점수)
                if query:
                    for product in products:
                        score = 0
                        name_lower = product.get('product_name', '').lower()
                        
                        # 정확한 일치
                        if query_lower == name_lower:
                            score += 100
                        # 시작 부분 일치
                        elif name_lower.startswith(query_lower):
                            score += 50
                        # 포함
                        elif query_lower in name_lower:
                            score += 20
                        
                        product['relevance_score'] = score
                    
                    # 관련성 순으로 정렬
                    products.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
                
                return jsonify({
                    'success': True,
                    'query': query,
                    'results': products,
                    'count': len(products),
                    'filters_applied': filters
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 오류: {response.status_code}'
                }), response.status_code
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_product_variants(self, product_no):
        """상품 옵션/변형 조회"""
        try:
            headers = self.get_headers()
            url = f"https://{self.get_mall_id()}.cafe24api.com/api/v2/admin/products/{product_no}/variants"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return jsonify({
                    'success': True,
                    'product_no': product_no,
                    'variants': data.get('variants', [])
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 오류: {response.status_code}'
                }), response.status_code
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def bulk_update_products(self):
        """대량 상품 업데이트"""
        try:
            headers = self.get_headers()
            updates = request.json.get('updates', [])
            
            results = []
            success_count = 0
            failed_count = 0
            
            for update in updates:
                product_no = update.get('product_no')
                if not product_no:
                    continue
                
                url = f"https://{self.get_mall_id()}.cafe24api.com/api/v2/admin/products/{product_no}"
                
                # 업데이트 데이터 준비
                update_data = {}
                if 'price' in update:
                    update_data['price'] = str(update['price'])
                if 'quantity' in update:
                    update_data['quantity'] = str(update['quantity'])
                if 'display' in update:
                    update_data['display'] = update['display']
                if 'selling' in update:
                    update_data['selling'] = update['selling']
                
                response = requests.put(
                    url,
                    headers=headers,
                    json={'product': update_data}
                )
                
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
            
            return jsonify({
                'success': True,
                'total': len(updates),
                'success_count': success_count,
                'failed_count': failed_count,
                'results': results
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def export_products(self):
        """상품 데이터 내보내기"""
        try:
            format_type = request.args.get('format', 'excel')
            
            # 모든 상품 가져오기
            headers = self.get_headers()
            url = self._get_base_url()
            
            all_products = []
            offset = 0
            limit = 100
            
            while True:
                params = {
                    'limit': limit,
                    'offset': offset,
                    'fields': request.args.get('fields', 'product_no,product_code,product_name,price,quantity,display')
                }
                
                response = requests.get(url, headers=headers, params=params)
                if response.status_code != 200:
                    break
                
                data = response.json()
                products = data.get('products', [])
                if not products:
                    break
                
                all_products.extend(products)
                offset += limit
                
                if len(products) < limit:
                    break
            
            if format_type == 'excel':
                # Excel 파일 생성
                df = pd.DataFrame(all_products)
                
                # 한글 컬럼명 매핑
                column_mapping = {
                    'product_no': '상품번호',
                    'product_code': '상품코드',
                    'product_name': '상품명',
                    'price': '판매가',
                    'quantity': '재고수량',
                    'display': '진열상태',
                    'brand_code': '브랜드',
                    'created_date': '등록일'
                }
                
                df.rename(columns=column_mapping, inplace=True)
                
                # Excel 파일로 저장
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='상품목록', index=False)
                
                output.seek(0)
                
                return send_file(
                    output,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name=f'products_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
                )
                
            elif format_type == 'csv':
                # CSV 파일 생성
                df = pd.DataFrame(all_products)
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                
                output = io.BytesIO()
                output.write(csv_data.encode('utf-8-sig'))
                output.seek(0)
                
                return send_file(
                    output,
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=f'products_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                )
                
            else:  # JSON
                return jsonify({
                    'success': True,
                    'export_date': datetime.now().isoformat(),
                    'total_products': len(all_products),
                    'products': all_products
                })
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_product_images(self, product_no):
        """상품 이미지 관리"""
        try:
            headers = self.get_headers()
            url = f"https://{self.get_mall_id()}.cafe24api.com/api/v2/admin/products/{product_no}/images"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return jsonify({
                    'success': True,
                    'product_no': product_no,
                    'images': data.get('images', [])
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 오류: {response.status_code}'
                }), response.status_code
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_product_seo(self, product_no):
        """상품 SEO 메타데이터"""
        try:
            headers = self.get_headers()
            url = f"https://{self.get_mall_id()}.cafe24api.com/api/v2/admin/products/{product_no}/seo"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return jsonify({
                    'success': True,
                    'product_no': product_no,
                    'seo': data.get('seo', {})
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 오류: {response.status_code}'
                }), response.status_code
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def analyze_products(self):
        """상품 데이터 분석"""
        try:
            # 모든 상품 데이터 수집
            headers = self.get_headers()
            url = self._get_base_url()
            
            response = requests.get(url, headers=headers, params={'limit': 500})
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                # 분석 결과
                analysis = {
                    'total_products': len(products),
                    'total_inventory_value': 0,
                    'average_price': 0,
                    'price_distribution': {},
                    'stock_analysis': {
                        'total_stock': 0,
                        'out_of_stock': 0,
                        'low_stock': 0,
                        'well_stocked': 0
                    },
                    'category_breakdown': {},
                    'brand_breakdown': {},
                    'display_status': {
                        'displayed': 0,
                        'hidden': 0
                    },
                    'top_products_by_value': [],
                    'recommendations': []
                }
                
                # 데이터 분석
                total_price = 0
                price_ranges = {'0-10000': 0, '10000-50000': 0, '50000-100000': 0, '100000+': 0}
                
                for product in products:
                    price = float(product.get('price', 0))
                    quantity = int(product.get('quantity', 0))
                    
                    # 재고 가치
                    analysis['total_inventory_value'] += price * quantity
                    total_price += price
                    
                    # 가격 분포
                    if price < 10000:
                        price_ranges['0-10000'] += 1
                    elif price < 50000:
                        price_ranges['10000-50000'] += 1
                    elif price < 100000:
                        price_ranges['50000-100000'] += 1
                    else:
                        price_ranges['100000+'] += 1
                    
                    # 재고 분석
                    analysis['stock_analysis']['total_stock'] += quantity
                    if quantity == 0:
                        analysis['stock_analysis']['out_of_stock'] += 1
                    elif quantity < 10:
                        analysis['stock_analysis']['low_stock'] += 1
                    else:
                        analysis['stock_analysis']['well_stocked'] += 1
                    
                    # 진열 상태
                    if product.get('display') == 'T':
                        analysis['display_status']['displayed'] += 1
                    else:
                        analysis['display_status']['hidden'] += 1
                    
                    # 카테고리별 분석
                    categories = product.get('product_category', [])
                    for cat in categories:
                        cat_name = cat.get('category_name', 'Unknown')
                        if cat_name not in analysis['category_breakdown']:
                            analysis['category_breakdown'][cat_name] = 0
                        analysis['category_breakdown'][cat_name] += 1
                    
                    # 브랜드별 분석
                    brand = product.get('brand_code', 'No Brand')
                    if brand not in analysis['brand_breakdown']:
                        analysis['brand_breakdown'][brand] = 0
                    analysis['brand_breakdown'][brand] += 1
                
                # 평균 계산
                if len(products) > 0:
                    analysis['average_price'] = total_price / len(products)
                
                analysis['price_distribution'] = price_ranges
                
                # 재고 가치 상위 상품
                products_by_value = sorted(
                    products,
                    key=lambda x: float(x.get('price', 0)) * int(x.get('quantity', 0)),
                    reverse=True
                )[:10]
                
                analysis['top_products_by_value'] = [
                    {
                        'name': p['product_name'],
                        'value': float(p.get('price', 0)) * int(p.get('quantity', 0)),
                        'price': float(p.get('price', 0)),
                        'stock': int(p.get('quantity', 0))
                    }
                    for p in products_by_value
                ]
                
                # 추천사항 생성
                if analysis['stock_analysis']['out_of_stock'] > len(products) * 0.1:
                    analysis['recommendations'].append(
                        f"주의: 전체 상품의 {analysis['stock_analysis']['out_of_stock']/len(products)*100:.1f}%가 품절 상태입니다."
                    )
                
                if analysis['display_status']['hidden'] > len(products) * 0.3:
                    analysis['recommendations'].append(
                        f"많은 상품({analysis['display_status']['hidden']}개)이 미진열 상태입니다. 진열 상태를 검토하세요."
                    )
                
                return jsonify({
                    'success': True,
                    'analysis': analysis,
                    'generated_at': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 오류: {response.status_code}'
                }), response.status_code
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_all_products(self):
        """모든 상품 가져오기 (페이지네이션 자동 처리)"""
        try:
            headers = self.get_headers()
            url = self._get_base_url()
            
            all_products = []
            offset = 0
            limit = 100
            
            while True:
                params = {
                    'limit': limit,
                    'offset': offset,
                    'fields': 'product_no,product_code,product_name,price,quantity,display,created_date,brand_code'
                }
                
                response = requests.get(url, headers=headers, params=params)
                if response.status_code != 200:
                    break
                
                data = response.json()
                products = data.get('products', [])
                
                if not products:
                    break
                
                all_products.extend(products)
                offset += limit
                
                # 더 이상 상품이 없으면 중단
                if len(products) < limit:
                    break
                
                # 안전 장치: 최대 10000개까지만
                if len(all_products) >= 10000:
                    break
            
            # 통계 계산
            stats = {
                'total_products': len(all_products),
                'out_of_stock': len([p for p in all_products if int(p.get('quantity', 0)) == 0]),
                'low_stock': len([p for p in all_products if 0 < int(p.get('quantity', 0)) < 10]),
                'displayed': len([p for p in all_products if p.get('display') == 'T']),
                'hidden': len([p for p in all_products if p.get('display') == 'F'])
            }
            
            return jsonify({
                'success': True,
                'products': all_products,
                'count': len(all_products),
                'stats': stats,
                'message': f'전체 {len(all_products)}개 상품을 불러왔습니다.'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

# 블루프린트 라우트 설정
def register_routes(bp, api):
    """라우트 등록"""
    bp.add_url_rule('/advanced', 'get_products_advanced', api.get_products_advanced, methods=['GET'])
    bp.add_url_rule('/all', 'get_all_products', api.get_all_products, methods=['GET'])
    bp.add_url_rule('/search', 'search_products', api.search_products, methods=['POST'])
    bp.add_url_rule('/<int:product_no>/variants', 'get_product_variants', api.get_product_variants, methods=['GET'])
    bp.add_url_rule('/bulk-update', 'bulk_update_products', api.bulk_update_products, methods=['POST'])
    bp.add_url_rule('/export', 'export_products', api.export_products, methods=['GET'])
    bp.add_url_rule('/<int:product_no>/images', 'get_product_images', api.get_product_images, methods=['GET'])
    bp.add_url_rule('/<int:product_no>/seo', 'get_product_seo', api.get_product_seo, methods=['GET'])
    bp.add_url_rule('/analyze', 'analyze_products', api.analyze_products, methods=['GET'])