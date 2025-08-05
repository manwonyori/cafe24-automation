#!/usr/bin/env python3
"""
Cafe24 Selenium 자동화 메인 실행 파일
"""

import os
import sys
import argparse
import json
from typing import Dict, Any, Optional
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.browser import create_browser_manager
from modules.login import create_login_manager
from modules.price_updater import create_price_updater
from modules.csv_uploader import create_csv_uploader
from utils.logger import setup_logger, create_session_logger
from utils.error_handler import SeleniumErrorHandler, safe_screenshot
from utils.wait_helper import create_wait_helper

# 메인 로거 설정
logger = setup_logger(__name__)


class Cafe24SeleniumAutomation:
    """Cafe24 Selenium 자동화 메인 클래스"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        """
        자동화 시스템 초기화
        
        Args:
            config_path: 설정 파일 경로
        """
        self.config = self._load_config(config_path)
        self.browser_manager = None
        self.login_manager = None
        self.price_updater = None
        self.csv_uploader = None
        self.wait_helper = None
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"설정 파일 로드 완료: {config_path}")
            return config
        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")
            # 기본 설정 반환
            return {
                "browser": {"headless": False},
                "cafe24": {"admin_url": "https://manwonyori.cafe24.com/admin"}
            }
    
    def initialize(self, headless: bool = None) -> bool:
        """시스템 초기화"""
        try:
            logger.info("=== Cafe24 Selenium 자동화 시스템 초기화 ===")
            
            # 브라우저 매니저 생성
            self.browser_manager = create_browser_manager()
            
            # 브라우저 시작
            browser_headless = headless if headless is not None else self.config.get("browser", {}).get("headless", False)
            self.browser_manager.create_driver(headless=browser_headless, undetected=True)
            
            # 로그인 매니저 생성
            self.login_manager = create_login_manager(self.browser_manager)
            
            # 가격 수정 매니저 생성
            self.price_updater = create_price_updater(self.browser_manager, self.login_manager)
            
            # CSV 업로더 생성
            self.csv_uploader = create_csv_uploader(self.browser_manager, self.login_manager)
            
            # 대기 헬퍼 생성
            self.wait_helper = create_wait_helper(self.browser_manager)
            
            logger.info("시스템 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"시스템 초기화 실패: {e}")
            return False
    
    def cleanup(self):
        """시스템 정리"""
        try:
            if self.browser_manager:
                self.browser_manager.close()
            logger.info("시스템 정리 완료")
        except Exception as e:
            logger.error(f"시스템 정리 중 오류: {e}")
    
    @SeleniumErrorHandler.handle_common_errors
    def login(self, force_relogin: bool = False) -> Dict[str, Any]:
        """로그인 실행"""
        if not self.login_manager:
            return {"success": False, "error": "시스템이 초기화되지 않았습니다"}
        
        success = self.login_manager.login(force_relogin=force_relogin)
        
        if success:
            return {"success": True, "message": "로그인 성공"}
        else:
            safe_screenshot(self.browser_manager, "login_failed")
            return {"success": False, "error": "로그인 실패"}
    
    @SeleniumErrorHandler.handle_common_errors
    def update_price_csv(self, csv_file_path: str) -> Dict[str, Any]:
        """CSV 파일을 이용한 가격 수정"""
        if not self.price_updater:
            return {"success": False, "error": "시스템이 초기화되지 않았습니다"}
        
        # 파일 존재 확인
        if not os.path.exists(csv_file_path):
            return {"success": False, "error": f"CSV 파일을 찾을 수 없습니다: {csv_file_path}"}
        
        return self.price_updater.update_prices_from_csv(csv_file_path)
    
    @SeleniumErrorHandler.handle_common_errors
    def update_single_price(self, product_code: str, new_price: str) -> Dict[str, Any]:
        """단일 상품 가격 수정"""
        if not self.price_updater:
            return {"success": False, "error": "시스템이 초기화되지 않았습니다"}
        
        return self.price_updater.update_single_price(product_code, new_price)
    
    @SeleniumErrorHandler.handle_common_errors
    def upload_csv(self, csv_file_path: str, upload_type: str = "modify") -> Dict[str, Any]:
        """CSV 파일 업로드"""
        if not self.csv_uploader:
            return {"success": False, "error": "시스템이 초기화되지 않았습니다"}
        
        return self.csv_uploader.upload_product_csv(csv_file_path, upload_type)
    
    def create_sample_csv(self, output_path: str = "data/csv/sample_price_update.csv") -> str:
        """샘플 CSV 파일 생성"""
        try:
            # 디렉토리 생성
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 샘플 데이터
            sample_data = {
                "P00000IB": "13500",  # 점보떡볶이
                "P00000IC": "25000",  # 샘플 상품 2
                "P00000ID": "30000"   # 샘플 상품 3
            }
            
            csv_path = self.csv_uploader.create_price_update_csv(sample_data, output_path)
            logger.info(f"샘플 CSV 파일 생성: {csv_path}")
            return csv_path
            
        except Exception as e:
            logger.error(f"샘플 CSV 생성 실패: {e}")
            raise


def parse_arguments():
    """명령행 인수 파싱"""
    parser = argparse.ArgumentParser(
        description="Cafe24 Selenium 자동화 시스템",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예제:
  python main.py --task login
  python main.py --task price_update --csv data/csv/price_list.csv
  python main.py --task single_price --product-code P00000IB --price 13500
  python main.py --task csv_upload --csv data/csv/new_products.csv --upload-type register
  python main.py --task create_sample
        """
    )
    
    parser.add_argument(
        "--task", 
        required=True,
        choices=["login", "price_update", "single_price", "csv_upload", "create_sample"],
        help="실행할 작업"
    )
    
    parser.add_argument(
        "--csv", 
        help="CSV 파일 경로"
    )
    
    parser.add_argument(
        "--product-code", 
        help="상품 코드 (single_price 작업용)"
    )
    
    parser.add_argument(
        "--price", 
        help="새로운 가격 (single_price 작업용)"
    )
    
    parser.add_argument(
        "--upload-type", 
        choices=["modify", "register"],
        default="modify",
        help="CSV 업로드 타입 (modify: 수정, register: 등록)"
    )
    
    parser.add_argument(
        "--headless", 
        action="store_true",
        help="헤드리스 모드로 실행"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="디버그 모드"
    )
    
    parser.add_argument(
        "--screenshot", 
        action="store_true",
        help="스크린샷 저장"
    )
    
    parser.add_argument(
        "--config", 
        default="config/settings.json",
        help="설정 파일 경로"
    )
    
    return parser.parse_args()


