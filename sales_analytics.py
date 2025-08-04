#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
매출 분석 API
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import pytz
import requests
import calendar
from collections import defaultdict
import logging
import json

logger = logging.getLogger(__name__)

# 한국 시간대
KST = pytz.timezone('Asia/Seoul')

sales_bp = Blueprint('sales', __name__)

class SalesAnalytics:
    def __init__(self, get_headers, get_mall_id):
        self.get_headers = get_headers
        self.get_mall_id = get_mall_id
        
    def get_date_range_orders(self, start_date, end_date):
        """특정 기간의 주문 데이터 조회"""
        try:
            headers = self.get_headers()
            mall_id = self.get_mall_id()
            
            url = f"https://{mall_id}.cafe24api.com/api/v2/admin/orders"
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'limit': 500,
                'embed': 'items,receivers,return',  # 상세 정보 포함
                'order_status': 'N00,N10,N20,N21,N22,N30,N40',  # 정상 주문만
                'date_type': 'order_date'
            }
            
            all_orders = []
            offset = 0
            
            while True:
                params['offset'] = offset
                response = requests.get(url, headers=headers, params=params)
                
                logger.info(f"Orders API request: {url} with params: {params}")
                logger.info(f"Orders API response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    orders = data.get('orders', [])
                    
                    # 주문 데이터 샘플 로깅
                    if orders and offset == 0:
                        logger.info(f"Sample order data: {orders[0] if orders else 'No orders'}")
                    
                    all_orders.extend(orders)
                    
                    if len(orders) < params['limit']:
                        break
                    offset += params['limit']
                else:
                    logger.error(f"Orders API error: {response.status_code} - {response.text}")
                    break
                    
            return all_orders
            
        except Exception as e:
            print(f"Error fetching orders: {str(e)}")
            return []
    
    def calculate_sales_summary(self, orders):
        """주문 데이터에서 매출 요약 계산"""
        total_sales = 0
        valid_order_count = 0
        customer_set = set()
        
        for idx, order in enumerate(orders):
            # 주문 상태 확인 (취소/환불 제외)
            order_status = order.get('order_status', '')
            if order_status.startswith('C'):  # 취소 주문 제외
                continue
                
            # 첫 주문 상세 로깅
            if idx == 0:
                logger.info(f"First order full data: {json.dumps(order, ensure_ascii=False)[:1000]}...")
            
            # 다양한 금액 필드 확인
            payment_amount = 0
            
            # actual_payment_amount를 우선 확인 (실제 결제 금액)
            if 'actual_payment_amount' in order:
                try:
                    payment_amount = float(str(order.get('actual_payment_amount', '0')).replace(',', ''))
                except:
                    payment_amount = 0
            # payment_amount 확인
            elif 'payment_amount' in order:
                try:
                    payment_amount = float(str(order.get('payment_amount', '0')).replace(',', ''))
                except:
                    payment_amount = 0
            # order_price_amount 확인
            elif 'order_price_amount' in order:
                try:
                    payment_amount = float(str(order.get('order_price_amount', '0')).replace(',', ''))
                except:
                    payment_amount = 0
            
            if payment_amount > 0:
                total_sales += payment_amount
                valid_order_count += 1
                customer_set.add(order.get('buyer_name', ''))
        
        logger.info(f"Total sales: {total_sales:,.0f} from {valid_order_count} valid orders (total: {len(orders)})")
        
        return {
            'total_sales': total_sales,
            'order_count': valid_order_count,
            'unique_customers': len(customer_set),
            'average_order_value': total_sales / valid_order_count if valid_order_count > 0 else 0
        }
    
    def get_monthly_sales_comparison(self):
        """월별 매출 비교 - 한국 시간 기준"""
        now_kst = datetime.now(KST)
        
        # 이번달 (KST)
        current_month_start = datetime(now_kst.year, now_kst.month, 1, tzinfo=KST)
        current_month_orders = self.get_date_range_orders(current_month_start, now_kst)
        current_month_summary = self.calculate_sales_summary(current_month_orders)
        
        # 전달
        if now_kst.month == 1:
            last_month_start = datetime(now_kst.year - 1, 12, 1, tzinfo=KST)
            last_month_end = datetime(now_kst.year - 1, 12, 31, tzinfo=KST)
        else:
            last_month_start = datetime(now_kst.year, now_kst.month - 1, 1, tzinfo=KST)
            last_month_days = calendar.monthrange(now_kst.year, now_kst.month - 1)[1]
            last_month_end = datetime(now_kst.year, now_kst.month - 1, last_month_days, tzinfo=KST)
            
        last_month_orders = self.get_date_range_orders(last_month_start, last_month_end)
        last_month_summary = self.calculate_sales_summary(last_month_orders)
        
        # 전년 동월
        last_year_month_start = datetime(now_kst.year - 1, now_kst.month, 1, tzinfo=KST)
        last_year_month_end = datetime(now_kst.year - 1, now_kst.month, min(now_kst.day, calendar.monthrange(now_kst.year - 1, now_kst.month)[1]), tzinfo=KST)
        last_year_month_orders = self.get_date_range_orders(last_year_month_start, last_year_month_end)
        last_year_month_summary = self.calculate_sales_summary(last_year_month_orders)
        
        # 증감률 계산
        mom_growth = 0  # Month over Month
        yoy_growth = 0  # Year over Year
        
        if last_month_summary['total_sales'] > 0:
            mom_growth = ((current_month_summary['total_sales'] - last_month_summary['total_sales']) 
                         / last_month_summary['total_sales'] * 100)
        
        if last_year_month_summary['total_sales'] > 0:
            yoy_growth = ((current_month_summary['total_sales'] - last_year_month_summary['total_sales']) 
                         / last_year_month_summary['total_sales'] * 100)
        
        return {
            'current_month': {
                'period': f"{now_kst.year}년 {now_kst.month}월",
                'days': now_kst.day,
                **current_month_summary
            },
            'last_month': {
                'period': f"{last_month_start.year}년 {last_month_start.month}월",
                'days': last_month_days if 'last_month_days' in locals() else 31,
                **last_month_summary
            },
            'last_year_month': {
                'period': f"{last_year_month_start.year}년 {last_year_month_start.month}월",
                'days': min(now_kst.day, calendar.monthrange(now_kst.year - 1, now_kst.month)[1]),
                **last_year_month_summary
            },
            'growth': {
                'mom': round(mom_growth, 2),
                'yoy': round(yoy_growth, 2)
            }
        }
    
    def get_daily_sales_trend(self, days=30):
        """일별 매출 추이 - 한국 시간 기준"""
        end_date = datetime.now(KST)
        start_date = end_date - timedelta(days=days)
        
        orders = self.get_date_range_orders(start_date, end_date)
        
        # 일별 집계
        daily_sales = defaultdict(lambda: {'sales': 0, 'orders': 0})
        
        for order in orders:
            order_date = order.get('order_date', '').split('T')[0]
            payment_amount = float(order.get('payment_amount', 0))
            
            if order_date:
                daily_sales[order_date]['sales'] += payment_amount
                daily_sales[order_date]['orders'] += 1
        
        # 날짜 순 정렬
        sorted_dates = sorted(daily_sales.keys())
        
        return {
            'labels': sorted_dates,
            'sales': [daily_sales[date]['sales'] for date in sorted_dates],
            'orders': [daily_sales[date]['orders'] for date in sorted_dates],
            'period': f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}"
        }
    
    def get_best_sellers(self, days=30):
        """베스트셀러 상품 - 한국 시간 기준"""
        end_date = datetime.now(KST)
        start_date = end_date - timedelta(days=days)
        
        orders = self.get_date_range_orders(start_date, end_date)
        
        logger.info(f"Best sellers: Found {len(orders)} orders for {days} days")
        
        # 상품별 집계
        product_sales = defaultdict(lambda: {
            'quantity': 0, 
            'revenue': 0, 
            'product_name': '',
            'orders': 0
        })
        
        items_found = False
        for order in orders:
            items = order.get('items', [])
            if items and not items_found:
                logger.info(f"Sample item: {items[0] if items else 'No items'}")
                items_found = True
                
            for item in items:
                product_no = item.get('product_no')
                if product_no:
                    # 가격 필드 확인 - API 버전에 따라 다를 수 있음
                    price = float(item.get('product_price', 0) or item.get('price', 0) or 0)
                    quantity = int(item.get('quantity', 0))
                    
                    product_sales[product_no]['quantity'] += quantity
                    product_sales[product_no]['revenue'] += price * quantity
                    product_sales[product_no]['product_name'] = item.get('product_name', '')
                    product_sales[product_no]['orders'] += 1
        
        # 매출 기준 정렬
        sorted_products = sorted(
            product_sales.items(), 
            key=lambda x: x[1]['revenue'], 
            reverse=True
        )[:10]
        
        return [{
            'product_no': product_no,
            'product_name': data['product_name'],
            'quantity': data['quantity'],
            'revenue': data['revenue'],
            'orders': data['orders']
        } for product_no, data in sorted_products]
    
    def get_hourly_distribution(self, days=7):
        """시간대별 주문 분포 - 한국 시간 기준"""
        end_date = datetime.now(KST)
        start_date = end_date - timedelta(days=days)
        
        orders = self.get_date_range_orders(start_date, end_date)
        
        # 시간대별 집계
        hourly_orders = defaultdict(int)
        hourly_sales = defaultdict(float)
        
        for order in orders:
            order_datetime = order.get('order_date', '')
            if 'T' in order_datetime:
                hour = int(order_datetime.split('T')[1][:2])
                hourly_orders[hour] += 1
                hourly_sales[hour] += float(order.get('payment_amount', 0))
        
        return {
            'hours': list(range(24)),
            'orders': [hourly_orders.get(h, 0) for h in range(24)],
            'sales': [hourly_sales.get(h, 0) for h in range(24)]
        }

def register_sales_routes(blueprint, analytics):
    """매출 분석 라우트 등록"""
    
    @blueprint.route('/monthly-comparison')
    def monthly_comparison():
        """월별 매출 비교"""
        try:
            data = analytics.get_monthly_sales_comparison()
            return jsonify({
                'success': True,
                **data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @blueprint.route('/daily-trend')
    def daily_trend():
        """일별 매출 추이"""
        try:
            days = request.args.get('days', 30, type=int)
            data = analytics.get_daily_sales_trend(days)
            return jsonify({
                'success': True,
                **data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @blueprint.route('/best-sellers')
    def best_sellers():
        """베스트셀러"""
        try:
            days = request.args.get('days', 30, type=int)
            data = analytics.get_best_sellers(days)
            return jsonify({
                'success': True,
                'products': data,
                'period_days': days
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @blueprint.route('/hourly-distribution')
    def hourly_distribution():
        """시간대별 분포"""
        try:
            days = request.args.get('days', 7, type=int)
            data = analytics.get_hourly_distribution(days)
            return jsonify({
                'success': True,
                **data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500