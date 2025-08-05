#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 기반 시장 인텔리전스 시스템
통합 판매 분석 + Claude AI 마케팅 제안
"""
import os
import sys
from datetime import datetime, timedelta
import pytz
import json
import anthropic
from collections import defaultdict
import logging
from secure_api_manager import SecureAPIManager
import requests

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 한국 시간대
KST = pytz.timezone('Asia/Seoul')

class MarketIntelligenceSystem:
    def __init__(self, get_headers, get_mall_id):
        self.get_headers = get_headers
        self.get_mall_id = get_mall_id
        
        # Claude API 초기화
        api_manager = SecureAPIManager()
        api_key = api_manager.get_api_key("anthropic")
        
        if api_key:
            self.claude = anthropic.Anthropic(api_key=api_key)
            logger.info("Claude AI initialized successfully")
        else:
            self.claude = None
            logger.warning("Claude API key not found - AI features disabled")
    
    def get_performance_analysis(self, days=7):
        """주간/일간 베스트&워스트 상품 분석"""
        from sales_analytics import SalesAnalytics
        
        sales = SalesAnalytics(self.get_headers, self.get_mall_id)
        
        # 주간 분석
        weekly_best = sales.get_best_sellers(days=7)
        weekly_worst = self._get_worst_sellers(days=7)
        
        # 어제 분석
        yesterday_best = self._get_daily_best_sellers(1)
        yesterday_worst = self._get_daily_worst_sellers(1)
        
        return {
            'weekly': {
                'best': weekly_best[:10],
                'worst': weekly_worst[:10]
            },
            'yesterday': {
                'best': yesterday_best[:10],
                'worst': yesterday_worst[:10]
            },
            'analysis_date': datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST')
        }
    
    def _get_worst_sellers(self, days=7):
        """워스트셀러 상품 분석"""
        try:
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            # 모든 상품 조회
            url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
            params = {
                'limit': 500,
                'fields': 'product_no,product_name,price,quantity,created_date'
            }
            
            all_products = []
            offset = 0
            
            while True:
                params['offset'] = offset
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    products = data.get('products', [])
                    all_products.extend(products)
                    
                    if len(products) < params['limit']:
                        break
                    offset += params['limit']
                else:
                    break
            
            # 판매 데이터와 매칭하여 판매 0인 상품 찾기
            from sales_analytics import SalesAnalytics
            sales = SalesAnalytics(self.get_headers, self.get_mall_id)
            
            end_date = datetime.now(KST)
            start_date = end_date - timedelta(days=days)
            orders = sales.get_date_range_orders(start_date, end_date)
            
            # 판매된 상품 목록
            sold_products = set()
            for order in orders:
                items = order.get('items', [])
                for item in items:
                    sold_products.add(item.get('product_no'))
            
            # 판매되지 않은 상품 필터링
            worst_sellers = []
            for product in all_products:
                if product.get('product_no') not in sold_products:
                    # 등록된지 최소 7일 이상 된 상품만
                    created_date = product.get('created_date', '')
                    if created_date:
                        created = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                        if (datetime.now(pytz.UTC) - created).days >= days:
                            worst_sellers.append({
                                'product_no': product.get('product_no'),
                                'product_name': product.get('product_name'),
                                'price': float(product.get('price', 0)),
                                'quantity': int(product.get('quantity', 0)),
                                'days_since_launch': (datetime.now(pytz.UTC) - created).days,
                                'sales_count': 0
                            })
            
            # 재고가 많은 순으로 정렬
            worst_sellers.sort(key=lambda x: x['quantity'], reverse=True)
            
            return worst_sellers
            
        except Exception as e:
            logger.error(f"Error getting worst sellers: {str(e)}")
            return []
    
    def _get_daily_best_sellers(self, days=1):
        """일간 베스트셀러"""
        from sales_analytics import SalesAnalytics
        sales = SalesAnalytics(self.get_headers, self.get_mall_id)
        return sales.get_best_sellers(days=days)
    
    def _get_daily_worst_sellers(self, days=1):
        """일간 워스트셀러"""
        return self._get_worst_sellers(days=days)
    
    def get_ai_marketing_suggestions(self, performance_data):
        """Claude AI를 활용한 마케팅 제안"""
        if not self.claude:
            return self._get_rule_based_suggestions(performance_data)
        
        try:
            # AI 프롬프트 구성
            prompt = f"""
당신은 한국 온라인 식품 유통 전문가입니다. 다음 판매 데이터를 분석하여 즉시 실행 가능한 마케팅 전략을 제안해주세요.

## 주간 베스트셀러 TOP 10
{json.dumps(performance_data['weekly']['best'], ensure_ascii=False, indent=2)}

## 주간 워스트셀러 TOP 10 (판매 0건)
{json.dumps(performance_data['weekly']['worst'], ensure_ascii=False, indent=2)}

## 어제 베스트셀러
{json.dumps(performance_data['yesterday']['best'], ensure_ascii=False, indent=2)}