def main():
    """메인 실행 함수"""
    # 명령행 인수 파싱
    args = parse_arguments()
    
    # 세션 로거 생성
    session_logger = create_session_logger()
    
    # 자동화 시스템 생성
    automation = Cafe24SeleniumAutomation(args.config)
    
    try:
        # 시스템 초기화
        if not automation.initialize(headless=args.headless):
            session_logger.error("시스템 초기화 실패")
            return 1
        
        # 작업 실행
        result = None
        
        if args.task == "login":
            session_logger.info("로그인 작업 시작")
            result = automation.login()
            
        elif args.task == "price_update":
            if not args.csv:
                session_logger.error("CSV 파일 경로가 필요합니다 (--csv)")
                return 1
            
            session_logger.info(f"가격 수정 작업 시작: {args.csv}")
            result = automation.update_price_csv(args.csv)
            
        elif args.task == "single_price":
            if not args.product_code or not args.price:
                session_logger.error("상품 코드와 가격이 필요합니다 (--product-code, --price)")
                return 1
            
            session_logger.info(f"단일 가격 수정: {args.product_code} → {args.price}원")
            result = automation.update_single_price(args.product_code, args.price)
            
        elif args.task == "csv_upload":
            if not args.csv:
                session_logger.error("CSV 파일 경로가 필요합니다 (--csv)")
                return 1
            
            session_logger.info(f"CSV 업로드 작업 시작: {args.csv} ({args.upload_type})")
            result = automation.upload_csv(args.csv, args.upload_type)
            
        elif args.task == "create_sample":
            session_logger.info("샘플 CSV 파일 생성")
            csv_path = automation.create_sample_csv()
            result = {"success": True, "csv_path": csv_path}
        
        # 결과 출력
        if result:
            if result.get("success"):
                session_logger.info("✅ 작업 완료!")
                if args.task == "price_update" and "results" in result:
                    session_logger.info(f"처리 결과: {result['success_count']}/{result['total_count']} 성공")
                elif args.task == "create_sample":
                    session_logger.info(f"샘플 파일 생성: {result['csv_path']}")
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                session_logger.error(f"❌ 작업 실패: {result.get('error', '알 수 없는 오류')}")
                if args.screenshot:
                    safe_screenshot(automation.browser_manager, "task_failed")
                return 1
        else:
            session_logger.error("작업 결과를 가져올 수 없습니다")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        session_logger.info("사용자에 의해 중단됨")
        return 1
        
    except Exception as e:
        session_logger.error(f"예상치 못한 오류: {e}")
        if args.debug:
            import traceback
            session_logger.error(traceback.format_exc())
        
        if args.screenshot:
            safe_screenshot(automation.browser_manager, "unexpected_error")
        
        return 1
        
    finally:
        # 시스템 정리
        automation.cleanup()
        session_logger.info("=== Selenium 자동화 세션 종료 ===")


if __name__ == "__main__":
    sys.exit(main())