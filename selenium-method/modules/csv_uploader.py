"""
CSV 업로드 자동화 모듈
카페24 관리자 페이지에서 CSV 파일을 자동으로 업로드
"""

import os
import time
import pandas as pd
from typing import Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from modules.browser import BrowserManager
from modules.login import LoginManager
from utils.logger import setup_logger, log_execution_time, LogContext

logger = setup_logger(__name__)


class CSVUploader:
    """CSV 업로드 자동화 클래스"""
    
    def __init__(self, browser_manager: BrowserManager, login_manager: LoginManager):
        """
        CSV 업로더 초기화
        
        Args:
            browser_manager: 브라우저 매니저 인스턴스
            login_manager: 로그인 매니저 인스턴스
        """
        self.browser = browser_manager
        self.login = login_manager
        
    @log_execution_time
    def upload_product_csv(self, csv_file_path: str, upload_type: str = "modify") -> Dict[str, Any]:
        """
        상품 CSV 파일 업로드
        
        Args:
            csv_file_path: 업로드할 CSV 파일 경로
            upload_type: 업로드 타입 ("modify": 수정, "register": 등록)
            
        Returns:
            실행 결과 딕셔너리
        """
        with LogContext(logger, f"CSV 업로드: {csv_file_path} ({upload_type})"):
            try:
                # 로그인 확인
                if not self.login.ensure_logged_in():
                    return {"success": False, "error": "로그인 실패"}
                
                # CSV 파일 존재 확인
                if not os.path.exists(csv_file_path):
                    return {"success": False, "error": f"CSV 파일을 찾을 수 없습니다: {csv_file_path}"}
                
                # CSV 업로드 페이지로 이동
                if not self._navigate_to_csv_upload_page():
                    return {"success": False, "error": "CSV 업로드 페이지 이동 실패"}
                
                # 업로드 타입 선택
                if not self._select_upload_type(upload_type):
                    return {"success": False, "error": "업로드 타입 선택 실패"}
                
                # 파일 업로드
                if not self._upload_file(csv_file_path):
                    return {"success": False, "error": "파일 업로드 실패"}
                
                # 업로드 실행
                result = self._execute_upload()
                
                if result["success"]:
                    logger.info(f"CSV 업로드 성공: {csv_file_path}")
                    return {
                        "success": True,
                        "message": "CSV 업로드 완료",
                        "processed_count": result.get("processed_count", 0),
                        "details": result.get("details", [])
                    }
                else:
                    return {"success": False, "error": result.get("error", "업로드 실행 실패")}
                    
            except Exception as e:
                logger.error(f"CSV 업로드 중 오류: {e}")
                self.browser.take_screenshot("csv_upload_error.png")
                return {"success": False, "error": str(e)}
    
    def _navigate_to_csv_upload_page(self) -> bool:
        """CSV 업로드 페이지로 이동"""
        try:
            # 직접 URL로 이동
            mall_id = self.login.credentials["cafe24"]["mall_id"]
            csv_upload_url = f"https://{mall_id}.cafe24.com/admin/php/shop1/p/product_csv_upload.php"
            
            logger.info(f"CSV 업로드 페이지로 이동: {csv_upload_url}")
            self.browser.navigate_to(csv_upload_url)
            
            # 페이지 로딩 대기
            time.sleep(3)
            
            # CSV 업로드 페이지 확인
            current_url = self.browser.get_current_url()
            if "csv_upload" in current_url or "csv" in current_url:
                logger.info("CSV 업로드 페이지 이동 성공")
                return True
            else:
                logger.warning(f"CSV 업로드 페이지 확인 실패. 현재 URL: {current_url}")
                
                # 메뉴에서 CSV 업로드 찾아서 이동
                return self._find_and_click_csv_menu()
                
        except Exception as e:
            logger.error(f"CSV 업로드 페이지 이동 중 오류: {e}")
            return False
    
    def _find_and_click_csv_menu(self) -> bool:
        """메뉴에서 CSV 업로드 링크 찾기"""
        try:
            csv_menu_selectors = [
                (By.XPATH, "//a[contains(text(), 'CSV') and (contains(text(), '업로드') or contains(text(), '등록'))]"),
                (By.XPATH, "//a[contains(@href, 'csv_upload')]"),
                (By.XPATH, "//a[contains(@href, 'csv') and contains(@href, 'product')]"),
                (By.CSS_SELECTOR, "a[href*='csv']"),
            ]
            
            for selector in csv_menu_selectors:
                try:
                    elements = self.browser.driver.find_elements(*selector)
                    for element in elements:
                        if element.is_displayed():
                            logger.info(f"CSV 메뉴 찾음: {element.text}")
                            element.click()
                            time.sleep(3)
                            return True
                except (NoSuchElementException, TimeoutException):
                    continue
            
            logger.error("CSV 업로드 메뉴를 찾을 수 없습니다.")
            return False
            
        except Exception as e:
            logger.error(f"CSV 메뉴 찾기 중 오류: {e}")
            return False
    
    def _select_upload_type(self, upload_type: str) -> bool:
        """업로드 타입 선택"""
        try:
            if upload_type == "modify":
                # 상품 수정 라디오 버튼 선택
                modify_selectors = [
                    (By.XPATH, "//input[@type='radio' and (@value='modify' or @value='update')]"),
                    (By.XPATH, "//input[@type='radio']//following-sibling::text()[contains(., '수정')]//preceding-sibling::input"),
                    (By.XPATH, "//label[contains(text(), '수정')]//input[@type='radio']")
                ]
            else:  # register
                # 상품 등록 라디오 버튼 선택
                modify_selectors = [
                    (By.XPATH, "//input[@type='radio' and (@value='register' or @value='add')]"),
                    (By.XPATH, "//input[@type='radio']//following-sibling::text()[contains(., '등록')]//preceding-sibling::input"),
                    (By.XPATH, "//label[contains(text(), '등록')]//input[@type='radio']")
                ]
            
            radio_button = None
            for selector in modify_selectors:
                try:
                    radio_button = self.browser.wait_for_element(selector, timeout=3)
                    if radio_button and radio_button.is_displayed():
                        break
                except TimeoutException:
                    continue
            
            if radio_button:
                if not radio_button.is_selected():
                    radio_button.click()
                    logger.info(f"업로드 타입 선택: {upload_type}")
                return True
            else:
                logger.warning(f"업로드 타입 선택 버튼을 찾을 수 없습니다: {upload_type}")
                return True  # 기본값으로 진행
                
        except Exception as e:
            logger.error(f"업로드 타입 선택 중 오류: {e}")
            return True  # 기본값으로 진행
    
    def _upload_file(self, csv_file_path: str) -> bool:
        """파일 업로드"""
        try:
            # 파일 입력 필드 찾기
            file_input_selectors = [
                (By.CSS_SELECTOR, "input[type='file']"),
                (By.XPATH, "//input[@type='file']"),
                (By.NAME, "csv_file"),
                (By.NAME, "upload_file"),
                (By.NAME, "file")
            ]
            
            file_input = None
            for selector in file_input_selectors:
                try:
                    file_input = self.browser.wait_for_element(selector, timeout=3)
                    if file_input:
                        break
                except TimeoutException:
                    continue
            
            if not file_input:
                logger.error("파일 업로드 입력 필드를 찾을 수 없습니다.")
                self.browser.take_screenshot("file_input_not_found.png")
                return False
            
            # 파일 경로를 절대 경로로 변환
            abs_file_path = os.path.abspath(csv_file_path)
            
            # 파일 선택
            file_input.send_keys(abs_file_path)
            logger.info(f"파일 선택 완료: {abs_file_path}")
            
            # 파일 선택 후 잠시 대기
            time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"파일 업로드 중 오류: {e}")
            return False
    
    def _execute_upload(self) -> Dict[str, Any]:
        """업로드 실행"""
        try:
            # 업로드 버튼 찾기
            upload_button_selectors = [
                (By.CSS_SELECTOR, "input[type='submit'][value*='업로드']"),
                (By.CSS_SELECTOR, "input[type='submit'][value*='등록']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//input[@type='submit' and (contains(@value, '업로드') or contains(@value, '등록') or contains(@value, '실행'))]"),
                (By.XPATH, "//button[contains(text(), '업로드') or contains(text(), '등록') or contains(text(), '실행')]")
            ]
            
            upload_button = None
            for selector in upload_button_selectors:
                try:
                    upload_button = self.browser.wait_for_element(selector, timeout=3)
                    if upload_button and upload_button.is_displayed():
                        break
                except TimeoutException:
                    continue
            
            if not upload_button:
                logger.error("업로드 버튼을 찾을 수 없습니다.")
                self.browser.take_screenshot("upload_button_not_found.png")
                return {"success": False, "error": "업로드 버튼을 찾을 수 없음"}
            
            # 업로드 버튼 클릭
            self.browser.scroll_to_element(upload_button)
            time.sleep(0.5)
            upload_button.click()
            logger.info("업로드 버튼 클릭")
            
            # 업로드 처리 대기 (CSV 파일 크기에 따라 시간이 걸릴 수 있음)
            logger.info("CSV 처리 중... (최대 5분 대기)")
            
            # 처리 완료 대기
            return self._wait_for_upload_completion()
            
        except Exception as e:
            logger.error(f"업로드 실행 중 오류: {e}")
            return {"success": False, "error": str(e)}
    
    def _wait_for_upload_completion(self) -> Dict[str, Any]:
        """업로드 완료 대기"""
        try:
            # 최대 5분 대기
            max_wait_time = 300  # 5분
            check_interval = 10   # 10초마다 확인
            
            for i in range(0, max_wait_time, check_interval):
                time.sleep(check_interval)
                
                current_url = self.browser.get_current_url()
                page_source = self.browser.get_page_source()
                
                # 성공 메시지 확인
                success_keywords = ["완료", "성공", "등록되었습니다", "처리되었습니다", "success"]
                if any(keyword in page_source for keyword in success_keywords):
                    logger.info("업로드 성공 메시지 확인")
                    
                    # 처리된 건수 추출 시도
                    processed_count = self._extract_processed_count(page_source)
                    
                    return {
                        "success": True,
                        "processed_count": processed_count,
                        "message": "업로드 완료"
                    }
                
                # 에러 메시지 확인
                error_keywords = ["오류", "실패", "error", "fail", "잘못"]
                if any(keyword in page_source for keyword in error_keywords):
                    logger.error("업로드 실패 메시지 확인")
                    self.browser.take_screenshot("upload_error.png")
                    return {
                        "success": False,
                        "error": "업로드 처리 중 오류 발생"
                    }
                
                # 진행 중인지 확인
                processing_keywords = ["처리중", "진행중", "loading", "processing"]
                if any(keyword in page_source for keyword in processing_keywords):
                    logger.info(f"처리 중... ({i//60}분 {i%60}초 경과)")
                    continue
                
                logger.info(f"업로드 상태 확인 중... ({i//60}분 {i%60}초 경과)")
            
            # 타임아웃
            logger.warning("업로드 완료 대기 시간 초과")
            self.browser.take_screenshot("upload_timeout.png")
            
            return {
                "success": False,
                "error": "업로드 처리 시간 초과 (5분)"
            }
            
        except Exception as e:
            logger.error(f"업로드 완료 대기 중 오류: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_processed_count(self, page_source: str) -> int:
        """처리된 건수 추출"""
        try:
            import re
            
            # 숫자 패턴 찾기
            patterns = [
                r'(\d+)\s*건.*처리',
                r'(\d+)\s*개.*등록',
                r'(\d+)\s*건.*완료',
                r'총\s*(\d+)\s*건'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, page_source)
                if matches:
                    return int(matches[0])
            
            return 0
            
        except Exception as e:
            logger.error(f"처리 건수 추출 중 오류: {e}")
            return 0
    
    def create_price_update_csv(self, price_data: Dict[str, str], output_path: str = None) -> str:
        """
        가격 수정용 CSV 파일 생성
        
        Args:
            price_data: {상품코드: 가격} 딕셔너리
            output_path: 출력 파일 경로 (None이면 자동 생성)
            
        Returns:
            생성된 CSV 파일 경로
        """
        try:
            if output_path is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"data/csv/price_update_{timestamp}.csv"
            
            # 디렉토리 생성
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # DataFrame 생성
            df = pd.DataFrame([
                {"상품코드": code, "판매가": price}
                for code, price in price_data.items()
            ])
            
            # CSV 저장
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            logger.info(f"가격 수정 CSV 생성: {output_path} ({len(df)}건)")
            
            return output_path
            
        except Exception as e:
            logger.error(f"CSV 파일 생성 중 오류: {e}")
            raise
    
    def validate_csv_format(self, csv_file_path: str, required_columns: list = None) -> Dict[str, Any]:
        """
        CSV 파일 형식 검증
        
        Args:
            csv_file_path: CSV 파일 경로
            required_columns: 필수 컬럼 목록
            
        Returns:
            검증 결과
        """
        try:
            if required_columns is None:
                required_columns = ["상품코드", "판매가"]
            
            # CSV 파일 읽기
            df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
            
            # 컬럼 확인
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return {
                    "valid": False,
                    "error": f"필수 컬럼 누락: {missing_columns}",
                    "current_columns": list(df.columns)
                }
            
            # 데이터 검증
            empty_rows = df.isnull().any(axis=1).sum()
            
            return {
                "valid": True,
                "row_count": len(df),
                "empty_rows": empty_rows,
                "columns": list(df.columns)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }


def create_csv_uploader(browser_manager: BrowserManager, login_manager: LoginManager) -> CSVUploader:
    """
    CSV 업로더 생성 팩토리 함수
    
    Args:
        browser_manager: 브라우저 매니저 인스턴스
        login_manager: 로그인 매니저 인스턴스
        
    Returns:
        CSVUploader 인스턴스
    """
    return CSVUploader(browser_manager, login_manager)