#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 CSV 템플릿 호환 Import/Export 기능 구현
manwonyori_20250805_201_f879_producr_template.csv 형식 지원
"""
from flask import Blueprint, request, jsonify, send_file
import pandas as pd
import requests
import json
import io
from datetime import datetime

csv_bp = Blueprint('csv', __name__)

class CSVProductManager:
    def __init__(self, get_headers, get_mall_id):
        self.get_headers = get_headers
        self.get_mall_id = get_mall_id
        
        # Cafe24 CSV 필드 → API 필드 매핑
        self.field_mapping = {
            '상품코드': 'product_code',
            '자체 상품코드': 'custom_product_code',
            '진열상태': 'display',
            '판매상태': 'selling',
            '상품명': 'product_name',
            '영문 상품명': 'product_name_en',
            '모델명': 'model_name',
            '상품 요약설명': 'summary_description',
            '과세구분': 'tax_type',
            '소비자가': 'retail_price',
            '공급가': 'supply_price',
            '판매가': 'price',
            '브랜드': 'brand_code',
            '제조사': 'manufacturer_code',
            '공급사': 'supplier_code',
            '원산지': 'made_in_code',
            '상품중량(kg)': 'weight',
            '검색어설정': 'product_tag',
            '네이버페이 사용': 'use_naverpay'
        }
        
        # 값 변환 규칙
        self.value_converters = {
            'display': lambda x: 'T' if x == 'Y' else 'F',
            'selling': lambda x: 'T' if x == 'Y' else 'F',
            'tax_type': lambda x: x.split('|')[0] if '|' in x else x,
            'price': lambda x: str(int(float(x))),
            'supply_price': lambda x: str(int(float(x))),
            'retail_price': lambda x: str(int(float(x)))
        }
    
    def export_to_cafe24_csv(self):
        """현재 상품을 Cafe24 CSV 형식으로 내보내기"""
        try:
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            # 모든 상품 가져오기
            all_products = []
            offset = 0
            limit = 100
            
            while True:
                url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
                params = {
                    'limit': limit,
                    'offset': offset,
                    'fields': ','.join([
                        'product_no', 'product_code', 'custom_product_code',
                        'product_name', 'price', 'supply_price', 'retail_price',
                        'display', 'selling', 'quantity', 'brand_code',
                        'manufacturer_code', 'supplier_code', 'made_in_code',
                        'model_name', 'summary_description', 'product_tag',
                        'tax_type', 'weight', 'use_naverpay'
                    ])
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
            
            # Cafe24 CSV 템플릿 읽기
            template_path = "static/excel_templates/manwonyori_20250805_201_f879_producr_template.csv"
            template_df = pd.read_csv(template_path, encoding='utf-8-sig', nrows=0)
            
            # 빈 데이터프레임 생성 (템플릿 구조 유지)
            export_df = pd.DataFrame(columns=template_df.columns)
            
            # API 데이터를 CSV 형식으로 변환
            for product in all_products:
                row_data = {}
                
                # 기본값 설정
                for col in template_df.columns:
                    row_data[col] = ''
                
                # API → CSV 필드 매핑
                row_data['상품코드'] = product.get('product_code', '')
                row_data['자체 상품코드'] = product.get('custom_product_code', '')
                row_data['진열상태'] = 'Y' if product.get('display') == 'T' else 'N'
                row_data['판매상태'] = 'Y' if product.get('selling') == 'T' else 'N'
                row_data['상품명'] = product.get('product_name', '')
                row_data['모델명'] = product.get('model_name', '')
                row_data['상품 요약설명'] = product.get('summary_description', '')
                row_data['과세구분'] = f"{product.get('tax_type', 'A')}|10"
                row_data['소비자가'] = str(float(product.get('retail_price', 0)))
                row_data['공급가'] = str(float(product.get('supply_price', 0)))
                row_data['판매가'] = str(float(product.get('price', 0)))
                row_data['검색어설정'] = product.get('product_tag', '')
                row_data['브랜드'] = product.get('brand_code', '')
                row_data['제조사'] = product.get('manufacturer_code', '')
                row_data['공급사'] = product.get('supplier_code', '')
                row_data['원산지'] = product.get('made_in_code', '')
                
                # 기본값 설정
                row_data['옵션사용'] = 'N'
                row_data['배송정보'] = 'F'
                row_data['배송비 구분'] = '3|7'
                
                export_df = pd.concat([export_df, pd.DataFrame([row_data])], ignore_index=True)
            
            # CSV 파일 생성
            output = io.StringIO()
            export_df.to_csv(output, index=False, encoding='utf-8-sig')
            output.seek(0)
            
            # 바이트로 변환
            output_bytes = io.BytesIO()
            output_bytes.write(output.getvalue().encode('utf-8-sig'))
            output_bytes.seek(0)
            
            return send_file(
                output_bytes,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'cafe24_products_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def import_from_cafe24_csv(self):
        """Cafe24 CSV 형식 파일 업로드 및 상품 등록/수정"""
        try:
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': '파일이 없습니다'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': '파일이 선택되지 않았습니다'}), 400
            
            # CSV 파일 읽기
            df = pd.read_csv(file, encoding='utf-8-sig')
            
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            results = {
                'total': len(df),
                'created': 0,
                'updated': 0,
                'failed': 0,
                'errors': []
            }
            
            for idx, row in df.iterrows():
                try:
                    # API 데이터 준비
                    api_data = {}
                    
                    # 필드 매핑 및 변환
                    for csv_field, api_field in self.field_mapping.items():
                        if csv_field in row and pd.notna(row[csv_field]):
                            value = row[csv_field]
                            
                            # 값 변환
                            if api_field in self.value_converters:
                                value = self.value_converters[api_field](value)
                            
                            api_data[api_field] = value
                    
                    # 상품코드 확인
                    product_code = row.get('상품코드', '')
                    
                    if product_code and product_code.startswith('P'):
                        # 기존 상품 수정
                        product_no = product_code  # 상품번호 추출 필요
                        url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{product_no}"
                        
                        response = requests.put(
                            url,
                            headers=headers,
                            json={'product': api_data}
                        )
                        
                        if response.status_code == 200:
                            results['updated'] += 1
                        else:
                            results['failed'] += 1
                            results['errors'].append({
                                'row': idx + 2,
                                'product_code': product_code,
                                'error': response.text
                            })
                    else:
                        # 신규 상품 등록
                        url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
                        
                        # 필수 필드 확인
                        if 'product_name' not in api_data or 'price' not in api_data:
                            results['failed'] += 1
                            results['errors'].append({
                                'row': idx + 2,
                                'error': '필수 필드 누락 (상품명, 판매가)'
                            })
                            continue
                        
                        response = requests.post(
                            url,
                            headers=headers,
                            json={'product': api_data}
                        )
                        
                        if response.status_code == 201:
                            results['created'] += 1
                        else:
                            results['failed'] += 1
                            results['errors'].append({
                                'row': idx + 2,
                                'product_name': api_data.get('product_name'),
                                'error': response.text
                            })
                    
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({
                        'row': idx + 2,
                        'error': str(e)
                    })
            
            return jsonify({
                'success': True,
                'results': results
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def get_template(self):
        """Cafe24 CSV 템플릿 다운로드"""
        try:
            template_path = "static/excel_templates/manwonyori_20250805_201_f879_producr_template.csv"
            
            # 템플릿에서 헤더만 가져오기
            template_df = pd.read_csv(template_path, encoding='utf-8-sig', nrows=0)
            
            # 샘플 데이터 추가
            sample_data = {
                '상품코드': '',  # 비워두면 자동생성
                '자체 상품코드': 'SAMPLE001',
                '진열상태': 'Y',
                '판매상태': 'Y',
                '상품명': '[샘플]테스트상품',
                '판매가': '10000',
                '공급가': '7000',
                '과세구분': 'A|10',
                '옵션사용': 'N',
                '배송정보': 'F'
            }
            
            # 나머지 컬럼은 빈 값
            for col in template_df.columns:
                if col not in sample_data:
                    sample_data[col] = ''
            
            # 데이터프레임 생성
            df = pd.DataFrame([sample_data], columns=template_df.columns)
            
            # CSV 파일 생성
            output = io.StringIO()
            df.to_csv(output, index=False, encoding='utf-8-sig')
            output.seek(0)
            
            output_bytes = io.BytesIO()
            output_bytes.write(output.getvalue().encode('utf-8-sig'))
            output_bytes.seek(0)
            
            return send_file(
                output_bytes,
                mimetype='text/csv',
                as_attachment=True,
                download_name='cafe24_product_upload_template.csv'
            )
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

# 라우트 등록
def register_csv_routes(bp, manager):
    """CSV Import/Export 라우트 등록"""
    bp.add_url_rule('/export', 'export_to_cafe24_csv', manager.export_to_cafe24_csv, methods=['GET'])
    bp.add_url_rule('/import', 'import_from_cafe24_csv', manager.import_from_cafe24_csv, methods=['POST'])
    bp.add_url_rule('/template', 'get_template', manager.get_template, methods=['GET'])