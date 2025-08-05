#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
마진 대시보드 가격 수정 및 CSV Export 기능 개선
"""
from flask import Blueprint, request, jsonify, send_file
import pandas as pd
import requests
import io
from datetime import datetime
from csv_folder_structure import CSVFolderManager

margin_export_bp = Blueprint('margin_export', __name__)

class MarginExportManager:
    def __init__(self, get_headers, get_mall_id):
        self.get_headers = get_headers
        self.get_mall_id = get_mall_id
        self.csv_manager = CSVFolderManager("csv_files")
    
    def update_single_product_margin(self):
        """단일 상품 마진율 기준 가격 수정"""
        try:
            data = request.json
            product_no = data.get('product_no')
            target_margin = data.get('target_margin')
            update_type = data.get('update_type', 'selling')
            
            if not product_no or target_margin is None:
                return jsonify({'success': False, 'error': '필수 파라미터 누락'}), 400
            
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            # 현재 상품 정보 조회
            url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{product_no}"
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return jsonify({'success': False, 'error': '상품 정보 조회 실패'}), 500
            
            product_data = response.json().get('product', {})
            current_selling_price = float(product_data.get('price', 0))
            current_supply_price = float(product_data.get('supply_price', 0))
            
            # 새 가격 계산
            if update_type == 'selling':
                new_selling_price = current_supply_price * (1 + target_margin / 100)
                new_selling_price = round(new_selling_price, -2)  # 100원 단위
                
                update_data = {
                    'product': {
                        'price': str(int(new_selling_price))
                    }
                }
            else:
                new_supply_price = current_selling_price / (1 + target_margin / 100)
                new_supply_price = round(new_supply_price, -2)
                
                update_data = {
                    'product': {
                        'supply_price': str(int(new_supply_price))
                    }
                }
            
            # 가격 업데이트
            response = requests.put(url, headers=headers, json=update_data)
            
            if response.status_code == 200:
                return jsonify({
                    'success': True,
                    'product_no': product_no,
                    'product_name': product_data.get('product_name'),
                    'old_price': current_selling_price if update_type == 'selling' else current_supply_price,
                    'new_price': new_selling_price if update_type == 'selling' else new_supply_price,
                    'margin_rate': target_margin
                })
            else:
                return jsonify({
                    'success': False,
                    'error': response.text
                }), 500
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def export_margin_updated_products(self):
        """마진율 수정된 상품들을 Cafe24 CSV 형식으로 Export"""
        try:
            data = request.json
            product_nos = data.get('product_nos', [])
            target_margin = data.get('target_margin')
            update_type = data.get('update_type', 'selling')
            
            if not product_nos:
                return jsonify({'success': False, 'error': '상품이 선택되지 않았습니다'}), 400
            
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            # Cafe24 CSV 템플릿 읽기
            template_path = "static/excel_templates/manwonyori_20250805_201_f879_producr_template.csv"
            template_df = pd.read_csv(template_path, encoding='utf-8-sig', nrows=0)
            
            # 빈 데이터프레임 생성
            export_df = pd.DataFrame(columns=template_df.columns)
            
            # 각 상품 정보 조회 및 새 가격 계산
            for product_no in product_nos:
                try:
                    # 상품 정보 조회
                    url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{product_no}"
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code != 200:
                        continue
                    
                    product = response.json().get('product', {})
                    
                    # 가격 계산
                    current_selling_price = float(product.get('price', 0))
                    current_supply_price = float(product.get('supply_price', 0))
                    
                    if update_type == 'selling' and current_supply_price > 0:
                        new_selling_price = current_supply_price * (1 + target_margin / 100)
                        new_selling_price = round(new_selling_price, -2)
                        selling_price = new_selling_price
                        supply_price = current_supply_price
                    elif update_type == 'supply' and current_selling_price > 0:
                        new_supply_price = current_selling_price / (1 + target_margin / 100)
                        new_supply_price = round(new_supply_price, -2)
                        selling_price = current_selling_price
                        supply_price = new_supply_price
                    else:
                        selling_price = current_selling_price
                        supply_price = current_supply_price
                    
                    # CSV 행 데이터 생성
                    row_data = {}
                    for col in template_df.columns:
                        row_data[col] = ''
                    
                    # 필드 매핑
                    row_data['상품코드'] = product.get('product_code', '')
                    row_data['자체 상품코드'] = product.get('custom_product_code', '')
                    row_data['진열상태'] = 'Y' if product.get('display') == 'T' else 'N'
                    row_data['판매상태'] = 'Y' if product.get('selling') == 'T' else 'N'
                    row_data['상품명'] = product.get('product_name', '')
                    row_data['모델명'] = product.get('model_name', '')
                    row_data['상품 요약설명'] = product.get('summary_description', '')
                    row_data['과세구분'] = f"{product.get('tax_type', 'A')}|10"
                    row_data['소비자가'] = str(float(product.get('retail_price', 0)))
                    row_data['공급가'] = str(supply_price)
                    row_data['판매가'] = str(selling_price)
                    row_data['상품가'] = str(selling_price)  # 상품가도 판매가와 동일하게
                    row_data['검색어설정'] = product.get('product_tag', '')
                    row_data['브랜드'] = product.get('brand_code', 'B0000000')
                    row_data['제조사'] = product.get('manufacturer_code', 'M000000U')
                    row_data['공급사'] = product.get('supplier_code', 'S000000T')
                    row_data['원산지'] = product.get('made_in_code', '1798')
                    
                    # 기본값 설정
                    row_data['옵션사용'] = 'N'
                    row_data['배송정보'] = 'F'
                    row_data['배송비 구분'] = '3|7'
                    row_data['배송방법'] = ''
                    row_data['국내/해외배송'] = 'A'
                    
                    export_df = pd.concat([export_df, pd.DataFrame([row_data])], ignore_index=True)
                    
                except Exception as e:
                    continue
            
            # CSV 파일 생성
            output = io.StringIO()
            export_df.to_csv(output, index=False, encoding='utf-8-sig')
            output.seek(0)
            
            # 바이트로 변환
            output_bytes = io.BytesIO()
            output_bytes.write(output.getvalue().encode('utf-8-sig'))
            output_bytes.seek(0)
            
            # 폴더 구조에 저장
            filename = f'margin_update_{target_margin}pct_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            filepath = self.csv_manager.save_download_file(
                file_type="products",
                filename=filename,
                content=output_bytes.getvalue()
            )
            
            return send_file(
                output_bytes,
                mimetype='text/csv',
                as_attachment=True,
                download_name=filename
            )
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def preview_margin_changes(self):
        """마진율 변경 미리보기"""
        try:
            data = request.json
            product_nos = data.get('product_nos', [])
            target_margin = data.get('target_margin')
            update_type = data.get('update_type', 'selling')
            
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            preview_results = []
            
            for product_no in product_nos[:10]:  # 최대 10개만 미리보기
                try:
                    url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{product_no}"
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        product = response.json().get('product', {})
                        
                        current_selling = float(product.get('price', 0))
                        current_supply = float(product.get('supply_price', 0))
                        
                        if update_type == 'selling' and current_supply > 0:
                            new_price = current_supply * (1 + target_margin / 100)
                            new_price = round(new_price, -2)
                            change_amount = new_price - current_selling
                            change_percent = (change_amount / current_selling * 100) if current_selling > 0 else 0
                        else:
                            new_price = current_selling / (1 + target_margin / 100)
                            new_price = round(new_price, -2)
                            change_amount = new_price - current_supply
                            change_percent = (change_amount / current_supply * 100) if current_supply > 0 else 0
                        
                        preview_results.append({
                            'product_no': product_no,
                            'product_name': product.get('product_name'),
                            'current_price': current_selling if update_type == 'selling' else current_supply,
                            'new_price': new_price,
                            'change_amount': change_amount,
                            'change_percent': round(change_percent, 1)
                        })
                        
                except Exception as e:
                    continue
            
            return jsonify({
                'success': True,
                'preview': preview_results,
                'total_count': len(product_nos),
                'preview_count': len(preview_results)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

# 라우트 등록
def register_margin_export_routes(bp, manager):
    """마진 Export 라우트 등록"""
    bp.add_url_rule('/update-single', 'update_single_product_margin', 
                    manager.update_single_product_margin, methods=['POST'])
    bp.add_url_rule('/export-updated', 'export_margin_updated_products', 
                    manager.export_margin_updated_products, methods=['POST'])
    bp.add_url_rule('/preview-changes', 'preview_margin_changes', 
                    manager.preview_margin_changes, methods=['POST'])