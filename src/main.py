#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 Automation System - Main Entry Point
"""

import os
import sys
import argparse
import logging
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cafe24_system import Cafe24System


def setup_logging(log_level: str = 'INFO'):
    """Configure logging for the application"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def interactive_mode(system: Cafe24System):
    """Run in interactive mode"""
    print("\n" + "="*60)
    print("Cafe24 Automation System - Interactive Mode")
    print("="*60)
    print("\nType 'help' for available commands or 'exit' to quit\n")
    
    while True:
        try:
            command = input("cafe24> ").strip()
            
            if command.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
                
            elif command.lower() == 'help':
                print_help()
                
            elif command.lower() == 'health':
                result = system.check_system_health()
                print(f"\nSystem Status: {result['status']}")
                for check, data in result['checks'].items():
                    status = "PASS" if data.get('passed', False) else "FAIL"
                    print(f"  {check}: [{status}] {data.get('message', '')}")
                print()
                
            elif command:
                # Process natural language command
                result = system.execute(command)
                
                if result['success']:
                    print(f"\nSuccess: {result.get('intent', {}).get('action', 'Unknown action')}")
                    
                    # Display results based on action
                    data = result.get('result')
                    if isinstance(data, list):
                        print(f"Found {len(data)} items")
                        # Show first few items
                        for item in data[:5]:
                            if 'product_name' in item:
                                print(f"  - {item['product_name']} (₩{item.get('price', 0)})")
                            elif 'order_id' in item:
                                print(f"  - Order {item['order_id']} (₩{item.get('total_price', 0)})")
                    elif isinstance(data, dict):
                        for key, value in data.items():
                            print(f"  {key}: {value}")
                else:
                    print(f"\nError: {result.get('error', 'Unknown error')}")
                print()
                
        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'exit' to quit.")
        except Exception as e:
            print(f"\nError: {e}")
            logging.error(f"Interactive mode error: {e}", exc_info=True)


def batch_mode(system: Cafe24System, command: str):
    """Run a single command in batch mode"""
    result = system.execute(command)
    
    if result['success']:
        print(f"Success: {command}")
        # Output result as JSON for scripting
        import json
        print(json.dumps(result['result'], ensure_ascii=False, indent=2))
        return 0
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        return 1


def print_help():
    """Print help message"""
    help_text = """
Available Commands:
===================

Natural Language Commands (Korean):
  - 오늘 신규 주문 보여줘
  - 재고 부족 상품 확인
  - 전체 상품 목록
  - 일일 리포트 생성
  - 시스템 상태 확인

Natural Language Commands (English):
  - Show today's orders
  - Check low stock items
  - List all products
  - Generate daily report
  - Check system health

System Commands:
  - help    : Show this help message
  - health  : Run system health check
  - exit    : Exit the program

Examples:
  cafe24> 오늘 주문 내역 보여줘
  cafe24> 재고 10개 이하인 상품 확인
  cafe24> 이번달 매출 통계
"""
    print(help_text)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Cafe24 Automation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python main.py
  
  # Batch mode
  python main.py -c "오늘 주문 보여줘"
  
  # With custom config
  python main.py --config config/production.json
  
  # Debug mode
  python main.py --log-level DEBUG
"""
    )
    
    parser.add_argument(
        '-c', '--command',
        help='Execute a single command and exit'
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Set logging level'
    )
    
    parser.add_argument(
        '--health-check',
        action='store_true',
        help='Run health check and exit'
    )
    
    parser.add_argument(
        '--web',
        action='store_true',
        help='Run as web service'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    try:
        # Initialize system
        print("Initializing Cafe24 Automation System...")
        system = Cafe24System(config_path=args.config)
        print("System initialized successfully!\n")
        
        # Health check mode
        if args.health_check:
            result = system.check_system_health()
            print(f"System Status: {result['status']}")
            return 0 if result['status'] == 'healthy' else 1
            
        # Web service mode
        if args.web:
            print("Starting web service...")
            from web_app import app
            port = int(os.environ.get('PORT', 5000))
            app.run(host='0.0.0.0', port=port)
            return 0
            
        # Batch mode
        if args.command:
            return batch_mode(system, args.command)
            
        # Interactive mode
        interactive_mode(system)
        return 0
        
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nFatal error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())