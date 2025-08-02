#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Natural Language Processor
Processes Korean and English commands for Cafe24 operations
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class NaturalLanguageProcessor:
    """Process natural language commands for Cafe24 operations"""
    
    def __init__(self):
        """Initialize NLP processor with command patterns"""
        self.logger = logging.getLogger('NLPProcessor')
        
        # Define command patterns
        self.patterns = {
            'get_products': {
                'patterns': [
                    r'상품.*목록',
                    r'전체.*상품',
                    r'모든.*상품',
                    r'상품.*보여',
                    r'product.*list',
                    r'show.*products'
                ],
                'extractor': self._extract_product_params
            },
            'get_orders': {
                'patterns': [
                    r'주문.*목록',
                    r'주문.*내역',
                    r'오늘.*주문',
                    r'신규.*주문',
                    r'order.*list',
                    r'today.*order'
                ],
                'extractor': self._extract_order_params
            },
            'check_inventory': {
                'patterns': [
                    r'재고.*확인',
                    r'재고.*부족',
                    r'품절.*상품',
                    r'재고.*점검',
                    r'inventory.*check',
                    r'low.*stock'
                ],
                'extractor': self._extract_inventory_params
            },
            'generate_report': {
                'patterns': [
                    r'리포트.*생성',
                    r'보고서.*작성',
                    r'통계.*보기',
                    r'일일.*리포트',
                    r'generate.*report',
                    r'daily.*report'
                ],
                'extractor': self._extract_report_params
            },
            'update_products': {
                'patterns': [
                    r'상품.*수정',
                    r'가격.*변경',
                    r'상품.*업데이트',
                    r'update.*product',
                    r'change.*price'
                ],
                'extractor': self._extract_update_params
            },
            'check_health': {
                'patterns': [
                    r'시스템.*상태',
                    r'헬스.*체크',
                    r'시스템.*점검',
                    r'system.*health',
                    r'health.*check'
                ],
                'extractor': lambda x: {}
            }
        }
        
        # Date patterns
        self.date_patterns = {
            '오늘': lambda: datetime.now(),
            '어제': lambda: datetime.now() - timedelta(days=1),
            '이번주': lambda: datetime.now() - timedelta(days=datetime.now().weekday()),
            '이번달': lambda: datetime.now().replace(day=1),
            '지난주': lambda: datetime.now() - timedelta(weeks=1),
            '지난달': lambda: (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1)
        }
        
    def process(self, command: str) -> Optional[Dict[str, Any]]:
        """Process natural language command"""
        try:
            # Normalize command
            command = command.strip().lower()
            
            # Find matching pattern
            for action, config in self.patterns.items():
                for pattern in config['patterns']:
                    if re.search(pattern, command):
                        self.logger.info(f"Matched action: {action} for command: {command}")
                        
                        # Extract parameters
                        params = config['extractor'](command)
                        
                        return {
                            'action': action,
                            'params': params,
                            'original_command': command
                        }
                        
            self.logger.warning(f"No pattern matched for command: {command}")
            return None
            
        except Exception as e:
            self.logger.error(f"NLP processing error: {e}")
            return None
            
    def _extract_product_params(self, command: str) -> Dict[str, Any]:
        """Extract parameters for product commands"""
        params = {}
        
        # Check for category
        category_match = re.search(r'카테고리\s*[:\s]*(\S+)', command)
        if category_match:
            params['category'] = category_match.group(1)
            
        # Check for search keyword
        search_match = re.search(r'검색\s*[:\s]*(\S+)', command)
        if search_match:
            params['keyword'] = search_match.group(1)
            
        # Check for price range
        price_match = re.search(r'(\d+)\s*원?\s*이상', command)
        if price_match:
            params['min_price'] = int(price_match.group(1))
            
        price_match = re.search(r'(\d+)\s*원?\s*이하', command)
        if price_match:
            params['max_price'] = int(price_match.group(1))
            
        # Check for status
        if '품절' in command:
            params['sold_out'] = True
        if '판매중' in command:
            params['selling'] = True
            
        return params
        
    def _extract_order_params(self, command: str) -> Dict[str, Any]:
        """Extract parameters for order commands"""
        params = {}
        
        # Extract date parameters
        for date_keyword, date_func in self.date_patterns.items():
            if date_keyword in command:
                date = date_func()
                params['start_date'] = date.strftime('%Y-%m-%d')
                
                # Set end date based on context
                if '주' in date_keyword:
                    end_date = date + timedelta(days=6)
                elif '달' in date_keyword:
                    # Last day of month
                    if date.month == 12:
                        end_date = date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1)
                    else:
                        end_date = date.replace(month=date.month + 1, day=1) - timedelta(days=1)
                else:
                    end_date = date
                    
                params['end_date'] = end_date.strftime('%Y-%m-%d')
                break
                
        # Check for order status
        if '신규' in command or 'new' in command:
            params['status'] = 'N00'  # New order
        elif '배송중' in command:
            params['status'] = 'N20'  # Shipping
        elif '완료' in command:
            params['status'] = 'N40'  # Completed
            
        return params
        
    def _extract_inventory_params(self, command: str) -> Dict[str, Any]:
        """Extract parameters for inventory commands"""
        params = {}
        
        # Extract threshold
        threshold_match = re.search(r'(\d+)\s*개?\s*이하', command)
        if threshold_match:
            params['threshold'] = int(threshold_match.group(1))
        else:
            # Default threshold
            params['threshold'] = 10
            
        return params
        
    def _extract_report_params(self, command: str) -> Dict[str, Any]:
        """Extract parameters for report commands"""
        params = {}
        
        # Determine report type
        if '일일' in command or 'daily' in command:
            params['report_type'] = 'daily'
        elif '재고' in command or 'inventory' in command:
            params['report_type'] = 'inventory'
        elif '매출' in command or 'sales' in command:
            params['report_type'] = 'sales'
        else:
            params['report_type'] = 'daily'  # Default
            
        return params
        
    def _extract_update_params(self, command: str) -> Dict[str, Any]:
        """Extract parameters for update commands"""
        params = {}
        
        # Extract percentage change
        percent_match = re.search(r'(\d+)\s*%', command)
        if percent_match:
            params['percentage'] = int(percent_match.group(1))
            
            if '인상' in command or 'increase' in command:
                params['operation'] = 'increase'
            elif '인하' in command or 'decrease' in command:
                params['operation'] = 'decrease'
                
        # Extract fixed price
        price_match = re.search(r'(\d+)\s*원으로', command)
        if price_match:
            params['fixed_price'] = int(price_match.group(1))
            params['operation'] = 'fixed'
            
        return params