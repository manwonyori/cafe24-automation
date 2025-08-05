"""
에러 처리 유틸리티 모듈
"""

import sys
import traceback
from typing import Dict, Any, Optional, Callable
from functools import wraps
from selenium.common.exceptions import (
    WebDriverException, TimeoutException, NoSuchElementException,
    StaleElementReferenceException, ElementClickInterceptedException,
    ElementNotInteractableException
)
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SeleniumErrorHandler:
    """Selenium 에러 처리 클래스"""
    
    @staticmethod
    def handle_common_errors(func):
        """일반적인 Selenium 에러를 처리하는 데코레이터"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
                
            except TimeoutException as e:
                logger.error(f"요소 대기 시간 초과: {func.__name__}")
                return {"success": False, "error": "요소를 찾을 수 없습니다 (시간 초과)"}
                
            except NoSuchElementException as e:
                logger.error(f"요소를 찾을 수 없음: {func.__name__}")
                return {"success": False, "error": "페이지에서 필요한 요소를 찾을 수 없습니다"}
                
            except StaleElementReferenceException as e:
                logger.error(f"요소 참조 오류: {func.__name__}")
                return {"success": False, "error": "페이지가 변경되어 요소를 다시 찾아야 합니다"}
                
            except ElementClickInterceptedException as e:
                logger.error(f"요소 클릭 차단: {func.__name__}")
                return {"success": False, "error": "다른 요소가 클릭을 차단하고 있습니다"}
                
            except ElementNotInteractableException as e:
                logger.error(f"요소 상호작용 불가: {func.__name__}")
                return {"success": False, "error": "요소와 상호작용할 수 없습니다"}
                
            except WebDriverException as e:
                logger.error(f"WebDriver 오류: {func.__name__} - {str(e)}")
                return {"success": False, "error": f"브라우저 오류가 발생했습니다: {str(e)}"}
                
            except Exception as e:
                logger.error(f"예상치 못한 오류: {func.__name__} - {str(e)}")
                logger.error(traceback.format_exc())
                return {"success": False, "error": f"예상치 못한 오류가 발생했습니다: {str(e)}"}
                
        return wrapper
    
    @staticmethod
    def safe_execute(func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """안전하게 함수 실행"""
        try:
            result = func(*args, **kwargs)
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"함수 실행 실패 ({func.__name__}): {e}")
            return {"success": False, "error": str(e)}


class ErrorRecovery:
    """에러 복구 클래스"""
    
    def __init__(self, browser_manager, login_manager):
        self.browser = browser_manager
        self.login = login_manager
        
    def recover_from_error(self, error_type: str, context: Dict[str, Any] = None) -> bool:
        """에러 타입에 따른 복구 시도"""
        recovery_methods = {
            "login_required": self._recover_login,
            "page_not_found": self._recover_navigation,
            "stale_element": self._recover_page_refresh,
            "timeout": self._recover_wait_longer,
            "click_intercepted": self._recover_scroll_and_click,
            "network_error": self._recover_retry_request
        }
        
        if error_type in recovery_methods:
            try:
                logger.info(f"에러 복구 시도: {error_type}")
                return recovery_methods[error_type](context or {})
            except Exception as e:
                logger.error(f"에러 복구 실패: {e}")
                return False
        
        logger.warning(f"알 수 없는 에러 타입: {error_type}")
        return False
    
    def _recover_login(self, context: Dict[str, Any]) -> bool:
        """로그인 복구"""
        try:
            return self.login.login(force_relogin=True)
        except Exception as e:
            logger.error(f"로그인 복구 실패: {e}")
            return False
    
    def _recover_navigation(self, context: Dict[str, Any]) -> bool:
        """페이지 네비게이션 복구"""
        try:
            target_url = context.get("target_url")
            if target_url:
                self.browser.navigate_to(target_url)
                return True
            return False
        except Exception as e:
            logger.error(f"네비게이션 복구 실패: {e}")
            return False
    
    def _recover_page_refresh(self, context: Dict[str, Any]) -> bool:
        """페이지 새로고침 복구"""
        try:
            self.browser.refresh_page()
            import time
            time.sleep(3)  # 페이지 로딩 대기
            return True
        except Exception as e:
            logger.error(f"새로고침 복구 실패: {e}")
            return False
    
    def _recover_wait_longer(self, context: Dict[str, Any]) -> bool:
        """더 오래 대기"""
        try:
            import time
            wait_time = context.get("wait_time", 5)
            logger.info(f"추가 대기: {wait_time}초")
            time.sleep(wait_time)
            return True
        except Exception as e:
            logger.error(f"대기 복구 실패: {e}")
            return False
    
    def _recover_scroll_and_click(self, context: Dict[str, Any]) -> bool:
        """스크롤 후 클릭 복구"""
        try:
            element = context.get("element")
            if element:
                self.browser.scroll_to_element(element)
                import time
                time.sleep(1)
                
                # JavaScript로 클릭 시도
                self.browser.execute_script("arguments[0].click();", element)
                return True
            return False
        except Exception as e:
            logger.error(f"스크롤/클릭 복구 실패: {e}")
            return False
    
    def _recover_retry_request(self, context: Dict[str, Any]) -> bool:
        """네트워크 요청 재시도"""
        try:
            import time
            retry_count = context.get("retry_count", 1)
            
            for i in range(retry_count):
                logger.info(f"네트워크 재시도 {i+1}/{retry_count}")
                time.sleep(2 ** i)  # 지수 백오프
                
                # 현재 페이지 새로고침
                self.browser.refresh_page()
                time.sleep(3)
                
                # 페이지 로딩 확인
                if self.browser.is_alive():
                    return True
            
            return False
        except Exception as e:
            logger.error(f"네트워크 재시도 복구 실패: {e}")
            return False


def create_error_context(
    function_name: str,
    error: Exception,
    browser_manager=None,
    additional_info: Dict[str, Any] = None
) -> Dict[str, Any]:
    """에러 컨텍스트 생성"""
    context = {
        "function_name": function_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "traceback": traceback.format_exc()
    }
    
    if browser_manager and browser_manager.is_alive():
        try:
            context.update({
                "current_url": browser_manager.get_current_url(),
                "page_title": browser_manager.driver.title,
                "window_size": browser_manager.driver.get_window_size()
            })
        except Exception:
            pass  # 브라우저 정보 가져오기 실패해도 무시
    
    if additional_info:
        context.update(additional_info)
    
    return context


def log_error_context(context: Dict[str, Any]) -> None:
    """에러 컨텍스트 로깅"""
    logger.error("=== 에러 컨텍스트 정보 ===")
    for key, value in context.items():
        if key == "traceback":
            logger.error(f"{key}:\n{value}")
        else:
            logger.error(f"{key}: {value}")
    logger.error("=== 에러 컨텍스트 끝 ===")


class RetryableError(Exception):
    """재시도 가능한 에러"""
    pass


class NonRetryableError(Exception):
    """재시도 불가능한 에러"""
    pass


def classify_error(error: Exception) -> str:
    """에러를 재시도 가능/불가능으로 분류"""
    retryable_errors = [
        TimeoutException,
        StaleElementReferenceException,
        WebDriverException  # 일부는 재시도 가능
    ]
    
    non_retryable_errors = [
        NoSuchElementException,  # 요소가 아예 없는 경우
        ElementNotInteractableException  # 요소 상호작용 불가
    ]
    
    if any(isinstance(error, err_type) for err_type in non_retryable_errors):
        return "non_retryable"
    elif any(isinstance(error, err_type) for err_type in retryable_errors):
        return "retryable"
    else:
        return "unknown"


def with_error_recovery(recovery_strategies: Dict[str, Callable] = None):
    """에러 복구 전략을 포함한 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    error_classification = classify_error(e)
                    
                    if error_classification == "non_retryable" or attempt == max_retries - 1:
                        # 재시도 불가능하거나 최대 재시도 횟수 도달
                        context = create_error_context(func.__name__, e)
                        log_error_context(context)
                        raise
                    
                    # 복구 전략 실행
                    if recovery_strategies and error_classification in recovery_strategies:
                        try:
                            recovery_strategies[error_classification]()
                        except Exception as recovery_error:
                            logger.error(f"에러 복구 실패: {recovery_error}")
                    
                    logger.warning(f"재시도 {attempt + 1}/{max_retries}: {func.__name__}")
                    
                    import time
                    time.sleep(2 ** attempt)  # 지수 백오프
            
        return wrapper
    return decorator


def safe_screenshot(browser_manager, filename_prefix: str = "error") -> Optional[str]:
    """안전하게 스크린샷 촬영"""
    try:
        if browser_manager and browser_manager.is_alive():
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.png"
            return browser_manager.take_screenshot(filename)
    except Exception as e:
        logger.error(f"스크린샷 촬영 실패: {e}")
    
    return None


def create_error_recovery(browser_manager, login_manager) -> ErrorRecovery:
    """ErrorRecovery 인스턴스 생성"""
    return ErrorRecovery(browser_manager, login_manager)