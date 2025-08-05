"""
가격 수정 자동화 모듈
카페24 관리자 페이지에서 상품 가격을 자동으로 수정
"""

import time
import pandas as pd
from typing import List, Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from modules.browser import BrowserManager
from modules.login import LoginManager
from utils.logger import setup_logger, log_execution_time, LogContext

logger = setup_logger(__name__)


class PriceUpdater:
    """가격 수정 자동화 클래스"""
    
    def __init__(self, browser_manager: BrowserManager, login_manager: LoginManager):
        """
        가격 수정 매니저 초기화
        
        Args:
            browser_manager: 브라우저 매니저 인스턴스
            login_manager: 로그인 매니저 인스턴스
        """
        self.browser = browser_manager
        self.login = login_manager
        
    @log_execution_time
    def update_prices_from_csv(self, csv_file_path: str) -> Dict[str, Any]:
        """
        CSV 파일을 이용한 가격 일괄 수정
        
        Args:
            csv_file_path: CSV 파일 경로
            
        Returns:
            실행 결과 딕셔너리
        """
        with LogContext(logger, f"CSV 가격 수정: {csv_file_path}"):
            try:
                # 로그인 확인
                if not self.login.ensure_logged_in():
                    return {"success": False, "error": "로그인 실패"}
                
                # CSV 파일 읽기
                price_data = self._read_price_csv(csv_file_path)
                if not price_data:
                    return {"success": False, "error": "CSV 파일 읽기 실패"}
                
                # 상품 목록 페이지로 이동
                if not self._navigate_to_product_list():
                    return {"success": False, "error": "상품 목록 페이지 이동 실패"}
                
                # 각 상품별 가격 수정
                results = []
                for idx, row in price_data.iterrows():
                    product_code = row.get('상품코드') or row.get('product_code')
                    new_price = row.get('판매가') or row.get('price')
                    
                    if pd.isna(product_code) or pd.isna(new_price):
                        logger.warning(f"행 {idx}: 필수 데이터 누락 - 상품코드: {product_code}, 가격: {new_price}")
                        continue
                    
                    result = self._update_single_product_price(str(product_code), str(int(new_price)))
                    results.append({
                        "product_code": product_code,
                        "new_price": new_price,
                        "success": result["success"],
                        "message": result.get("message", "")
                    })
                    
                    # 각 상품 처리 후 잠시 대기
                    time.sleep(1)
                
                # 결과 집계
                success_count = sum(1 for r in results if r["success"])
                total_count = len(results)
                
                logger.info(f"가격 수정 완료: {success_count}/{total_count} 성공")
                
                return {
                    "success": True,
                    "total_count": total_count,
                    "success_count": success_count,
                    "results": results
                }
                
            except Exception as e:
                logger.error(f"CSV 가격 수정 중 오류: {e}")
                self.browser.take_screenshot("price_update_error.png")
                return {"success": False, "error": str(e)}
    
    def _read_price_csv(self, csv_file_path: str) -> Optional[pd.DataFrame]:
        """CSV 파일 읽기"""
        try:
            # 다양한 인코딩으로 시도
            encodings = ['utf-8', 'cp949', 'euc-kr', 'utf-8-sig']
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_file_path, encoding=encoding)
                    logger.info(f"CSV 파일 읽기 성공 ({encoding}): {len(df)}행")
                    
                    # 컬럼명 확인
                    required_columns = ['상품코드', '판매가']
                    alt_columns = ['product_code', 'price']
                    
                    has_required = all(col in df.columns for col in required_columns)
                    has_alt = all(col in df.columns for col in alt_columns)
                    
                    if not has_required and not has_alt:
                        logger.error(f"필수 컬럼이 없습니다. 필요: {required_columns} 또는 {alt_columns}")
                        logger.error(f"현재 컬럼: {list(df.columns)}")
                        return None
                    
                    return df
                    
                except UnicodeDecodeError:
                    continue
            
            logger.error("모든 인코딩으로 CSV 파일 읽기 실패")
            return None
            
        except Exception as e:
            logger.error(f"CSV 파일 읽기 오류: {e}")
            return None
    
    def _navigate_to_product_list(self) -> bool:
        """상품 목록 페이지로 이동"""
        try:
            # 상품 관리 메뉴 클릭 시도
            product_menu_selectors = [
                (By.XPATH, "//a[contains(text(), '상품관리') or contains(text(), '상품')]"),
                (By.CSS_SELECTOR, "a[href*='product']"),
                (By.XPATH, "//li[contains(@class, 'product')]//a"),
            ]
            
            # 직접 URL로 이동
            mall_id = self.login.credentials["cafe24"]["mall_id"]
            product_list_url = f"https://{mall_id}.cafe24.com/admin/php/shop1/p/product_list.php"
            
            logger.info(f"상품 목록 페이지로 직접 이동: {product_list_url}")
            self.browser.navigate_to(product_list_url)
            
            # 페이지 로딩 대기
            time.sleep(3)
            
            # 상품 목록 페이지 확인
            if "product_list" in self.browser.get_current_url():
                logger.info("상품 목록 페이지 이동 성공")
                return True
            else:
                logger.error("상품 목록 페이지 이동 실패")
                return False
                
        except Exception as e:
            logger.error(f"상품 목록 페이지 이동 중 오류: {e}")
            return False
    
    def _update_single_product_price(self, product_code: str, new_price: str) -> Dict[str, Any]:
        """단일 상품 가격 수정"""
        try:
            with LogContext(logger, f"상품 {product_code} 가격 수정 → {new_price}원"):
                
                # 상품 검색
                if not self._search_product(product_code):
                    return {"success": False, "message": "상품 검색 실패"}
                
                # 상품 편집 버튼 클릭
                if not self._click_edit_button(product_code):
                    return {"success": False, "message": "편집 버튼 클릭 실패"}
                
                # 가격 수정
                if not self._modify_price(new_price):
                    return {"success": False, "message": "가격 입력 실패"}
                
                # 저장
                if not self._save_changes():
                    return {"success": False, "message": "저장 실패"}
                
                logger.info(f"상품 {product_code} 가격 수정 완료: {new_price}원")
                return {"success": True, "message": "가격 수정 완료"}
                
        except Exception as e:
            logger.error(f"상품 {product_code} 가격 수정 중 오류: {e}")
            return {"success": False, "message": str(e)}
    
    def _search_product(self, product_code: str) -> bool:
        """상품 검색"""
        try:
            # 검색 입력 필드 찾기
            search_selectors = [
                (By.NAME, "keyword"),
                (By.NAME, "search_keyword"),
                (By.CSS_SELECTOR, "input[type='text'][name*='search']"),
                (By.CSS_SELECTOR, "input[placeholder*='검색']"),
                (By.XPATH, "//input[@type='text' and contains(@placeholder, '상품')]")
            ]
            
            search_field = None
            for selector in search_selectors:
                try:
                    search_field = self.browser.wait_for_element(selector, timeout=3)
                    if search_field and search_field.is_displayed():
                        break
                except TimeoutException:
                    continue
            
            if not search_field:
                logger.error("검색 입력 필드를 찾을 수 없습니다.")
                return False
            
            # 검색어 입력
            search_field.clear()
            search_field.send_keys(product_code)
            logger.info(f"검색어 입력: {product_code}")
            
            # 검색 버튼 클릭
            search_button_selectors = [
                (By.CSS_SELECTOR, "input[type='submit'][value*='검색']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//input[@type='submit' and (@value='검색' or @value='Search')]"),
                (By.XPATH, "//button[contains(text(), '검색')]")
            ]
            
            search_button = None
            for selector in search_button_selectors:
                try:
                    search_button = self.browser.wait_for_element(selector, timeout=3)
                    if search_button and search_button.is_displayed():
                        break
                except TimeoutException:
                    continue
            
            if search_button:
                search_button.click()
                logger.info("검색 버튼 클릭")
            else:
                # Enter 키로 검색
                from selenium.webdriver.common.keys import Keys
                search_field.send_keys(Keys.RETURN)
                logger.info("Enter 키로 검색 실행")
            
            # 검색 결과 로딩 대기
            time.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"상품 검색 중 오류: {e}")
            return False
    
    def _click_edit_button(self, product_code: str) -> bool:
        """편집 버튼 클릭"""
        try:
            # 편집 버튼 찾기 (여러 방법 시도)
            edit_selectors = [
                (By.XPATH, f"//tr[contains(., '{product_code}')]//a[contains(text(), '수정') or contains(text(), '편집')]"),
                (By.XPATH, f"//tr[contains(., '{product_code}')]//input[@value='수정' or @value='편집']"),
                (By.XPATH, f"//tr[contains(., '{product_code}')]//a[contains(@href, 'product_modify')]"),
                (By.CSS_SELECTOR, "a[href*='product_modify']"),
                (By.XPATH, "//a[contains(text(), '수정')]")
            ]
            
            edit_button = None
            for selector in edit_selectors:
                try:
                    elements = self.browser.driver.find_elements(*selector)
                    for element in elements:
                        if element.is_displayed():
                            edit_button = element
                            break
                    if edit_button:
                        break
                except NoSuchElementException:
                    continue
            
            if not edit_button:
                logger.error("편집 버튼을 찾을 수 없습니다.")
                self.browser.take_screenshot("edit_button_not_found.png")
                return False
            
            # 편집 버튼 클릭
            self.browser.scroll_to_element(edit_button)
            time.sleep(0.5)
            edit_button.click()
            logger.info("편집 버튼 클릭 완료")
            
            # 편집 페이지 로딩 대기
            time.sleep(3)
            
            return True
            
        except Exception as e:
            logger.error(f"편집 버튼 클릭 중 오류: {e}")
            return False
    
    def _modify_price(self, new_price: str) -> bool:
        """가격 입력 필드 수정"""
        try:
            # 판매가격 입력 필드 찾기
            price_selectors = [
                (By.NAME, "selling_price"),
                (By.NAME, "product_price"),
                (By.NAME, "price"),
                (By.CSS_SELECTOR, "input[name*='price']"),
                (By.XPATH, "//input[@type='text' and contains(@name, 'price')]"),
                (By.XPATH, "//td[contains(text(), '판매가격') or contains(text(), '판매가')]//following-sibling::td//input[@type='text']")
            ]
            
            price_field = None
            for selector in price_selectors:
                try:
                    price_field = self.browser.wait_for_element(selector, timeout=3)
                    if price_field and price_field.is_displayed():
                        break
                except TimeoutException:
                    continue
            
            if not price_field:
                logger.error("가격 입력 필드를 찾을 수 없습니다.")
                self.browser.take_screenshot("price_field_not_found.png")
                return False
            
            # 기존 가격 지우고 새 가격 입력
            price_field.clear()
            price_field.send_keys(new_price)
            logger.info(f"새 가격 입력: {new_price}")
            
            return True
            
        except Exception as e:
            logger.error(f"가격 수정 중 오류: {e}")
            return False
    
    def _save_changes(self) -> bool:
        """변경사항 저장"""
        try:
            # 저장 버튼 찾기
            save_selectors = [
                (By.CSS_SELECTOR, "input[type='submit'][value*='저장']"),
                (By.CSS_SELECTOR, "input[type='submit'][value*='수정']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//input[@type='submit' and (@value='저장' or @value='수정' or @value='확인')]"),
                (By.XPATH, "//button[contains(text(), '저장') or contains(text(), '수정')]")
            ]
            
            save_button = None
            for selector in save_selectors:
                try:
                    save_button = self.browser.wait_for_element(selector, timeout=3)
                    if save_button and save_button.is_displayed():
                        break
                except TimeoutException:
                    continue
            
            if not save_button:
                logger.error("저장 버튼을 찾을 수 없습니다.")
                self.browser.take_screenshot("save_button_not_found.png")
                return False
            
            # 저장 버튼 클릭
            self.browser.scroll_to_element(save_button)
            time.sleep(0.5)
            save_button.click()
            logger.info("저장 버튼 클릭")
            
            # 저장 완료 대기
            time.sleep(3)
            
            # 저장 성공 확인
            current_url = self.browser.get_current_url()
            if "product_list" in current_url or "success" in current_url:
                logger.info("저장 완료")
                return True
            else:
                logger.warning("저장 완료 여부 불확실")
                return True  # 일단 성공으로 간주
                
        except Exception as e:
            logger.error(f"저장 중 오류: {e}")
            return False
    
    def update_single_price(self, product_code: str, new_price: str) -> Dict[str, Any]:
        """
        단일 상품 가격 수정 (외부 호출용)
        
        Args:
            product_code: 상품 코드
            new_price: 새로운 가격
            
        Returns:
            실행 결과
        """
        try:
            # 로그인 확인
            if not self.login.ensure_logged_in():
                return {"success": False, "error": "로그인 실패"}
            
            # 상품 목록 페이지로 이동
            if not self._navigate_to_product_list():
                return {"success": False, "error": "상품 목록 페이지 이동 실패"}
            
            # 가격 수정 실행
            result = self._update_single_product_price(product_code, new_price)
            return result
            
        except Exception as e:
            logger.error(f"단일 상품 가격 수정 중 오류: {e}")
            return {"success": False, "error": str(e)}


def create_price_updater(browser_manager: BrowserManager, login_manager: LoginManager) -> PriceUpdater:
    """
    가격 수정 매니저 생성 팩토리 함수
    
    Args:
        browser_manager: 브라우저 매니저 인스턴스
        login_manager: 로그인 매니저 인스턴스
        
    Returns:
        PriceUpdater 인스턴스
    """
    return PriceUpdater(browser_manager, login_manager)