#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import io

# Windows에서 한글 출력을 위한 설정
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
    except:
        pass

"""
Cafe24 API 워스트셀러 분석 테스트 스크립트
Direct API 호출을 통한 상품 및 주문 데이터 분석

이 스크립트는 다음을 수행합니다:
1. Cafe24 API 인증 확인
2. 상품 데이터 조회 및 분석
3. 주문 데이터 조회 및 분석
4. 최근 7일간 판매량 0인 상품 식별
5. 워스트셀러 분석 가능성 검토
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import time

class Cafe24APITester:
    """Cafe24 API 테스터 클래스"""
    
    def __init__(self):
        """초기화"""
        self.cafe24_dir = os.path.dirname(os.path.abspath(__file__))
        self.oauth_token_file = os.path.join(self.cafe24_dir, 'oauth_token.json')
        self.env_file = os.path.join(self.cafe24_dir, 'config', '.env')
        
        # API 설정
        self.mall_id = None
        self.access_token = None
        self.client_id = None
        self.api_version = "2025-06-01"
        self.base_url = None
        
        # 결과 저장
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'authentication': {'success': False, 'method': None},
            'products_api': {'success': False, 'total_products': 0, 'sample_data': []},
            'orders_api': {'success': False, 'total_orders': 0, 'sample_data': []},
            'worst_sellers': {'feasible': False, 'zero_sales_products': [], 'analysis': ''},
            'recommendations': []
        }
        
        # 초기화
        self._load_credentials()
    
    def _load_credentials(self):
        """인증 정보 로드"""
        print("카페24 API 인증 정보 로드 중...")
        print("=" * 50)
        
        # OAuth 토큰 파일 확인
        if os.path.exists(self.oauth_token_file):
            try:
                with open(self.oauth_token_file, 'r', encoding='utf-8') as f:
                    token_data = json.load(f)
                
                self.access_token = token_data.get('access_token')
                self.mall_id = token_data.get('mall_id')
                self.client_id = token_data.get('client_id')
                
                if self.access_token and self.mall_id:
                    self.base_url = f"https://{self.mall_id}.cafe24api.com/api/v2"
                    self.test_results['authentication']['success'] = True
                    self.test_results['authentication']['method'] = 'OAuth Token'
                    
                    print(f"[성공] OAuth 토큰 로드 성공")
                    print(f"   쇼핑몰 ID: {self.mall_id}")
                    print(f"   API URL: {self.base_url}")
                    print(f"   토큰 만료시간: {token_data.get('expires_at', 'N/A')}")
                    return
                    
            except Exception as e:
                print(f"[오류] OAuth 토큰 로드 실패: {e}")
        
        # 환경 변수 파일 확인
        if os.path.exists(self.env_file):
            try:
                with open(self.env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            if key == 'CAFE24_MALL_ID':
                                self.mall_id = value
                            elif key == 'CAFE24_ACCESS_TOKEN':
                                self.access_token = value
                            elif key == 'CAFE24_CLIENT_ID':
                                self.client_id = value
                            elif key == 'CAFE24_API_VERSION':
                                self.api_version = value
                
                if self.access_token and self.mall_id:
                    self.base_url = f"https://{self.mall_id}.cafe24api.com/api/v2"
                    self.test_results['authentication']['success'] = True
                    self.test_results['authentication']['method'] = 'Environment File'
                    
                    print(f"[성공] 환경 변수 로드 성공")
                    print(f"   쇼핑몰 ID: {self.mall_id}")
                    print(f"   API URL: {self.base_url}")
                    return
                    
            except Exception as e:
                print(f"[오류] 환경 변수 로드 실패: {e}")
        
        print("[오류] 인증 정보를 찾을 수 없습니다!")
        print("   필요한 파일:")
        print(f"   - {self.oauth_token_file}")
        print(f"   - {self.env_file}")
        sys.exit(1)
    
    def _get_headers(self) -> Dict[str, str]:
        """API 요청 헤더 생성"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Cafe24-Api-Version': self.api_version
        }
    
    def _make_request(self, endpoint: str, params: Dict = None, method: str = 'GET') -> Optional[Dict]:
        """API 요청 수행"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            else:
                response = requests.post(url, headers=headers, json=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[오류] API 요청 실패: {response.status_code}")
                print(f"   URL: {url}")
                print(f"   응답: {response.text[:200]}...")
                return None
                
        except Exception as e:
            print(f"[오류] 요청 오류: {e}")
            return None
    
    def test_products_api(self):
        """상품 API 테스트"""
        print("\n상품 API 테스트")
        print("-" * 30)
        
        # 상품 데이터 가져오기
        params = {'limit': 50, 'offset': 0, 'embed': 'variants,discountprice'}
        result = self._make_request('/admin/products', params)
        
        if not result:
            print("[오류] 상품 API 연결 실패")
            return
        
        products = result.get('products', [])
        self.test_results['products_api']['success'] = True
        self.test_results['products_api']['total_products'] = len(products)
        
        print(f"[성공] 상품 API 연결 성공")
        print(f"조회된 상품 수: {len(products)}개")
        print("\n상품 데이터 샘플:")
        
        for i, product in enumerate(products[:5], 1):
            product_info = {
                'product_no': product.get('product_no'),
                'product_name': product.get('product_name'),
                'product_code': product.get('product_code'),
                'price': product.get('price'),
                'retail_price': product.get('retail_price'),
                'supply_price': product.get('supply_price'),
                'display': product.get('display'),
                'selling': product.get('selling'),
                'quantity': product.get('quantity'),
                'created_date': product.get('created_date'),
                'updated_date': product.get('updated_date')
            }
            
            self.test_results['products_api']['sample_data'].append(product_info)
            
            print(f"\n   {i}. {product.get('product_name', 'N/A')}")
            print(f"      상품번호: {product.get('product_no', 'N/A')}")
            print(f"      상품코드: {product.get('product_code', 'N/A')}")
            print(f"      판매가: {product.get('price', 'N/A')}원")
            print(f"      재고: {product.get('quantity', 'N/A')}개")
            print(f"      진열상태: {product.get('display', 'N/A')}")
            print(f"      판매상태: {product.get('selling', 'N/A')}")
        
        # 사용 가능한 필드 분석
        if products:
            available_fields = set()
            for product in products:
                available_fields.update(product.keys())
            
            print(f"\n상품 데이터 사용 가능한 필드 ({len(available_fields)}개):")
            sorted_fields = sorted(available_fields)
            for i, field in enumerate(sorted_fields):
                if i % 4 == 0:
                    print("\n   ", end="")
                print(f"{field:<20}", end="")
            print()
    
    def test_orders_api(self):
        """주문 API 테스트"""
        print("\n주문 API 테스트")
        print("-" * 30)
        
        # 최근 7일간 주문 데이터 조회
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        params = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'limit': 100,
            'embed': 'items'
        }
        
        print(f"조회 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        
        result = self._make_request('/admin/orders', params)
        
        if not result:
            print("[오류] 주문 API 연결 실패")
            return {}
        
        orders = result.get('orders', [])
        self.test_results['orders_api']['success'] = True
        self.test_results['orders_api']['total_orders'] = len(orders)
        
        print(f"[성공] 주문 API 연결 성공")
        print(f"최근 7일간 주문 수: {len(orders)}개")
        
        # 상품별 판매 집계
        product_sales = defaultdict(int)
        
        if orders:
            print("\n주문 데이터 샘플:")
            
            for i, order in enumerate(orders[:5], 1):
                order_info = {
                    'order_id': order.get('order_id'),
                    'order_date': order.get('order_date'),
                    'buyer_name': order.get('buyer_name'),
                    'order_amount': order.get('order_amount'),
                    'order_status': order.get('order_status'),
                    'items': []
                }
                
                print(f"\n   {i}. 주문번호: {order.get('order_id', 'N/A')}")
                print(f"      주문일시: {order.get('order_date', 'N/A')}")
                print(f"      고객명: {order.get('buyer_name', 'N/A')}")
                print(f"      주문금액: {order.get('order_amount', 'N/A')}원")
                print(f"      주문상태: {order.get('order_status', 'N/A')}")
                
                # 주문 상품 정보
                items = order.get('items', [])
                if items:
                    print(f"      주문상품 ({len(items)}개):")
                    for item in items:
                        product_no = item.get('product_no')
                        quantity = int(item.get('quantity', 0))
                        product_sales[product_no] += quantity
                        
                        item_info = {
                            'product_no': product_no,
                            'product_name': item.get('product_name'),
                            'quantity': quantity,
                            'product_price': item.get('product_price')
                        }
                        order_info['items'].append(item_info)
                        
                        print(f"         - {item.get('product_name', 'N/A')} x {quantity}개")
                
                self.test_results['orders_api']['sample_data'].append(order_info)
            
            # 모든 주문의 상품별 판매량 집계
            for order in orders:
                items = order.get('items', [])
                for item in items:
                    product_no = item.get('product_no')
                    quantity = int(item.get('quantity', 0))
                    product_sales[product_no] += quantity
            
            print(f"\n최근 7일간 상품별 판매량 집계:")
            print(f"   총 {len(product_sales)}개 상품이 판매됨")
            
            # 판매량 상위 5개 상품
            top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
            if top_products:
                print("\n   판매량 상위 5개 상품:")
                for product_no, quantity in top_products:
                    print(f"      상품번호 {product_no}: {quantity}개 판매")
        
        return product_sales
    
    def analyze_worst_sellers(self, product_sales: Dict):
        """워스트셀러 분석"""
        print("\n워스트셀러 분석")
        print("-" * 30)
        
        # 전체 상품 목록 가져오기
        all_products = []
        offset = 0
        limit = 100
        
        print("전체 상품 데이터 수집 중...")
        
        while True:
            params = {'limit': limit, 'offset': offset}
            result = self._make_request('/admin/products', params)
            
            if not result or 'products' not in result:
                break
            
            products = result['products']
            if not products:
                break
            
            all_products.extend(products)
            offset += limit
            
            print(f"   수집된 상품: {len(all_products)}개", end='\r')
            
            # API 호출 제한 고려
            time.sleep(0.1)
            
            if len(products) < limit:
                break
        
        print(f"\n[성공] 전체 상품 수집 완료: {len(all_products)}개")
        
        # 판매량 0인 상품 찾기
        zero_sales_products = []
        
        for product in all_products:
            product_no = product.get('product_no')
            product_name = product.get('product_name', 'N/A')
            
            # 최근 7일간 판매량이 0인 상품
            if product_no not in product_sales:
                zero_sales_info = {
                    'product_no': product_no,
                    'product_name': product_name,
                    'product_code': product.get('product_code'),
                    'price': product.get('price'),
                    'quantity': product.get('quantity'),
                    'display': product.get('display'),
                    'selling': product.get('selling'),
                    'created_date': product.get('created_date'),
                    'sales_last_7_days': 0
                }
                zero_sales_products.append(zero_sales_info)
        
        self.test_results['worst_sellers']['zero_sales_products'] = zero_sales_products
        
        print(f"\n워스트셀러 분석 결과:")
        print(f"   전체 상품 수: {len(all_products)}개")
        print(f"   최근 7일간 판매된 상품: {len(product_sales)}개")
        print(f"   최근 7일간 판매량 0인 상품: {len(zero_sales_products)}개")
        
        if zero_sales_products:
            print(f"\n판매량 0인 상품 샘플 (상위 10개):")
            
            for i, product in enumerate(zero_sales_products[:10], 1):
                print(f"   {i}. {product['product_name']}")
                print(f"      상품번호: {product['product_no']}")
                print(f"      판매가: {product['price']}원")
                print(f"      재고: {product['quantity']}개")
                print(f"      진열: {product['display']}, 판매: {product['selling']}")
                print()
        
        # 분석 가능성 평가
        feasible = len(all_products) > 0 and len(zero_sales_products) >= 0
        self.test_results['worst_sellers']['feasible'] = feasible
        
        if feasible:
            analysis = f"""
