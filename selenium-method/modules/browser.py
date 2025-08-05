"""
브라우저 관리 모듈
Chrome WebDriver 초기화 및 설정 관리
"""

import os
import json
import platform
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BrowserManager:
    """Chrome WebDriver 관리 클래스"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        """
        브라우저 매니저 초기화
        
        Args:
            config_path: 설정 파일 경로
        """
        self.config = self._load_config(config_path)
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"설정 파일 로드 완료: {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"설정 파일을 찾을 수 없습니다: {config_path}")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"설정 파일 JSON 파싱 오류: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """기본 설정 반환"""
        return {
            "browser": {
                "headless": False,
                "window_size": [1920, 1080],
                "implicit_wait": 10,
                "page_load_timeout": 30,
                "disable_gpu": True,
                "no_sandbox": True,
                "disable_dev_shm_usage": True
            },
            "paths": {
                "download_folder": "./downloads",
                "screenshot_folder": "./data/screenshots"
            }
        }
    
    def create_driver(self, headless: bool = None, undetected: bool = True) -> webdriver.Chrome:
        """
        Chrome WebDriver 생성
        
        Args:
            headless: 헤드리스 모드 여부 (None이면 설정파일 값 사용)
            undetected: 탐지 우회 ChromeDriver 사용 여부
            
        Returns:
            Chrome WebDriver 인스턴스
        """
        try:
            browser_config = self.config.get("browser", {})
            
            # Chrome 옵션 설정
            options = Options()
            
            # 헤드리스 모드 설정
            if headless is None:
                headless = browser_config.get("headless", False)
            
            if headless:
                options.add_argument("--headless")
                logger.info("헤드리스 모드로 브라우저 시작")
            
            # 기본 옵션들
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")  # 이미지 로딩 비활성화로 속도 향상
            
            # User Agent 설정
            if "user_agent" in browser_config:
                options.add_argument(f"--user-agent={browser_config['user_agent']}")
            
            # 다운로드 폴더 설정
            download_folder = os.path.abspath(
                self.config.get("paths", {}).get("download_folder", "./downloads")
            )
            os.makedirs(download_folder, exist_ok=True)
            
            prefs = {
                "download.default_directory": download_folder,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0
            }
            options.add_experimental_option("prefs", prefs)
            
            # 창 크기 설정
            window_size = browser_config.get("window_size", [1920, 1080])
            options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
            
            # 메모리 사용량 최적화
            options.add_argument("--memory-pressure-off")
            options.add_argument("--max_old_space_size=4096")
            
            # WebDriver 생성
            if undetected:
                # 탐지 우회용 ChromeDriver 사용
                self.driver = uc.Chrome(options=options, version_main=None)
                logger.info("Undetected ChromeDriver로 시작")
            else:
                # 일반 ChromeDriver 사용
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                logger.info("일반 ChromeDriver로 시작")
            
            # 대기 시간 설정
            implicit_wait = browser_config.get("implicit_wait", 10)
            page_load_timeout = browser_config.get("page_load_timeout", 30)
            
            self.driver.implicitly_wait(implicit_wait)
            self.driver.set_page_load_timeout(page_load_timeout)
            
            # WebDriverWait 객체 생성
            self.wait = WebDriverWait(self.driver, implicit_wait)
            
            logger.info(f"브라우저 시작 완료 - Chrome {self.driver.capabilities['browserVersion']}")
            return self.driver
            
        except Exception as e:
            logger.error(f"브라우저 생성 실패: {e}")
            raise WebDriverException(f"브라우저 초기화 실패: {e}")
    
    def take_screenshot(self, filename: str = None) -> str:
        """
        스크린샷 촬영
        
        Args:
            filename: 저장할 파일명 (None이면 자동 생성)
            
        Returns:
            저장된 파일 경로
        """
        if not self.driver:
            raise ValueError("브라우저가 시작되지 않았습니다.")
        
        try:
            # 스크린샷 폴더 생성
            screenshot_folder = self.config.get("paths", {}).get("screenshot_folder", "./data/screenshots")
            os.makedirs(screenshot_folder, exist_ok=True)
            
            # 파일명 생성
            if filename is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            filepath = os.path.join(screenshot_folder, filename)
            
            # 스크린샷 촬영
            self.driver.save_screenshot(filepath)
            logger.info(f"스크린샷 저장: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"스크린샷 촬영 실패: {e}")
            raise
    
    def wait_for_element(self, locator: tuple, timeout: int = None) -> Any:
        """
        요소가 나타날 때까지 대기
        
        Args:
            locator: (By, selector) 튜플
            timeout: 대기 시간 (초)
            
        Returns:
            찾은 요소
        """
        if not self.wait:
            raise ValueError("WebDriverWait이 초기화되지 않았습니다.")
        
        try:
            if timeout:
                wait = WebDriverWait(self.driver, timeout)
                element = wait.until(EC.presence_of_element_located(locator))
            else:
                element = self.wait.until(EC.presence_of_element_located(locator))
            
            return element
            
        except TimeoutException:
            logger.error(f"요소를 찾을 수 없습니다: {locator}")
            self.take_screenshot(f"timeout_error_{locator[1]}.png")
            raise
    
    def wait_for_clickable(self, locator: tuple, timeout: int = None) -> Any:
        """
        요소가 클릭 가능할 때까지 대기
        
        Args:
            locator: (By, selector) 튜플
            timeout: 대기 시간 (초)
            
        Returns:
            클릭 가능한 요소
        """
        if not self.wait:
            raise ValueError("WebDriverWait이 초기화되지 않았습니다.")
        
        try:
            if timeout:
                wait = WebDriverWait(self.driver, timeout)
                element = wait.until(EC.element_to_be_clickable(locator))
            else:
                element = self.wait.until(EC.element_to_be_clickable(locator))
            
            return element
            
        except TimeoutException:
            logger.error(f"클릭 가능한 요소를 찾을 수 없습니다: {locator}")
            self.take_screenshot(f"clickable_timeout_{locator[1]}.png")
            raise
    
    def scroll_to_element(self, element) -> None:
        """요소까지 스크롤"""
        if not self.driver:
            raise ValueError("브라우저가 시작되지 않았습니다.")
        
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            import time
            time.sleep(0.5)  # 스크롤 완료 대기
            
        except Exception as e:
            logger.error(f"스크롤 실패: {e}")
            raise
    
    def execute_script(self, script: str, *args) -> Any:
        """JavaScript 실행"""
        if not self.driver:
            raise ValueError("브라우저가 시작되지 않았습니다.")
        
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            logger.error(f"JavaScript 실행 실패: {e}")
            raise
    
    def get_page_source(self) -> str:
        """페이지 소스 반환"""
        if not self.driver:
            raise ValueError("브라우저가 시작되지 않았습니다.")
        
        return self.driver.page_source
    
    def refresh_page(self) -> None:
        """페이지 새로고침"""
        if not self.driver:
            raise ValueError("브라우저가 시작되지 않았습니다.")
        
        try:
            self.driver.refresh()
            logger.info("페이지 새로고침 완료")
            
        except Exception as e:
            logger.error(f"페이지 새로고침 실패: {e}")
            raise
    
    def close(self) -> None:
        """브라우저 종료"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("브라우저 종료 완료")
            except Exception as e:
                logger.error(f"브라우저 종료 중 오류: {e}")
            finally:
                self.driver = None
                self.wait = None
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()
    
    def is_alive(self) -> bool:
        """브라우저가 살아있는지 확인"""
        if not self.driver:
            return False
        
        try:
            # 현재 URL을 가져와서 브라우저가 응답하는지 확인
            _ = self.driver.current_url
            return True
        except Exception:
            return False
    
    def get_current_url(self) -> str:
        """현재 URL 반환"""
        if not self.driver:
            raise ValueError("브라우저가 시작되지 않았습니다.")
        
        return self.driver.current_url
    
    def navigate_to(self, url: str) -> None:
        """지정된 URL로 이동"""
        if not self.driver:
            raise ValueError("브라우저가 시작되지 않았습니다.")
        
        try:
            logger.info(f"페이지 이동: {url}")
            self.driver.get(url)
            
        except Exception as e:
            logger.error(f"페이지 이동 실패 ({url}): {e}")
            raise


def create_browser_manager(config_path: str = "config/settings.json") -> BrowserManager:
    """
    브라우저 매니저 생성 팩토리 함수
    
    Args:
        config_path: 설정 파일 경로
        
    Returns:
        BrowserManager 인스턴스
    """
    return BrowserManager(config_path)