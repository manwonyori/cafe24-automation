#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카페24 API 종합 진단 스크립트
모든 API 연결과 데이터 흐름을 단계별로 테스트하여 문제점을 찾아냅니다.
"""
import os
import sys
import json
import requests
import time
from datetime import datetime, timedelta
import pytz
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_test.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class Cafe24APITester:
    """카페24 API 종합 테스터"""
    
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now(KST)
        self.mall_id = None
        self.headers = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test_result(self, test_name: str, success: bool, message: str, data: Any = None):
        """테스트 결과 로깅"""
        self.total_tests += 1
        
        if success:
            self.passed_tests += 1
            status = "[성공]"
            logger.info(f"{status} | {test_name}: {message}")
        else:
            self.failed_tests += 1
            status = "[실패]"
            logger.error(f"{status} | {test_name}: {message}")
        
        self.results[test_name] = {
            'success': success,
            'message': message,
            'data': data,
            'timestamp': datetime.now(KST).isoformat()
        }
        
        print(f"\n{status} | {test_name}")
        print(f"결과: {message}")
        if data:
            print(f"데이터: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
        print("-" * 80)
    
    def test_environment_variables(self):
        """1. 환경변수 확인"""
        print("\n[1단계] 환경변수 테스트")
        print("=" * 80)
        
        env_vars = {
            'CAFE24_CLIENT_ID': os.environ.get('CAFE24_CLIENT_ID'),
            'CAFE24_CLIENT_SECRET': os.environ.get('CAFE24_CLIENT_SECRET'),
            'CAFE24_ACCESS_TOKEN': os.environ.get('CAFE24_ACCESS_TOKEN'),
            'CAFE24_MALL_ID': os.environ.get('CAFE24_MALL_ID'),
            'CAFE24_REDIRECT_URI': os.environ.get('CAFE24_REDIRECT_URI')
        }
        
        found_vars = {k: v for k, v in env_vars.items() if v is not None}
        missing_vars = [k for k, v in env_vars.items() if v is None]
        
        self.log_test_result(
            "환경변수_확인",
            len(found_vars) > 0,
            f"환경변수 {len(found_vars)}개 발견, {len(missing_vars)}개 누락",
            {
                'found': list(found_vars.keys()),
                'missing': missing_vars,
                'values': {k: f"***{v[-4:]}" if v else None for k, v in env_vars.items()}
            }
        )
        
        return found_vars
    
    def test_token_files(self):
        """2. 토큰 파일 확인"""
        print("\n[2단계] 토큰 파일 테스트")
        print("=" * 80)
        
        token_files = [
            'oauth_token.json',
            'config/oauth_token.json',
            '../oauth_token.json'
        ]
        
        token_data = None
        found_file = None
        
        for token_file in token_files:
            if os.path.exists(token_file):
                try:
                    with open(token_file, 'r', encoding='utf-8') as f:
                        token_data = json.load(f)
                    found_file = token_file
                    break
                except Exception as e:
                    self.log_test_result(
                        f"토큰파일_읽기_{token_file}",
                        False,
                        f"파일 읽기 실패: {str(e)}"
                    )
        
        if token_data and found_file:
            # 토큰 만료 시간 확인
            expires_at = token_data.get('expires_at', '')
            if expires_at:
                try:
                    # 다양한 시간 형식 시도
                    for fmt in ['%Y-%m-%dT%H:%M:%S.%f.%f', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S']:
                        try:
                            expire_time = datetime.strptime(expires_at.split('.000')[0], fmt)
                            break
                        except:
                            continue
                    else:
                        expire_time = datetime.now() - timedelta(hours=1)
                    
                    time_remaining = expire_time - datetime.now()
                    is_valid = time_remaining.total_seconds() > 0
                    
                    self.log_test_result(
                        "토큰파일_유효성",
                        is_valid,
                        f"토큰 만료까지 {time_remaining} 남음" if is_valid else "토큰이 만료되었습니다",
                        {
                            'file': found_file,
                            'mall_id': token_data.get('mall_id'),
                            'client_id': token_data.get('client_id'),
                            'expires_at': expires_at,
                            'scopes': token_data.get('scopes', [])
                        }
                    )
                    
                except Exception as e:
                    self.log_test_result(
                        "토큰파일_시간분석",
                        False,
                        f"시간 파싱 실패: {str(e)}"
                    )
        else:
            self.log_test_result(
                "토큰파일_검색",
                False,
                f"토큰 파일을 찾을 수 없습니다. 검색한 위치: {token_files}"
            )
        
        return token_data
    
    def get_access_credentials(self):
        """3. 접근 인증 정보 수집"""
        print("\n[3단계] 인증 정보 수집")
        print("=" * 80)
        
        # 환경변수에서 토큰 시도
        access_token = os.environ.get('CAFE24_ACCESS_TOKEN')
        mall_id = os.environ.get('CAFE24_MALL_ID')
        
        # 토큰 파일에서 시도
        token_data = self.test_token_files()
        if token_data:
            if not access_token:
                access_token = token_data.get('access_token')
            if not mall_id:
                mall_id = token_data.get('mall_id')
        
        # config.py에서 기본값 시도
        try:
            from config import DEFAULT_MALL_ID, CAFE24_API_VERSION
            if not mall_id:
                mall_id = DEFAULT_MALL_ID
        except ImportError:
            pass
        
        if not mall_id:
            mall_id = 'manwonyori'  # 하드코딩된 기본값
        
        self.mall_id = mall_id
        
        if access_token:
            self.headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'X-Cafe24-Api-Version': '2025-06-01'
            }
            
            self.log_test_result(
                "인증정보_수집",
                True,
                f"Mall ID: {mall_id}, Token: ***{access_token[-10:]}",
                {
                    'mall_id': mall_id,
                    'token_length': len(access_token),
                    'headers_set': True
                }
            )
        else:
            self.log_test_result(
                "인증정보_수집",
                False,
                "액세스 토큰을 찾을 수 없습니다"
            )
        
        return access_token, mall_id
    
    def test_basic_authentication(self):
        """4. 기본 인증 테스트"""
        print("\n[4단계] 기본 인증 테스트")
        print("=" * 80)
        
        if not self.headers or not self.mall_id:
            self.log_test_result(
                "기본인증_전제조건",
                False,
                "인증 정보가 없습니다"
            )
            return False
        
        # 상품 수량 조회로 인증 테스트
        url = f"https://{self.mall_id}.cafe24api.com/api/v2/admin/products/count"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            self.log_test_result(
                "기본인증_테스트",
                response.status_code == 200,
                f"응답 코드: {response.status_code}, 메시지: {response.text[:200]}",
                {
                    'url': url,
                    'status_code': response.status_code,
                    'response_preview': response.text[:500]
                }
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.log_test_result(
                "기본인증_테스트",
                False,
                f"요청 실패: {str(e)}"
            )
            return False
    
    def test_products_api(self):
        """5. 상품 API 테스트"""
        print("\n[5단계] 상품 API 테스트")
        print("=" * 80)
        
        if not self.headers or not self.mall_id:
            return False
        
        # 상품 목록 조회
        url = f"https://{self.mall_id}.cafe24api.com/api/v2/admin/products"
        params = {
            'limit': 10,
            'fields': 'product_no,product_name,price,quantity,display'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                self.log_test_result(
                    "상품API_목록조회",
                    True,
                    f"{len(products)}개 상품 조회 성공",
                    {
                        'product_count': len(products),
                        'sample_product': products[0] if products else None,
                        'available_fields': list(products[0].keys()) if products else []
                    }
                )
                
                return products
            else:
                self.log_test_result(
                    "상품API_목록조회",
                    False,
                    f"응답 코드: {response.status_code}, 내용: {response.text[:200]}"
                )
                
        except Exception as e:
            self.log_test_result(
                "상품API_목록조회",
                False,
                f"요청 실패: {str(e)}"
            )
        
        return False
    
    def test_orders_api(self):
        """6. 주문 API 테스트"""
        print("\n[6단계] 주문 API 테스트")
        print("=" * 80)
        
        if not self.headers or not self.mall_id:
            return False
        
        # 오늘 주문 조회 (한국 시간)
        now_kst = datetime.now(KST)
        today = now_kst.strftime('%Y-%m-%d')
        
        url = f"https://{self.mall_id}.cafe24api.com/api/v2/admin/orders"
        params = {
            'start_date': today,
            'end_date': today,
            'limit': 10,
            'embed': 'items,receivers',
            'date_type': 'order_date'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                orders = data.get('orders', [])
                
                # 주문 금액 계산
                total_amount = 0
                for order in orders:
                    amount = 0
                    for field in ['actual_payment_amount', 'payment_amount', 'order_price_amount']:
                        if field in order:
                            try:
                                amount = float(str(order[field]).replace(',', ''))
                                break
                            except:
                                continue
                    total_amount += amount
                
                self.log_test_result(
                    "주문API_오늘주문",
                    True,
                    f"오늘 주문 {len(orders)}건, 총액 {total_amount:,.0f}원",
                    {
                        'order_count': len(orders),
                        'total_amount': total_amount,
                        'date': today,
                        'sample_order': orders[0] if orders else None
                    }
                )
                
                return orders
            else:
                self.log_test_result(
                    "주문API_오늘주문",
                    False if response.status_code != 422 else True,  # 422는 주문이 없을 때
                    f"응답 코드: {response.status_code} ({'주문 없음' if response.status_code == 422 else response.text[:200]})"
                )
                
        except Exception as e:
            self.log_test_result(
                "주문API_오늘주문",
                False,
                f"요청 실패: {str(e)}"
            )
        
        return False
    
    def test_sales_analytics(self):
        """7. 매출 분석 기능 테스트"""
        print("\n[7단계] 매출 분석 기능 테스트")
        print("=" * 80)
        
        try:
            # sales_analytics 모듈 import 시도
            from sales_analytics import SalesAnalytics
            
            # SalesAnalytics 인스턴스 생성
            def get_headers():
                return self.headers
            
            def get_mall_id():
                return self.mall_id
            
            sales = SalesAnalytics(get_headers, get_mall_id)
            
            # 주간 베스트셀러 테스트
            try:
                best_sellers = sales.get_best_sellers(days=7)
                
                self.log_test_result(
                    "매출분석_베스트셀러",
                    True,
                    f"주간 베스트셀러 {len(best_sellers)}개 조회",
                    {
                        'best_seller_count': len(best_sellers),
                        'top_3': best_sellers[:3] if best_sellers else []
                    }
                )
            except Exception as e:
                self.log_test_result(
                    "매출분석_베스트셀러",
                    False,
                    f"베스트셀러 조회 실패: {str(e)}"
                )
            
            # 월별 매출 비교 테스트
            try:
                monthly_comparison = sales.get_monthly_sales_comparison()
                
                self.log_test_result(
                    "매출분석_월별비교",
                    True,
                    f"월별 매출 비교 완료: 이번달 {monthly_comparison.get('current_month', {}).get('total_sales', 0):,.0f}원",
                    {
                        'current_month_sales': monthly_comparison.get('current_month', {}).get('total_sales', 0),
                        'growth': monthly_comparison.get('growth', {})
                    }
                )
            except Exception as e:
                self.log_test_result(
                    "매출분석_월별비교",
                    False,
                    f"월별 비교 실패: {str(e)}"
                )
            
        except ImportError as e:
            self.log_test_result(
                "매출분석_모듈로드",
                False,
                f"매출 분석 모듈 로드 실패: {str(e)}"
            )
    
    def test_market_intelligence(self):
        """8. 마켓 인텔리전스 시스템 테스트"""
        print("\n[8단계] 마켓 인텔리전스 시스템 테스트")
        print("=" * 80)
        
        try:
            from market_intelligence_system import MarketIntelligenceSystem
            
            def get_headers():
                return self.headers
            
            def get_mall_id():
                return self.mall_id
            
            market_intel = MarketIntelligenceSystem(get_headers, get_mall_id)
            
            # 성과 분석 테스트
            try:
                performance = market_intel.get_performance_analysis(days=7)
                
                weekly_best_count = len(performance.get('weekly', {}).get('best', []))
                weekly_worst_count = len(performance.get('weekly', {}).get('worst', []))
                
                self.log_test_result(
                    "마켓인텔_성과분석",
                    True,
                    f"성과 분석 완료: 베스트 {weekly_best_count}개, 워스트 {weekly_worst_count}개",
                    {
                        'weekly_best_count': weekly_best_count,
                        'weekly_worst_count': weekly_worst_count,
                        'ai_enabled': market_intel.claude is not None
                    }
                )
                
                # AI 제안 테스트 (데이터가 있을 때만)
                if weekly_best_count > 0 or weekly_worst_count > 0:
                    try:
                        suggestions = market_intel.get_ai_marketing_suggestions(performance)
                        
                        self.log_test_result(
                            "마켓인텔_AI제안",
                            True,
                            f"AI 마케팅 제안 생성 완료 (Claude {'사용' if market_intel.claude else '미사용'})",
                            {
                                'suggestions_generated': len(suggestions.get('urgent_promotions', [])),
                                'ai_enabled': market_intel.claude is not None
                            }
                        )
                    except Exception as e:
                        self.log_test_result(
                            "마켓인텔_AI제안",
                            False,
                            f"AI 제안 실패: {str(e)}"
                        )
                
            except Exception as e:
                self.log_test_result(
                    "마켓인텔_성과분석",
                    False,
                    f"성과 분석 실패: {str(e)}"
                )
                
        except ImportError as e:
            self.log_test_result(
                "마켓인텔_모듈로드",
                False,
                f"마켓 인텔리전스 모듈 로드 실패: {str(e)}"
            )
    
    def test_deployed_services(self):
        """9. 배포된 서비스 테스트"""
        print("\n[9단계] 배포된 서비스 테스트")
        print("=" * 80)
        
        deployed_urls = [
            "https://cafe24-automation.onrender.com",
            "https://cafe24-automation.onrender.com/api/status",
            "https://cafe24-automation.onrender.com/health"
        ]
        
        for url in deployed_urls:
            try:
                response = requests.get(url, timeout=30)
                
                self.log_test_result(
                    f"배포서비스_{url.split('/')[-1] or 'root'}",
                    response.status_code == 200,
                    f"응답 코드: {response.status_code}",
                    {
                        'url': url,
                        'status_code': response.status_code,
                        'response_preview': response.text[:300]
                    }
                )
                
            except Exception as e:
                self.log_test_result(
                    f"배포서비스_{url.split('/')[-1] or 'root'}",
                    False,
                    f"연결 실패: {str(e)}"
                )
    
    def test_local_server(self):
        """10. 로컬 서버 테스트"""
        print("\n[10단계] 로컬 서버 테스트")
        print("=" * 80)
        
        local_urls = [
            "http://localhost:5000",
            "http://localhost:5000/api/status",
            "http://127.0.0.1:5000"
        ]
        
        for url in local_urls:
            try:
                response = requests.get(url, timeout=5)
                
                self.log_test_result(
                    f"로컬서버_{url.split(':')[-1].split('/')[1] if '/' in url else 'root'}",
                    response.status_code == 200,
                    f"응답 코드: {response.status_code}",
                    {
                        'url': url,
                        'status_code': response.status_code
                    }
                )
                
            except Exception as e:
                # URL 파싱을 더 안전하게 처리
                try:
                    url_parts = url.split('/')
                    if len(url_parts) > 3:
                        endpoint = url_parts[3]
                    else:
                        endpoint = 'root'
                except:
                    endpoint = 'unknown'
                
                self.log_test_result(
                    f"로컬서버_{endpoint}",
                    False,
                    f"연결 실패: {str(e)} (서버가 실행되지 않았을 수 있음)"
                )
    
    def test_component_integration(self):
        """11. 컴포넌트 통합 테스트"""
        print("\n[11단계] 컴포넌트 통합 테스트")
        print("=" * 80)
        
        # 주요 모듈들이 함께 동작하는지 테스트
        try:
            # 모든 필요한 모듈 import
            modules_to_test = [
                'auto_token_manager',
                'enhanced_products_api', 
                'sales_analytics',
                'market_intelligence_system',
                'config'
            ]
            
            imported_modules = []
            failed_modules = []
            
            for module in modules_to_test:
                try:
                    __import__(module)
                    imported_modules.append(module)
                except ImportError as e:
                    failed_modules.append((module, str(e)))
            
            self.log_test_result(
                "컴포넌트_통합_모듈로드",
                len(failed_modules) == 0,
                f"모듈 로드: 성공 {len(imported_modules)}개, 실패 {len(failed_modules)}개",
                {
                    'imported': imported_modules,
                    'failed': failed_modules
                }
            )
            
        except Exception as e:
            self.log_test_result(
                "컴포넌트_통합_모듈로드",
                False,
                f"통합 테스트 실패: {str(e)}"
            )
    
    def diagnose_data_flow_issues(self):
        """12. 데이터 흐름 문제 진단"""
        print("\n[12단계] 데이터 흐름 문제 진단")
        print("=" * 80)
        
        # 실패한 테스트들을 분석하여 데이터 흐름의 어느 부분에서 문제가 발생했는지 진단
        failed_tests = {k: v for k, v in self.results.items() if not v['success']}
        
        if not failed_tests:
            self.log_test_result(
                "데이터흐름_진단",
                True,
                "모든 테스트가 통과했습니다. 데이터 흐름에 문제가 없습니다."
            )
            return
        
        # 문제점 분류
        auth_issues = []
        api_issues = []
        module_issues = []
        network_issues = []
        
        for test_name, result in failed_tests.items():
            if '인증' in test_name or '토큰' in test_name:
                auth_issues.append(test_name)
            elif 'API' in test_name or '주문' in test_name or '상품' in test_name:
                api_issues.append(test_name)
            elif '모듈' in test_name or '컴포넌트' in test_name:
                module_issues.append(test_name)
            elif '서버' in test_name or '배포' in test_name:
                network_issues.append(test_name)
        
        # 진단 보고서 생성
        diagnosis = []
        
        if auth_issues:
            diagnosis.append("[인증 문제] 토큰이 만료되었거나 잘못된 설정입니다.")
        
        if api_issues:
            diagnosis.append("[API 연결 문제] Cafe24 API 호출에서 오류가 발생했습니다.")
        
        if module_issues:
            diagnosis.append("[모듈 문제] 필요한 Python 모듈이 누락되었거나 오류가 있습니다.")
        
        if network_issues:
            diagnosis.append("[네트워크 문제] 서버 연결이나 배포에 문제가 있습니다.")
        
        self.log_test_result(
            "데이터흐름_진단",
            False,
            f"총 {len(failed_tests)}개 문제 발견: {', '.join(diagnosis)}",
            {
                'failed_tests': list(failed_tests.keys()),
                'auth_issues': auth_issues,
                'api_issues': api_issues,
                'module_issues': module_issues,
                'network_issues': network_issues,
                'diagnosis': diagnosis
            }
        )
    
    def generate_final_report(self):
        """최종 보고서 생성"""
        print("\n" + "=" * 80)
        print("[최종 진단 보고서]")
        print("=" * 80)
        
        end_time = datetime.now(KST)
        duration = end_time - self.start_time
        
        # 요약 통계
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        report = {
            'summary': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'total_tests': self.total_tests,
                'passed_tests': self.passed_tests,
                'failed_tests': self.failed_tests,
                'success_rate': round(success_rate, 2)
            },
            'test_results': self.results,
            'recommendations': []
        }
        
        # 권장사항 생성
        if success_rate < 50:
            report['recommendations'].append("[긴급] 기본 설정에 심각한 문제가 있습니다. 토큰과 API 설정을 다시 확인하세요.")
        elif success_rate < 80:
            report['recommendations'].append("[주의] 일부 기능에 문제가 있습니다. 실패한 테스트를 확인하여 수정하세요.")  
        else:
            report['recommendations'].append("[정상] 대부분의 기능이 정상적으로 작동합니다.")
        
        # 파일로 저장
        report_file = f'comprehensive_test_report_{datetime.now(KST).strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 콘솔 출력
        print(f"\n[테스트 결과] {self.passed_tests}/{self.total_tests} 통과 ({success_rate:.1f}%)")
        print(f"[소요 시간] {duration.total_seconds():.1f}초")
        print(f"[상세 보고서] {report_file}")
        
        if self.failed_tests > 0:
            print(f"\n[실패한 테스트 {self.failed_tests}개]")
            for test_name, result in self.results.items():
                if not result['success']:
                    print(f"  - {test_name}: {result['message']}")
        
        for rec in report['recommendations']:
            print(f"\n{rec}")
        
        print("\n" + "=" * 80)
        
        return report

def main():
    """메인 함수"""
    print("[카페24 API 종합 진단 시작]")
    print("=" * 80)
    print(f"시작 시간: {datetime.now(KST).strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}")
    print("=" * 80)
    
    tester = Cafe24APITester()
    
    # 순서대로 테스트 실행
    tester.test_environment_variables()
    tester.test_token_files()
    tester.get_access_credentials() 
    tester.test_basic_authentication()
    tester.test_products_api()
    tester.test_orders_api()
    tester.test_sales_analytics()
    tester.test_market_intelligence()
    tester.test_deployed_services()
    tester.test_local_server()
    tester.test_component_integration()
    tester.diagnose_data_flow_issues()
    
    # 최종 보고서 생성
    final_report = tester.generate_final_report()
    
    return final_report

if __name__ == '__main__':
    # 현재 디렉토리를 스크립트 위치로 변경
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        report = main()
        
        # 성공률이 낮으면 exit code로 알림
        if report['summary']['success_rate'] < 50:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n[중단] 사용자에 의해 테스트가 중단되었습니다.")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n[오류] 테스트 실행 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(3)