워스트셀러 분석이 가능합니다!

분석 가능한 데이터:
- 전체 상품 정보: {len(all_products)}개
- 주문 데이터: 최근 7일간 주문 {self.test_results['orders_api']['total_orders']}건
- 판매량 0인 상품: {len(zero_sales_products)}개

분석 기능:
- 기간별 판매량 0인 상품 식별
- 상품별 판매 실적 추적
- 재고 현황과 판매 실적 비교
- 진열/판매 상태별 분석
"""
        else:
            analysis = "데이터 부족으로 워스트셀러 분석이 어려울 수 있습니다."
        
        self.test_results['worst_sellers']['analysis'] = analysis
        print(analysis)
    
    def generate_recommendations(self):
        """개선 권장사항 생성"""
        print("\n워스트셀러 분석 시스템 구축 권장사항")
        print("-" * 50)
        
        recommendations = []
        
        if self.test_results['products_api']['success']:
            recommendations.append("[성공] 상품 API: 정상 작동 - 상품 정보 수집 가능")
        else:
            recommendations.append("[오류] 상품 API: 문제 발생 - API 인증 확인 필요")
        
        if self.test_results['orders_api']['success']:
            recommendations.append("[성공] 주문 API: 정상 작동 - 판매 데이터 수집 가능")
        else:
            recommendations.append("[오류] 주문 API: 문제 발생 - API 권한 확인 필요")
        
        if self.test_results['worst_sellers']['feasible']:
            recommendations.extend([
                "\n워스트셀러 분석 시스템 구축 권장사항:",
                "   1. 일별/주별/월별 판매 데이터 수집 자동화",
                "   2. 상품별 판매 실적 데이터베이스 구축",
                "   3. 재고 현황과 판매 실적 연동 분석",
                "   4. 대시보드를 통한 시각화",
                "   5. 알림 시스템 (일정 기간 판매량 0인 상품)",
                "   6. 할인/프로모션 대상 상품 자동 추천"
            ])
        
        recommendations.extend([
            "\n기술적 개선사항:",
            "   - API 호출 최적화 (캐싱, 배치 처리)",
            "   - 데이터 저장소 구축 (SQLite, PostgreSQL 등)",
            "   - 스케줄러를 통한 정기 데이터 수집",
            "   - 웹 대시보드 개발 (Flask, Django 등)"
        ])
        
        self.test_results['recommendations'] = recommendations
        
        for rec in recommendations:
            print(rec)
    
    def save_results(self):
        """테스트 결과 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"worst_sellers_test_results_{timestamp}.json"
        filepath = os.path.join(self.cafe24_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            
            print(f"\n테스트 결과 저장: {filename}")
            return filepath
        except Exception as e:
            print(f"[오류] 결과 저장 실패: {e}")
            return None
    
    def run_full_test(self):
        """전체 테스트 실행"""
        print("Cafe24 API 워스트셀러 분석 테스트 시작")
        print("=" * 60)
        
        if not self.test_results['authentication']['success']:
            print("[오류] 인증 실패로 테스트를 중단합니다.")
            return
        
        # 1. 상품 API 테스트
        self.test_products_api()
        
        # 2. 주문 API 테스트
        product_sales = self.test_orders_api()
        
        # 3. 워스트셀러 분석
        self.analyze_worst_sellers(product_sales)
        
        # 4. 권장사항 생성
        self.generate_recommendations()
        
        # 5. 결과 저장
        result_file = self.save_results()
        
        print("\n" + "=" * 60)
        print("워스트셀러 분석 테스트 완료!")
        print("=" * 60)
        
        # 최종 요약
        print("\n테스트 결과 요약:")
        print(f"   인증: {'[성공]' if self.test_results['authentication']['success'] else '[실패]'}")
        print(f"   상품 API: {'[성공]' if self.test_results['products_api']['success'] else '[실패]'}")
        print(f"   주문 API: {'[성공]' if self.test_results['orders_api']['success'] else '[실패]'}")
        print(f"   워스트셀러 분석: {'[가능]' if self.test_results['worst_sellers']['feasible'] else '[불가능]'}")
        
        if result_file:
            print(f"\n상세 결과: {os.path.basename(result_file)}")


def main():
    """메인 함수"""
    try:
        tester = Cafe24APITester()
        tester.run_full_test()
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n[오류] 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()