"""
개선된 카페24 관리자 로그인 자동화 모듈
"""
import os
import json
import time
from typing import Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.logger import get_logger

logger = get_logger(__name__)

class LoginManager:
    def __init__(self, browser_manager, config_path: str = "config/credentials.json"):
        self.browser_manager = browser_manager
        self.credentials = self._load_credentials(config_path)
        self.is_logged_in = False
        
    def _load_credentials(self, config_path: str) -> Dict[str, Any]:
        """인증 정보 로드"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 환경변수에서 로드
                return {
                    "cafe24": {
                        "admin_id": os.getenv("CAFE24_ADMIN_ID", ""),
                        "admin_password": os.getenv("CAFE24_ADMIN_PASSWORD", ""),
                        "mall_id": os.getenv("CAFE24_MALL_ID", "manwonyori")
                    }
                }
        except Exception as e:
            logger.error(f"인증 정보 로드 실패: {e}")
            return {"cafe24": {"admin_id": "", "admin_password": "", "mall_id": "manwonyori"}}

    def login(self) -> bool:
        """카페24 관리자 로그인"""
        try:
            logger.info("=== 카페24 관리자 로그인 시작 ===")
            
            # 1단계: 로그인 페이지 접근 시도
            login_success = self._try_multiple_login_methods()
            if not login_success:
                logger.error("모든 로그인 방법 실패")
                return False
            
            # 2단계: 로그인 성공 확인
            if self._verify_login_success():
                self.is_logged_in = True
                logger.info("✅ 로그인 성공!")
                return True
            else:
                logger.error("로그인 실패 - 관리자 페이지로 이동하지 못함")
                return False
                
        except Exception as e:
            logger.error(f"로그인 중 오류 발생: {e}")
            return False

    def _try_multiple_login_methods(self) -> bool:
        """다양한 로그인 방법 시도"""
        mall_id = self.credentials["cafe24"]["mall_id"]
        
        # 시도할 로그인 URL 목록
        login_methods = [
            {
                "name": "직접 관리자 로그인",
                "url": f"https://echosting.cafe24.com/manage/shop/login",
                "wait_time": 5
            },
            {
                "name": "몰 관리자 페이지",
                "url": f"https://{mall_id}.cafe24.com/admin",
                "wait_time": 5
            },
            {
                "name": "호스팅 관리자",
                "url": f"https://echosting.cafe24.com/Shop/{mall_id}/",
                "wait_time": 3
            }
        ]
        
        for method in login_methods:
            logger.info(f"로그인 방법 시도: {method['name']}")
            logger.info(f"URL: {method['url']}")
            
            try:
                # 페이지 접근
                self.browser_manager.driver.get(method['url'])
                time.sleep(method['wait_time'])
                
                # 알림창 처리
                self._handle_alerts()
                
                # 페이지 소스 저장 (디버깅용)
                self._save_page_source(f"login_attempt_{method['name'].replace(' ', '_')}")
                
                # iframe 처리
                self._handle_iframes()
                
                # 로그인 폼 찾기 및 입력
                if self._find_and_fill_login_form():
                    # 로그인 버튼 클릭
                    if self._submit_login():
                        logger.info(f"로그인 시도 완료: {method['name']}")
                        time.sleep(3)  # 로그인 처리 대기
                        return True
                        
            except Exception as e:
                logger.warning(f"로그인 방법 '{method['name']}' 실패: {e}")
                continue
                
        return False

    def _save_page_source(self, filename: str):
        """페이지 소스 저장 (디버깅용)"""
        try:
            page_source = self.browser_manager.driver.page_source
            os.makedirs("data/debug", exist_ok=True)
            
            with open(f"data/debug/{filename}.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            logger.info(f"페이지 소스 저장: data/debug/{filename}.html")
        except Exception as e:
            logger.warning(f"페이지 소스 저장 실패: {e}")

    def _handle_alerts(self) -> None:
        """알림창 처리"""
        try:
            # 알림창 확인 (최대 2초 대기)
            alert = WebDriverWait(self.browser_manager.driver, 2).until(EC.alert_is_present())
            alert_text = alert.text
            logger.info(f"알림창 감지: {alert_text}")
            alert.accept()
            time.sleep(1)
        except TimeoutException:
            pass  # 알림창이 없는 경우
        except Exception as e:
            logger.warning(f"알림창 처리 중 오류: {e}")

    def _handle_iframes(self) -> None:
        """iframe 처리"""
        try:
            # iframe이 있는지 확인
            iframes = self.browser_manager.driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                logger.info(f"iframe {len(iframes)}개 감지")
                for i, iframe in enumerate(iframes):
                    try:
                        self.browser_manager.driver.switch_to.frame(iframe)
                        logger.info(f"iframe {i+1}로 전환 성공")
                        # 로그인 폼이 있는지 확인
                        login_forms = self.browser_manager.driver.find_elements(By.TAG_NAME, "form")
                        if login_forms:
                            logger.info("iframe 내에서 폼 발견")
                            return
                        else:
                            # 원래 프레임으로 돌아가기
                            self.browser_manager.driver.switch_to.default_content()
                    except Exception as e:
                        logger.warning(f"iframe {i+1} 처리 실패: {e}")
                        self.browser_manager.driver.switch_to.default_content()
        except Exception as e:
            logger.warning(f"iframe 처리 중 오류: {e}")

    def _find_and_fill_login_form(self) -> bool:
        """로그인 폼 찾기 및 입력"""
        try:
            # 1. 아이디 입력 필드 찾기
            id_field = self._find_login_field("아이디", [
                # 일반적인 셀렉터
                (By.NAME, "admin_id"),
                (By.NAME, "id"),
                (By.NAME, "userid"),
                (By.NAME, "user_id"),
                (By.NAME, "loginId"),
                (By.ID, "admin_id"),
                (By.ID, "id"),
                (By.ID, "userid"),
                (By.ID, "loginId"),
                # CSS 셀렉터
                (By.CSS_SELECTOR, "input[name*='id']"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.CSS_SELECTOR, "input[placeholder*='아이디']"),
                (By.CSS_SELECTOR, "input[placeholder*='ID']"),
                # XPath로 폼 내 첫 번째 텍스트 입력
                (By.XPATH, "//form//input[@type='text'][1]"),
                (By.XPATH, "//input[@type='text'][1]"),
                (By.XPATH, "//table//input[@type='text'][1]"),
                # 더 광범위한 검색
                (By.XPATH, "//input[contains(@name, 'id') or contains(@id, 'id')]"),
            ])
            
            if not id_field:
                logger.error("아이디 입력 필드를 찾을 수 없습니다")
                return False
            
            # 2. 패스워드 입력 필드 찾기
            password_field = self._find_login_field("패스워드", [
                (By.NAME, "admin_password"),
                (By.NAME, "password"),
                (By.NAME, "passwd"),
                (By.NAME, "pwd"),
                (By.NAME, "loginPwd"),
                (By.ID, "admin_password"),
                (By.ID, "password"),
                (By.ID, "passwd"),
                (By.ID, "loginPwd"),
                # CSS 셀렉터
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.CSS_SELECTOR, "input[name*='pass']"),
                (By.CSS_SELECTOR, "input[placeholder*='패스워드']"),
                (By.CSS_SELECTOR, "input[placeholder*='비밀번호']"),
                # XPath
                (By.XPATH, "//form//input[@type='password'][1]"),
                (By.XPATH, "//input[@type='password'][1]"),
                (By.XPATH, "//table//input[@type='password'][1]"),
            ])
            
            if not password_field:
                logger.error("패스워드 입력 필드를 찾을 수 없습니다")
                return False
            
            # 3. 필드에 값 입력
            admin_id = self.credentials["cafe24"]["admin_id"]
            admin_password = self.credentials["cafe24"]["admin_password"]
            
            logger.info("로그인 정보 입력 중...")
            
            # 기존 값 지우고 입력
            id_field.clear()
            time.sleep(0.5)
            id_field.send_keys(admin_id)
            
            password_field.clear()
            time.sleep(0.5)
            password_field.send_keys(admin_password)
            
            logger.info("로그인 정보 입력 완료")
            return True
            
        except Exception as e:
            logger.error(f"로그인 폼 입력 중 오류: {e}")
            return False

    def _find_login_field(self, field_name: str, selectors: list):
        """로그인 필드 찾기"""
        for selector_type, selector_value in selectors:
            try:
                element = WebDriverWait(self.browser_manager.driver, 2).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                logger.info(f"{field_name} 필드 발견: {selector_type} = {selector_value}")
                return element
            except TimeoutException:
                continue
            except Exception as e:
                logger.debug(f"{field_name} 필드 찾기 실패 ({selector_value}): {e}")
                continue
        
        logger.warning(f"{field_name} 필드를 찾을 수 없습니다")
        return None

    def _submit_login(self) -> bool:
        """로그인 버튼 클릭"""
        try:
            # 로그인 버튼 찾기
            login_button = self._find_login_button()
            if not login_button:
                # Enter 키로 대체 시도
                logger.info("로그인 버튼이 없어 Enter 키로 시도")
                from selenium.webdriver.common.keys import Keys
                password_field = self.browser_manager.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                password_field.send_keys(Keys.RETURN)
                return True
            
            # 버튼 클릭
            logger.info("로그인 버튼 클릭")
            login_button.click()
            
            # 클릭 후 알림창 처리
            time.sleep(1)
            self._handle_alerts()
            
            return True
            
        except Exception as e:
            logger.error(f"로그인 버튼 클릭 중 오류: {e}")
            return False

    def _find_login_button(self):
        """로그인 버튼 찾기"""
        button_selectors = [
            (By.CSS_SELECTOR, "input[type='submit']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, "input[value*='로그인']"),
            (By.CSS_SELECTOR, "button:contains('로그인')"),
            (By.XPATH, "//input[@value='로그인' or @value='LOGIN' or @value='login']"),
            (By.XPATH, "//button[contains(text(), '로그인') or contains(text(), 'LOGIN')]"),
            (By.XPATH, "//form//input[@type='submit'][1]"),
            (By.XPATH, "//form//button[1]"),
        ]
        
        for selector_type, selector_value in button_selectors:
            try:
                button = self.browser_manager.driver.find_element(selector_type, selector_value)
                if button.is_displayed() and button.is_enabled():
                    logger.info(f"로그인 버튼 발견: {selector_value}")
                    return button
            except:
                continue
        
        return None

    def _verify_login_success(self) -> bool:
        """로그인 성공 확인"""
        try:
            # 여러 성공 지표 확인
            success_indicators = [
                # URL 변화 확인
                ("URL", lambda: "admin" in self.browser_manager.driver.current_url.lower()),
                ("URL", lambda: "manage" in self.browser_manager.driver.current_url.lower()),
                # 페이지 요소 확인
                ("요소", lambda: self._check_admin_elements()),
            ]
            
            for indicator_name, check_func in success_indicators:
                try:
                    if check_func():
                        logger.info(f"로그인 성공 확인: {indicator_name}")
                        return True
                except:
                    continue
            
            # 마지막으로 페이지 제목 확인
            current_url = self.browser_manager.driver.current_url
            page_title = self.browser_manager.driver.title
            
            logger.info(f"현재 URL: {current_url}")
            logger.info(f"페이지 제목: {page_title}")
            
            # 관리자 관련 키워드가 있으면 성공으로 간주
            admin_keywords = ["admin", "manage", "관리", "운영", "상품", "주문"]
            for keyword in admin_keywords:
                if keyword in current_url.lower() or keyword in page_title.lower():
                    logger.info(f"관리자 키워드 '{keyword}' 감지 - 로그인 성공으로 판단")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"로그인 성공 확인 중 오류: {e}")
            return False

    def _check_admin_elements(self) -> bool:
        """관리자 페이지 요소 확인"""
        admin_selectors = [
            "a[href*='product']",  # 상품 관리
            "a[href*='order']",    # 주문 관리
            ".gnb",                # 글로벌 네비게이션
            ".admin-menu",         # 관리자 메뉴
            "#admin-container",    # 관리자 컨테이너
        ]
        
        for selector in admin_selectors:
            try:
                elements = self.browser_manager.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return True
            except:
                continue
        
        return False

    def logout(self) -> bool:
        """로그아웃"""
        try:
            if not self.is_logged_in:
                return True
                
            logger.info("로그아웃 시도")
            
            # 로그아웃 버튼 찾기
            logout_selectors = [
                "a[href*='logout']",
                "button:contains('로그아웃')",
                ".logout",
            ]
            
            for selector in logout_selectors:
                try:
                    logout_element = self.browser_manager.driver.find_element(By.CSS_SELECTOR, selector)
                    if logout_element.is_displayed():
                        logout_element.click()
                        self.is_logged_in = False
                        logger.info("로그아웃 완료")
                        return True
                except:
                    continue
            
            logger.warning("로그아웃 버튼을 찾을 수 없습니다")
            return False
            
        except Exception as e:
            logger.error(f"로그아웃 중 오류: {e}")
            return False