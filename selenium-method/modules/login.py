"""
카페24 관리자 로그인 자동화 모듈
"""

import os
import json
import time
from typing import Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from modules.browser import BrowserManager
from utils.logger import setup_logger, log_execution_time, LogContext

logger = setup_logger(__name__)


class LoginManager:
    """카페24 관리자 로그인 관리 클래스"""
    
    def __init__(self, browser_manager: BrowserManager, credentials_path: str = "config/credentials.json"):
        """
        로그인 매니저 초기화
        
        Args:
            browser_manager: 브라우저 매니저 인스턴스
            credentials_path: 인증 정보 파일 경로
        """
        self.browser = browser_manager
        self.credentials = self._load_credentials(credentials_path)
        self.is_logged_in = False
        
    def _load_credentials(self, credentials_path: str) -> Dict[str, Any]:
        """인증 정보 로드"""
        try:
            # 파일에서 로드
            if os.path.exists(credentials_path):
                with open(credentials_path, 'r', encoding='utf-8') as f:
                    credentials = json.load(f)
                logger.info(f"인증 정보 파일 로드: {credentials_path}")
                return credentials
            
            # 환경변수에서 로드
            credentials = {
                "cafe24": {
                    "admin_id": os.getenv("CAFE24_ADMIN_ID"),
                    "admin_password": os.getenv("CAFE24_ADMIN_PASSWORD"),
                    "mall_id": os.getenv("CAFE24_MALL_ID", "manwonyori")
                }
            }
            
            if credentials["cafe24"]["admin_id"] and credentials["cafe24"]["admin_password"]:
                logger.info("환경변수에서 인증 정보 로드")
                return credentials
            
            raise ValueError("인증 정보를 찾을 수 없습니다.")
            
        except Exception as e:
            logger.error(f"인증 정보 로드 실패: {e}")
            raise
    
    @log_execution_time
    def login(self, force_relogin: bool = False) -> bool:
        """
        카페24 관리자 로그인
        
        Args:
            force_relogin: 강제 재로그인 여부
            
        Returns:
            로그인 성공 여부
        """
        if self.is_logged_in and not force_relogin:
            logger.info("이미 로그인되어 있습니다.")
            return True
        
        with LogContext(logger, "카페24 관리자 로그인"):
            try:
                # 로그인 페이지로 이동
                login_url = self._get_login_url()
                self.browser.navigate_to(login_url)
                
                # 로그인 폼 찾기 및 입력
                if self._fill_login_form():
                    # 로그인 버튼 클릭
                    if self._submit_login():
                        # 로그인 성공 확인
                        if self._verify_login_success():
                            self.is_logged_in = True
                            logger.info("로그인 성공!")
                            return True
                        else:
                            logger.error("로그인 후 관리자 페이지 진입 실패")
                            return False
                    else:
                        logger.error("로그인 버튼 클릭 실패")
                        return False
                else:
                    logger.error("로그인 폼 입력 실패")
                    return False
                    
            except Exception as e:
                logger.error(f"로그인 중 오류 발생: {e}")
                self.browser.take_screenshot("login_error.png")
                return False
    
    def _get_login_url(self) -> str:
        """로그인 URL 생성"""
        mall_id = self.credentials["cafe24"]["mall_id"]
        return f"https://{mall_id}.cafe24.com/admin"
    
    def _fill_login_form(self) -> bool:
        """로그인 폼 입력"""
        try:
            # 아이디 입력 필드 찾기
            id_selectors = [
                (By.NAME, "admin_id"),
                (By.ID, "admin_id"),
                (By.CSS_SELECTOR, "input[name='admin_id']"),
                (By.CSS_SELECTOR, "input#admin_id"),
                (By.XPATH, "//input[@placeholder='아이디' or @placeholder='ID' or contains(@class, 'id')]")
            ]
            
            id_field = self._find_element_by_selectors(id_selectors, "아이디 입력 필드")
            if not id_field:
                return False
            
            # 아이디 입력
            admin_id = self.credentials["cafe24"]["admin_id"]
            id_field.clear()
            id_field.send_keys(admin_id)
            logger.info(f"아이디 입력 완료: {admin_id}")
            
            # 패스워드 입력 필드 찾기
            password_selectors = [
                (By.NAME, "admin_password"),
                (By.NAME, "password"),
                (By.ID, "admin_password"),
                (By.ID, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.XPATH, "//input[@type='password']")
            ]
            
            password_field = self._find_element_by_selectors(password_selectors, "패스워드 입력 필드")
            if not password_field:
                return False
            
            # 패스워드 입력
            admin_password = self.credentials["cafe24"]["admin_password"]
            password_field.clear()
            password_field.send_keys(admin_password)
            logger.info("패스워드 입력 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"로그인 폼 입력 중 오류: {e}")
            return False
    
    def _submit_login(self) -> bool:
        """로그인 버튼 클릭"""
        try:
            # 로그인 버튼 찾기
            button_selectors = [
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//input[@value='로그인' or @value='LOGIN' or @value='확인']"),
                (By.XPATH, "//button[contains(text(), '로그인') or contains(text(), 'LOGIN')]"),
                (By.ID, "login_btn"),
                (By.ID, "loginBtn"),
                (By.CLASS_NAME, "login-btn")
            ]
            
            login_button = self._find_element_by_selectors(button_selectors, "로그인 버튼")
            if not login_button:
                return False
            
            # 버튼 클릭
            self.browser.scroll_to_element(login_button)
            time.sleep(0.5)
            login_button.click()
            logger.info("로그인 버튼 클릭 완료")
            
            # 페이지 로딩 대기
            time.sleep(3)
            
            return True
            
        except Exception as e:
            logger.error(f"로그인 버튼 클릭 중 오류: {e}")
            return False
    
    def _verify_login_success(self) -> bool:
        """로그인 성공 확인"""
        try:
            # 관리자 페이지 요소들 확인
            success_indicators = [
                (By.XPATH, "//a[contains(@href, 'logout') or contains(text(), '로그아웃')]"),
                (By.CSS_SELECTOR, ".admin-header"),
                (By.CSS_SELECTOR, ".gnb"),
                (By.XPATH, "//title[contains(text(), '관리자')]"),
                (By.XPATH, "//div[@class='container' or @class='main-container']"),
                (By.CSS_SELECTOR, "frame[name='menu']"),  # 카페24 특유의 프레임 구조
                (By.CSS_SELECTOR, "frame[name='main']")
            ]
            
            # URL 확인
            current_url = self.browser.get_current_url()
            if "admin" in current_url and "login" not in current_url:
                logger.info(f"관리자 페이지 URL 확인: {current_url}")
                
                # 추가 요소 확인
                for selector in success_indicators:
                    try:
                        element = self.browser.wait_for_element(selector, timeout=5)
                        if element:
                            logger.info(f"로그인 성공 요소 확인: {selector}")
                            return True
                    except TimeoutException:
                        continue
                
                # 요소를 찾지 못해도 URL이 관리자 페이지면 성공으로 간주
                logger.info("URL 기준으로 로그인 성공 판정")
                return True
            
            # 로그인 실패 확인
            if self._check_login_error():
                return False
            
            logger.warning("로그인 성공 여부를 확실히 판단할 수 없습니다.")
            self.browser.take_screenshot("login_verification.png")
            return False
            
        except Exception as e:
            logger.error(f"로그인 확인 중 오류: {e}")
            return False
    
    def _check_login_error(self) -> bool:
        """로그인 에러 확인"""
        try:
            error_selectors = [
                (By.XPATH, "//div[contains(@class, 'error') or contains(@class, 'alert')]"),
                (By.XPATH, "//span[contains(text(), '잘못') or contains(text(), '실패') or contains(text(), 'error')]"),
                (By.CSS_SELECTOR, ".error-message"),
                (By.CSS_SELECTOR, ".alert-danger")
            ]
            
            for selector in error_selectors:
                try:
                    error_element = self.browser.driver.find_element(*selector)
                    if error_element and error_element.is_displayed():
                        error_text = error_element.text
                        logger.error(f"로그인 에러 감지: {error_text}")
                        return True
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"로그인 에러 확인 중 오류: {e}")
            return False
    
    def _find_element_by_selectors(self, selectors: list, description: str) -> Optional[Any]:
        """여러 선택자로 요소 찾기"""
        for selector in selectors:
            try:
                element = self.browser.wait_for_element(selector, timeout=3)
                if element and element.is_displayed():
                    logger.debug(f"{description} 찾기 성공: {selector}")
                    return element
            except (TimeoutException, NoSuchElementException):
                continue
        
        logger.error(f"{description}를 찾을 수 없습니다.")
        self.browser.take_screenshot(f"element_not_found_{description}.png")
        return None
    
    def logout(self) -> bool:
        """로그아웃"""
        if not self.is_logged_in:
            logger.info("로그인 상태가 아닙니다.")
            return True
        
        try:
            with LogContext(logger, "로그아웃"):
                # 로그아웃 링크 찾기
                logout_selectors = [
                    (By.XPATH, "//a[contains(@href, 'logout')]"),
                    (By.XPATH, "//a[contains(text(), '로그아웃')]"),
                    (By.CSS_SELECTOR, "a[href*='logout']")
                ]
                
                logout_link = self._find_element_by_selectors(logout_selectors, "로그아웃 링크")
                if logout_link:
                    logout_link.click()
                    self.is_logged_in = False
                    logger.info("로그아웃 완료")
                    return True
                else:
                    logger.warning("로그아웃 링크를 찾을 수 없습니다.")
                    return False
                    
        except Exception as e:
            logger.error(f"로그아웃 중 오류: {e}")
            return False
    
    def check_login_status(self) -> bool:
        """현재 로그인 상태 확인"""
        try:
            current_url = self.browser.get_current_url()
            
            # URL 기반 확인
            if "admin" in current_url and "login" not in current_url:
                self.is_logged_in = True
                logger.info("로그인 상태 확인됨")
                return True
            else:
                self.is_logged_in = False
                logger.info("로그인되지 않은 상태")
                return False
                
        except Exception as e:
            logger.error(f"로그인 상태 확인 중 오류: {e}")
            self.is_logged_in = False
            return False
    
    def ensure_logged_in(self) -> bool:
        """로그인 상태 보장"""
        if not self.check_login_status():
            return self.login()
        return True


def create_login_manager(browser_manager: BrowserManager, credentials_path: str = "config/credentials.json") -> LoginManager:
    """
    로그인 매니저 생성 팩토리 함수
    
    Args:
        browser_manager: 브라우저 매니저 인스턴스
        credentials_path: 인증 정보 파일 경로
        
    Returns:
        LoginManager 인스턴스
    """
    return LoginManager(browser_manager, credentials_path)