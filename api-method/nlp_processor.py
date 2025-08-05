#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
자연어 명령 처리 모듈
"""
import re
import logging

class NLPProcessor:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 명령 패턴 정의
        self.patterns = {
            'products': {
                'patterns': [
                    r'상품\s*(목록|리스트)?',
                    r'(모든|전체)\s*상품',
                    r'판매\s*가능한?\s*(제품|상품)',
                    r'제품\s*(목록|리스트)?',
                    r'products?\s*list?',
                    r'show\s*(all)?\s*products?'
                ],
                'action': 'list_products'
            },
            'orders': {
                'patterns': [
                    r'(오늘|today)\s*(주문|order)',
                    r'주문\s*(내역|목록)',
                    r'orders?\s*(today|list)?'
                ],
                'action': 'list_orders'
            },
            'inventory': {
                'patterns': [
                    r'재고\s*(부족|확인)',
                    r'(낮은|부족한)\s*재고',
                    r'low\s*stock',
                    r'inventory\s*(check|low)?'
                ],
                'action': 'check_inventory'
            },
            'sales': {
                'patterns': [
                    r'매출\s*(확인|리포트)',
                    r'(오늘|이번달)\s*매출',
                    r'sales\s*(report|today)?'
                ],
                'action': 'sales_report'
            },
            'update': {
                'patterns': [
                    r'(상품|가격)\s*(수정|변경|업데이트)',
                    r'update\s*(product|price)',
                    r'가격\s*인상',
                    r'진열\s*(변경|상태)'
                ],
                'action': 'update_product'
            }
        }
    
    def process(self, text):
        """자연어 텍스트를 명령으로 변환"""
        text = text.lower().strip()
        self.logger.info(f"Processing text: {text}")
        
        # 각 패턴 매칭
        for cmd_type, config in self.patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, text):
                    params = self._extract_parameters(text, cmd_type)
                    result = {
                        'action': config['action'],
                        'parameters': params,
                        'original_text': text
                    }
                    self.logger.info(f"Matched command: {result}")
                    return result
        
        # 매칭되지 않은 경우
        self.logger.warning(f"No matching command for: {text}")
        return {
            'action': 'unknown',
            'parameters': {},
            'original_text': text
        }
    
    def _extract_parameters(self, text, cmd_type):
        """텍스트에서 파라미터 추출"""
        params = {}
        
        # 숫자 추출
        numbers = re.findall(r'\d+', text)
        if numbers:
            params['limit'] = int(numbers[0])
        
        # 카테고리 추출
        categories = ['식품', '음료', '생활', '부산', '인생']
        for category in categories:
            if category in text:
                params['category'] = category
                break
        
        # 날짜 관련
        if '오늘' in text or 'today' in text:
            params['date'] = 'today'
        elif '어제' in text or 'yesterday' in text:
            params['date'] = 'yesterday'
        elif '이번달' in text or 'this month' in text:
            params['date'] = 'this_month'
        
        # 정렬 관련
        if '높은' in text or 'high' in text:
            params['sort'] = 'desc'
        elif '낮은' in text or 'low' in text:
            params['sort'] = 'asc'
        
        return params