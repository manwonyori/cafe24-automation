#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web API for Cafe24 Automation System
Provides REST API and health check endpoints
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cafe24_system import Cafe24System

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Cafe24 system
try:
    system = Cafe24System()
    system_initialized = True
except Exception as e:
    logging.error(f"Failed to initialize Cafe24 system: {e}")
    system_initialized = False
    system = None

@app.route('/')
def home():
    """Home endpoint"""
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
    if not system_initialized:
        return jsonify({'error': 'System not initialized'}), 503
    
    try:
        # Get query parameters
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        display = request.args.get('display')
        selling = request.args.get('selling')
        
        # Build kwargs
        kwargs = {}
        if display:
            kwargs['display'] = display
        if selling:
            kwargs['selling'] = selling
            
        products = system.get_products(limit=limit, offset=offset, **kwargs)
        
        return jsonify({
            'success': True,
            'count': len(products),
            'products': products
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get orders list"""
    if not system_initialized:
        return jsonify({'error': 'System not initialized'}), 503
    
    try:
        start_date = request.args.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', start_date)
        
        orders = system.get_orders(start_date=start_date, end_date=end_date)
        
        return jsonify({
            'success': True,
            'count': len(orders),
            'orders': orders
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/inventory', methods=['GET'])
def check_inventory():
    """Check inventory status"""
    if not system_initialized:
        return jsonify({'error': 'System not initialized'}), 503
    
    try:
        threshold = int(request.args.get('threshold', 10))
        inventory = system.check_inventory(threshold=threshold)
        
        return jsonify({
            'success': True,
            'inventory': inventory
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)