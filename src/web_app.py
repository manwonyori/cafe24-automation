#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web API for Cafe24 Automation System
Provides REST API and health check endpoints
"""

import os
import json
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cafe24_system import Cafe24System

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Cafe24 system with improved error handling
try:
    system = Cafe24System()
    system_initialized = True
    logging.info("Cafe24 system initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize Cafe24 system: {e}")
    # Create a fallback demo system
    try:
        from demo_mode import DemoAPIClient
        class FallbackSystem:
            def __init__(self):
                self.api_client = DemoAPIClient({})
                self.demo_mode = True
                self.logger = logging.getLogger('FallbackSystem')
                
            def get_products(self, **kwargs):
                return self.api_client.get_products(**kwargs)
                
            def get_orders(self, **kwargs):
                return self.api_client.get_orders(**kwargs)
                
            def check_inventory(self, threshold=10):
                products = self.api_client.get_products()
                low_stock = [p for p in products if p.get('inventory_quantity', 0) <= threshold]
                out_of_stock = [p for p in products if p.get('inventory_quantity', 0) == 0]
                return {
                    'low_stock': low_stock,
                    'out_of_stock': out_of_stock,
                    'total_products': len(products),
                    'threshold': threshold
                }
                
            def get_customers(self, **kwargs):
                return self.api_client.get_customers(**kwargs)
                
            def get_sales_statistics(self, **kwargs):
                return self.api_client.get_sales_statistics(**kwargs)
                
            def generate_report(self, report_type='daily'):
                if report_type == 'daily':
                    return {
                        'report_type': 'daily',
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'summary': 'Demo mode - System operational'
                    }
                return {'report_type': report_type, 'status': 'demo_mode'}
                
            def execute(self, command):
                return {
                    'success': True,
                    'message': 'Demo mode active - Command processed',
                    'command': command,
                    'mode': 'demo'
                }
        
        system = FallbackSystem()
        system_initialized = True
        logging.info("Fallback demo system initialized")
    except Exception as fallback_error:
        logging.error(f"Failed to initialize fallback system: {fallback_error}")
        system_initialized = False
        system = None

@app.route('/')
def home():
    """Home endpoint - Return dashboard if browser, JSON if API"""
    # Check if request is from browser
    if request.headers.get('Accept', '').find('text/html') != -1:
        return render_template('dashboard.html')
    
    # Return JSON for API requests
    mode = 'demo' if hasattr(system, 'demo_mode') and system.demo_mode else 'production'
    
    return jsonify({
        'name': 'Cafe24 Automation System',
        'version': '2.0.0',
        'description': '카페24 쇼핑몰 완전 자동화 시스템',
        'status': 'online' if system_initialized else 'error',
        'mode': mode,
        'features': {
            'natural_language': '한국어/영어 자연어 명령 지원',
            'oauth': 'OAuth 2.0 인증',
            'caching': '고성능 캐싱 시스템',
            'auto_refresh': '토큰 자동 갱신'
        },
        'endpoints': {
            'health': '/health',
            'execute': '/api/execute',
            'products': '/api/products',
            'orders': '/api/orders', 
            'inventory': '/api/inventory',
            'report': '/api/report'
        },
        'examples': {
            'execute': 'POST /api/execute {"command": "오늘 주문 확인"}',
            'products': 'GET /api/products?limit=10',
            'inventory': 'GET /api/inventory?threshold=5'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    # Simple health check without API calls
    return jsonify({
        'status': 'healthy',
        'service': 'cafe24-automation',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'system_initialized': system_initialized
    }), 200

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """Execute natural language command"""
    if not system_initialized:
        return jsonify({'error': 'System not initialized'}), 503
    
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        result = system.execute(command)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get products list"""
    if not system_initialized or not system:
        return jsonify({
            'error': 'System not initialized',
            'message': 'The Cafe24 automation system is not properly initialized'
        }), 503
    
    try:
        # Get query parameters with safe defaults
        limit = min(int(request.args.get('limit', 100)), 1000)  # Cap at 1000
        offset = max(int(request.args.get('offset', 0)), 0)  # Non-negative
        display = request.args.get('display')
        selling = request.args.get('selling')
        
        # Build kwargs
        kwargs = {}
        if display:
            kwargs['display'] = display
        if selling:
            kwargs['selling'] = selling
            
        products = system.get_products(limit=limit, offset=offset, **kwargs)
        
        # Ensure products is a list
        if not isinstance(products, list):
            products = []
            
        return jsonify({
            'success': True,
            'count': len(products),
            'products': products,
            'demo_mode': getattr(system, 'demo_mode', False)
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        logging.error(f"Products API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e) if app.debug else 'An error occurred while fetching products'
        }), 500

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get orders list"""
    if not system_initialized or not system:
        return jsonify({
            'error': 'System not initialized',
            'message': 'The Cafe24 automation system is not properly initialized'
        }), 503
    
    try:
        start_date = request.args.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', start_date)
        limit = min(int(request.args.get('limit', 100)), 1000)
        offset = max(int(request.args.get('offset', 0)), 0)
        
        orders = system.get_orders(
            start_date=start_date, 
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        # Ensure orders is a list
        if not isinstance(orders, list):
            orders = []
        
        return jsonify({
            'success': True,
            'count': len(orders),
            'orders': orders,
            'demo_mode': getattr(system, 'demo_mode', False),
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        logging.error(f"Orders API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e) if app.debug else 'An error occurred while fetching orders'
        }), 500

@app.route('/api/inventory', methods=['GET'])
def check_inventory():
    """Check inventory status"""
    if not system_initialized or not system:
        return jsonify({
            'error': 'System not initialized',
            'message': 'The Cafe24 automation system is not properly initialized'
        }), 503
    
    try:
        threshold = max(int(request.args.get('threshold', 10)), 1)
        
        inventory_data = system.check_inventory(threshold=threshold)
        
        return jsonify({
            'success': True,
            'threshold': threshold,
            'low_stock': inventory_data.get('low_stock', []),
            'out_of_stock': inventory_data.get('out_of_stock', []),
            'low_stock_count': len(inventory_data.get('low_stock', [])),
            'out_of_stock_count': len(inventory_data.get('out_of_stock', [])),
            'total_products': inventory_data.get('total_products', 0),
            'demo_mode': getattr(system, 'demo_mode', False)
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        logging.error(f"Inventory API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e) if app.debug else 'An error occurred while checking inventory'
        }), 500

@app.route('/api/report/<report_type>', methods=['GET'])
def generate_report(report_type):
    """Generate various reports"""
    if not system_initialized:
        return jsonify({'error': 'System not initialized'}), 503
    
    try:
        if report_type not in ['daily', 'inventory', 'sales']:
            return jsonify({'error': 'Invalid report type'}), 400
            
        report = system.generate_report(report_type)
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Get customers list"""
    if not system_initialized or not system:
        return jsonify({
            'error': 'System not initialized',
            'message': 'The Cafe24 automation system is not properly initialized'
        }), 503
    
    try:
        limit = min(int(request.args.get('limit', 100)), 1000)
        offset = max(int(request.args.get('offset', 0)), 0)
        
        customers = system.get_customers(limit=limit, offset=offset)
        
        # Ensure customers is a list
        if not isinstance(customers, list):
            customers = []
        
        return jsonify({
            'success': True,
            'count': len(customers),
            'customers': customers,
            'demo_mode': getattr(system, 'demo_mode', False)
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        logging.error(f"Customers API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e) if app.debug else 'An error occurred while fetching customers'
        }), 500

@app.route('/api/sales/statistics', methods=['GET'])
def get_sales_statistics():
    """Get sales statistics"""
    if not system_initialized or not system:
        return jsonify({
            'error': 'System not initialized',
            'message': 'The Cafe24 automation system is not properly initialized'
        }), 503
    
    try:
        period = request.args.get('period', 'daily')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Validate period
        valid_periods = ['daily', 'weekly', 'monthly']
        if period not in valid_periods:
            period = 'daily'
        
        kwargs = {'period': period}
        if start_date:
            kwargs['start_date'] = start_date
        if end_date:
            kwargs['end_date'] = end_date
            
        stats = system.get_sales_statistics(**kwargs)
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'demo_mode': getattr(system, 'demo_mode', False)
        })
        
    except Exception as e:
        logging.error(f"Sales statistics API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e) if app.debug else 'An error occurred while fetching sales statistics'
        }), 500

