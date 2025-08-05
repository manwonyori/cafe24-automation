"""
대기 및 재시도 유틸리티 모듈
"""

import time
import functools
from typing import Callable, Any, Optional, Union
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from utils.logger import setup_logger

logger = setup_logger(__name__)


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    예외 발생 시 재시도하는 데코레이터
    
    Args:
        max_retries: 최대 재시도 횟수
        delay: 초기 대기 시간 (초)
        backoff: 지수 백오프 배수
        exceptions: 재시도할 예외 튜플
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(f"{func.__name__} 재시도 {attempt}회 후 성공")
                    return result
                    
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} 최대 재시도 횟수 초과: {e}")
                        raise
                    
                    logger.warning(f"{func.__name__} 실패 (시도 {attempt + 1}/{max_retries + 1}): {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
        return wrapper
    return decorator


def wait_for_condition(
    condition: Callable[[], bool],
    timeout: float = 30.0,
    poll_frequency: float = 0.5,
    error_message: str = "조건 대기 시간 초과"
) -> bool:
    """
    특정 조건이 참이 될 때까지 대기
    
    Args:
        condition: 확인할 조건 함수
        timeout: 최대 대기 시간 (초)
        poll_frequency: 확인 간격 (초)
        error_message: 타임아웃 시 에러 메시지
        
    Returns:
        조건 만족 여부
        
    Raises:
        TimeoutException: 대기 시간 초과 시
    """
    end_time = time.time() + timeout
    
    while time.time() < end_time:
        try:
            if condition():
                return True
        except Exception as e:
            logger.debug(f"조건 확인 중 예외: {e}")
        
        time.sleep(poll_frequency)
    
    raise TimeoutException(error_message)


def smart_wait(
    browser_manager,
    locator: tuple,
    condition_type: str = "presence",
    timeout: float = 10.0,
    poll_frequency: float = 0.5
) -> Any:
    """
    스마트 대기 함수 - 다양한 조건으로 요소 대기
    
    Args:
        browser_manager: 브라우저 매니저 인스턴스
        locator: (By, selector) 튜플
        condition_type: 대기 조건 타입
        timeout: 최대 대기 시간
        poll_frequency: 확인 간격
        
    Returns:
        찾은 요소
    """
    wait = WebDriverWait(browser_manager.driver, timeout, poll_frequency)
    
    conditions = {
        "presence": EC.presence_of_element_located(locator),
        "visible": EC.visibility_of_element_located(locator),
        "clickable": EC.element_to_be_clickable(locator),
        "invisible": EC.invisibility_of_element_located(locator),
        "selected": EC.element_to_be_selected(locator)
    }
    
    if condition_type not in conditions:
        raise ValueError(f"지원하지 않는 조건 타입: {condition_type}")
    
    try:
        return wait.until(conditions[condition_type])
    except TimeoutException:
        logger.error(f"요소 대기 시간 초과 ({condition_type}): {locator}")
        browser_manager.take_screenshot(f"wait_timeout_{condition_type}.png")
        raise


def wait_for_page_load(
    browser_manager,
    timeout: float = 30.0,
    expected_url_contains: str = None
) -> bool:
    """
    페이지 로딩 완료 대기
    
    Args:
        browser_manager: 브라우저 매니저 인스턴스
        timeout: 최대 대기 시간
        expected_url_contains: 예상 URL 포함 문자열
        
    Returns:
        페이지 로딩 완료 여부
    """
    def page_loaded():
        try:
            # JavaScript 실행 완료 확인
            ready_state = browser_manager.execute_script("return document.readyState")
            if ready_state != "complete":
                return False
            
            # jQuery 로딩 확인 (있는 경우)
            try:
                jquery_ready = browser_manager.execute_script("return jQuery.active == 0")
                if not jquery_ready:
                    return False
            except:
                pass  # jQuery가 없으면 무시
            
            # 예상 URL 확인
            if expected_url_contains:
                current_url = browser_manager.get_current_url()
                return expected_url_contains in current_url
            
            return True
            
        except Exception as e:
            logger.debug(f"페이지 로딩 확인 중 예외: {e}")
            return False
    
    try:
        return wait_for_condition(
            condition=page_loaded,
            timeout=timeout,
            poll_frequency=0.5,
            error_message="페이지 로딩 대기 시간 초과"
        )
    except TimeoutException:
        logger.warning("페이지 로딩 대기 시간 초과")
        return False


def wait_for_element_stable(
    browser_manager,
    locator: tuple,
    stability_time: float = 2.0,
    timeout: float = 30.0
) -> Any:
    """
    요소가 안정적으로 표시될 때까지 대기
    (위치나 크기가 변하지 않을 때까지)
    
    Args:
        browser_manager: 브라우저 매니저 인스턴스
        locator: (By, selector) 튜플
        stability_time: 안정성 확인 시간
        timeout: 최대 대기 시간
        
    Returns:
        안정적인 요소
    """
    element = smart_wait(browser_manager, locator, "visible", timeout)
    
    # 요소 위치/크기 안정성 확인
    stable_count = 0
    last_location = None
    last_size = None
    
    while stable_count < stability_time * 2:  # 0.5초마다 확인
        try:
            current_location = element.location
            current_size = element.size
            
            if (last_location == current_location and 
                last_size == current_size and 
                element.is_displayed()):
                stable_count += 1
            else:
                stable_count = 0
                
            last_location = current_location
            last_size = current_size
            
            time.sleep(0.5)
            
        except StaleElementReferenceException:
            # 요소가 stale되면 다시 찾기
            element = smart_wait(browser_manager, locator, "visible", 5)
            stable_count = 0
    
    return element


def progressive_wait(
    condition: Callable[[], bool],
    max_timeout: float = 60.0,
    initial_wait: float = 0.1,
    max_wait: float = 5.0,
    multiplier: float = 1.5
) -> bool:
    """
    점진적 대기 - 대기 시간을 점차 늘려가며 조건 확인
    
    Args:
        condition: 확인할 조건 함수
        max_timeout: 최대 총 대기 시간
        initial_wait: 초기 대기 시간
        max_wait: 최대 단일 대기 시간
        multiplier: 대기 시간 증가 배수
        
    Returns:
        조건 만족 여부
    """
    start_time = time.time()
    current_wait = initial_wait
    
    while time.time() - start_time < max_timeout:
        try:
            if condition():
                return True
        except Exception as e:
            logger.debug(f"조건 확인 중 예외: {e}")
        
        time.sleep(current_wait)
        current_wait = min(current_wait * multiplier, max_wait)
    
    return False


class WaitHelper:
    """대기 관련 헬퍼 클래스"""
    
    def __init__(self, browser_manager):
        self.browser = browser_manager
        
    def wait_and_click(
        self, 
        locator: tuple, 
        timeout: float = 10.0,
        scroll_to: bool = True
    ) -> bool:
        """요소를 기다린 후 클릭"""
        try:
            element = smart_wait(
                self.browser, 
                locator, 
                "clickable", 
                timeout
            )
            
            if scroll_to:
                self.browser.scroll_to_element(element)
                time.sleep(0.5)
            
            element.click()
            return True
            
        except Exception as e:
            logger.error(f"요소 클릭 실패 {locator}: {e}")
            return False
    
    def wait_and_send_keys(
        self, 
        locator: tuple, 
        text: str,
        clear: bool = True,
        timeout: float = 10.0
    ) -> bool:
        """요소를 기다린 후 텍스트 입력"""
        try:
            element = smart_wait(
                self.browser, 
                locator, 
                "visible", 
                timeout
            )
            
            if clear:
                element.clear()
            
            element.send_keys(text)
            return True
            
        except Exception as e:
            logger.error(f"텍스트 입력 실패 {locator}: {e}")
            return False
    
    def wait_for_text_change(
        self, 
        locator: tuple, 
        original_text: str,
        timeout: float = 10.0
    ) -> Optional[str]:
        """텍스트가 변경될 때까지 대기"""
        def text_changed():
            try:
                element = self.browser.driver.find_element(*locator)
                current_text = element.text
                return current_text != original_text
            except:
                return False
        
        try:
            wait_for_condition(
                condition=text_changed,
                timeout=timeout,
                error_message="텍스트 변경 대기 시간 초과"
            )
            
            element = self.browser.driver.find_element(*locator)
            return element.text
            
        except TimeoutException:
            return None
    
    def wait_for_url_change(
        self, 
        original_url: str,
        timeout: float = 10.0
    ) -> Optional[str]:
        """URL이 변경될 때까지 대기"""
        def url_changed():
            current_url = self.browser.get_current_url()
            return current_url != original_url
        
        try:
            wait_for_condition(
                condition=url_changed,
                timeout=timeout,
                error_message="URL 변경 대기 시간 초과"
            )
            
            return self.browser.get_current_url()
            
        except TimeoutException:
            return None


def create_wait_helper(browser_manager) -> WaitHelper:
    """WaitHelper 인스턴스 생성"""
    return WaitHelper(browser_manager)