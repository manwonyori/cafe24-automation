#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 System - Main integration module
Handles all core functionality with improved architecture
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .api_client import Cafe24APIClient
from .nlp_processor import NaturalLanguageProcessor
from .cache_manager import CacheManager
from .utils.health_checker import HealthChecker
from .utils.report_generator import ReportGenerator


class Cafe24System:
    """Main Cafe24 automation system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the system with configuration"""
        self.config = self._load_config(config_path)
        self._setup_logging()
        
        # Verify environment
        self._check_environment()
        
        # Initialize components
        self.api_client = Cafe24APIClient(self.config)
        self.nlp_processor = NaturalLanguageProcessor()
        self.cache_manager = CacheManager(self.config.get('cache', {}))
        self.health_checker = HealthChecker()
        self.report_generator = ReportGenerator()
        
        self.logger.info("Cafe24 System initialized successfully")
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from file or environment"""
        config = {
            'mall_id': os.getenv('CAFE24_MALL_ID'),
            'client_id': os.getenv('CAFE24_CLIENT_ID'),
            'client_secret': os.getenv('CAFE24_CLIENT_SECRET'),
            'api_version': os.getenv('CAFE24_API_VERSION', '2025-06-01'),
            'cache': {
                'enabled': os.getenv('CAFE24_CACHE_ENABLED', 'true').lower() == 'true',
                'ttl': int(os.getenv('CAFE24_CACHE_TTL', '3600'))
            },
            'retry': {
                'count': int(os.getenv('CAFE24_RETRY_COUNT', '3')),
                'delay': int(os.getenv('CAFE24_RETRY_DELAY', '2'))
            },
            'log_level': os.getenv('CAFE24_LOG_LEVEL', 'INFO')
        }
        
        # Load from config file if provided
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                config.update(file_config)
                
        return config
        
    def _setup_logging(self):
        """Configure logging"""
        log_level = getattr(logging, self.config['log_level'])
        log_file = os.getenv('CAFE24_LOG_FILE', 'logs/cafe24_system.log')
        
        # Create logs directory if needed
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configure logger
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('Cafe24System')
        
    def _check_environment(self):
        """Check and prepare environment"""
        # Check Python version
        if sys.version_info < (3, 8):
            raise EnvironmentError("Python 3.8+ required")
            
        # Check required packages
        required_packages = [
            'requests', 'pandas', 'flask', 'python-dotenv'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing.append(package)
                
        if missing:
            self.logger.warning(f"Missing packages: {', '.join(missing)}")
            # Auto-install if allowed
            if os.getenv('CAFE24_AUTO_INSTALL', 'false').lower() == 'true':
                import subprocess
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
                
    def execute(self, command: str) -> Dict[str, Any]:
        """Execute a natural language command"""
        try:
            # Process natural language
            intent = self.nlp_processor.process(command)
            
            if not intent:
                return {
                    'success': False,
                    'error': 'Command not understood',
                    'command': command
                }
                
            # Execute based on intent
            result = self._execute_intent(intent)
            
            return {
                'success': True,
                'command': command,
                'intent': intent,
                'result': result
            }
            
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'command': command
            }
            
    def _execute_intent(self, intent: Dict[str, Any]) -> Any:
        """Execute the identified intent"""
        action = intent.get('action')
        params = intent.get('params', {})
        
        # Map actions to methods
        action_map = {
            'get_products': self.get_products,
            'get_orders': self.get_orders,
            'check_inventory': self.check_inventory,
            'generate_report': self.generate_report,
            'update_products': self.update_products,
            'check_health': self.check_system_health
        }
        
        if action in action_map:
            return action_map[action](**params)
        else:
            raise ValueError(f"Unknown action: {action}")
            
    def get_products(self, **kwargs) -> List[Dict]:
        """Get products with caching"""
        # Check cache first
        cache_key = f"products:{json.dumps(kwargs, sort_keys=True)}"
        cached = self.cache_manager.get(cache_key)
        
        if cached:
            self.logger.info("Products retrieved from cache")
            return cached
            
        # Fetch from API
        products = self.api_client.get_products(**kwargs)
        
        # Cache the results
        self.cache_manager.set(cache_key, products)
        
        return products
        
    def get_orders(self, start_date: Optional[str] = None, 
                   end_date: Optional[str] = None, **kwargs) -> List[Dict]:
        """Get orders with date filtering"""
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        if not end_date:
            end_date = start_date
            
        return self.api_client.get_orders(
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )
        
    def check_inventory(self, threshold: int = 10) -> Dict[str, Any]:
        """Check inventory levels"""
        products = self.get_products()
        
        low_stock = []
        out_of_stock = []
        
        for product in products:
            quantity = product.get('inventory_quantity', 0)
            if quantity == 0:
                out_of_stock.append(product)
            elif quantity < threshold:
                low_stock.append(product)
                
        return {
            'low_stock': low_stock,
            'out_of_stock': out_of_stock,
            'total_products': len(products),
            'threshold': threshold
        }
        
    def update_products(self, updates: List[Dict]) -> Dict[str, Any]:
        """Batch update products"""
        results = {
            'success': [],
            'failed': [],
            'total': len(updates)
        }
        
        for update in updates:
            try:
                result = self.api_client.update_product(
                    update['product_no'],
                    update['data']
                )
                results['success'].append(update['product_no'])
            except Exception as e:
                results['failed'].append({
                    'product_no': update['product_no'],
                    'error': str(e)
                })
                
        return results
        
    def generate_report(self, report_type: str = 'daily') -> Dict[str, Any]:
        """Generate various reports"""
        if report_type == 'daily':
            return self.report_generator.generate_daily_report(self)
        elif report_type == 'inventory':
            return self.report_generator.generate_inventory_report(self)
        elif report_type == 'sales':
            return self.report_generator.generate_sales_report(self)
        else:
            raise ValueError(f"Unknown report type: {report_type}")
            
    def check_system_health(self) -> Dict[str, Any]:
        """Run system health checks"""
        checks = {
            'api_connection': self.health_checker.check_api_connection(self.api_client),
            'cache_status': self.health_checker.check_cache(self.cache_manager),
            'environment': self.health_checker.check_environment(),
            'dependencies': self.health_checker.check_dependencies()
        }
        
        all_passed = all(check['passed'] for check in checks.values())
        
        return {
            'status': 'healthy' if all_passed else 'unhealthy',
            'checks': checks,
            'timestamp': datetime.now().isoformat()
        }