@app.route('/api/test/all', methods=['GET'])
def test_all_endpoints():
    """Test all API endpoints"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'system_initialized': system_initialized,
        'tests': []
    }
    
    # Define test cases
    test_cases = [
        {
            'name': 'Health Check',
            'endpoint': '/health',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'Products API',
            'endpoint': '/api/products?limit=5',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'Orders API',
            'endpoint': '/api/orders?limit=5',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'Inventory API',
            'endpoint': '/api/inventory?threshold=10',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'Customers API',
            'endpoint': '/api/customers?limit=5',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'Sales Statistics API',
            'endpoint': '/api/sales/statistics?period=daily',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'Natural Language API',
            'endpoint': '/api/execute',
            'method': 'POST',
            'data': {'command': '상품 목록 보여줘'},
            'expected_status': 200
        }
    ]
    
    # Run tests
    for test in test_cases:
        try:
            # Make internal request
            with app.test_client() as client:
                if test['method'] == 'GET':
                    response = client.get(test['endpoint'])
                else:
                    response = client.post(
                        test['endpoint'],
                        json=test.get('data', {}),
                        headers={'Content-Type': 'application/json'}
                    )
                
                test_result = {
                    'name': test['name'],
                    'endpoint': test['endpoint'],
                    'status': response.status_code,
                    'success': response.status_code == test['expected_status'],
                    'response': response.get_json()
                }
                
                results['tests'].append(test_result)
                
        except Exception as e:
            results['tests'].append({
                'name': test['name'],
                'endpoint': test['endpoint'],
                'success': False,
                'error': str(e)
            })
    
    # Summary
    total_tests = len(results['tests'])
    passed_tests = sum(1 for t in results['tests'] if t.get('success', False))
    results['summary'] = {
        'total': total_tests,
        'passed': passed_tests,
        'failed': total_tests - passed_tests,
        'success_rate': f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
    }
    
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)