다음을 분석하고 제안해주세요:

1. **긴급 프로모션 (3개)**
   - 재고 소진이 시급한 워스트 상품 번들 구성
   - 구체적인 할인율과 번들 구성
   - 예상 효과

2. **트렌드 활용 전략 (3개)**
   - 베스트셀러의 성공 요인 분석
   - 워스트셀러와의 시너지 상품 구성
   - SNS 마케팅 메시지

3. **계절/이벤트 연계 (2개)**
   - 현재 시즌에 맞는 프로모션
   - 다가오는 이벤트 활용 방안

JSON 형식으로 응답해주세요.
"""
            
            response = self.claude.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # AI 응답 파싱
            ai_response = response.content[0].text
            
            # JSON 추출 시도
            try:
                # JSON 블록 찾기
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
                if json_match:
                    suggestions = json.loads(json_match.group(1))
                else:
                    # JSON 블록이 없으면 전체를 파싱 시도
                    suggestions = json.loads(ai_response)
            except:
                # 파싱 실패시 텍스트 그대로 반환
                suggestions = {
                    'urgent_promotions': [],
                    'trend_strategies': [],
                    'seasonal_events': [],
                    'raw_response': ai_response
                }
            
            return suggestions
            
        except Exception as e:
            logger.error(f"AI suggestion error: {str(e)}")
            return self._get_rule_based_suggestions(performance_data)
    
    def _get_rule_based_suggestions(self, performance_data):
        """룰 기반 마케팅 제안 (AI 없을 때)"""
        suggestions = {
            'urgent_promotions': [],
            'trend_strategies': [],
            'seasonal_events': []
        }
        
        # 긴급 프로모션 생성
        worst_products = performance_data['weekly']['worst'][:5]
        best_products = performance_data['weekly']['best'][:5]
        
        for i, worst in enumerate(worst_products):
            if i < len(best_products):
                best = best_products[i]
                suggestions['urgent_promotions'].append({
                    'type': 'bundle',
                    'title': f"{best['product_name']} + {worst['product_name']} 특가 세트",
                    'discount': 20,
                    'products': [best['product_no'], worst['product_no']],
                    'reason': f"인기상품 구매시 {worst['days_since_launch']}일간 판매 0인 상품 할인"
                })
        
        # 트렌드 전략
        for best in best_products[:3]:
            suggestions['trend_strategies'].append({
                'type': 'featured',
                'product': best['product_name'],
                'strategy': f"일 평균 {best.get('quantity', 0) // 7}개 판매 인기상품",
                'action': "메인 배너 노출 + SNS 홍보"
            })
        
        # 계절 이벤트
        current_month = datetime.now(KST).month
        if current_month in [7, 8]:  # 여름
            suggestions['seasonal_events'].append({
                'event': '여름 특별 기획전',
                'products': '시원한 면요리, 냉동식품',
                'discount': 15
            })
        
        return suggestions
    
    def generate_promotion_execution(self, suggestion):
        """프로모션 실행 계획 생성"""
        execution_plan = {
            'promotion_id': f"PROMO_{datetime.now(KST).strftime('%Y%m%d%H%M%S')}",
            'created_at': datetime.now(KST).isoformat(),
            'details': suggestion,
            'execution_steps': [
                {
                    'step': 1,
                    'action': '가격 조정',
                    'target': suggestion.get('products', []),
                    'discount': suggestion.get('discount', 0)
                },
                {
                    'step': 2,
                    'action': '상품 노출 순위 변경',
                    'priority': 'high'
                },
                {
                    'step': 3,
                    'action': 'SNS 마케팅 포스트',
                    'content': suggestion.get('title', '')
                }
            ]
        }
        
        return execution_plan

# Flask Blueprint 등록용
from flask import Blueprint, jsonify, request
import requests

market_intel_bp = Blueprint('market_intel', __name__)

def register_market_intel_routes(blueprint, system):
    """마켓 인텔리전스 라우트 등록"""
    
    @blueprint.route('/performance-analysis')
    def performance_analysis():
        """판매 성과 분석"""
        try:
            days = request.args.get('days', 7, type=int)
            data = system.get_performance_analysis(days)
            return jsonify({
                'success': True,
                **data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @blueprint.route('/ai-suggestions', methods=['POST'])
    def ai_suggestions():
        """AI 마케팅 제안"""
        try:
            performance_data = request.get_json()
            if not performance_data:
                # 자동으로 성과 데이터 가져오기
                performance_data = system.get_performance_analysis()
            
            suggestions = system.get_ai_marketing_suggestions(performance_data)
            
            return jsonify({
                'success': True,
                'suggestions': suggestions,
                'ai_enabled': system.claude is not None
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @blueprint.route('/execute-promotion', methods=['POST'])
    def execute_promotion():
        """프로모션 실행"""
        try:
            suggestion = request.get_json()
            execution_plan = system.generate_promotion_execution(suggestion)
            
            return jsonify({
                'success': True,
                'execution_plan': execution_plan
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500