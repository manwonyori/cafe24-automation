"""
로깅 유틸리티 모듈
통합 로깅 설정 및 관리
"""

import os
import sys
import logging
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional
import colorlog


def setup_logger(
    name: str, 
    config_path: str = "config/settings.json",
    log_level: str = None
) -> logging.Logger:
    """
    로거 설정 및 생성
    
    Args:
        name: 로거 이름
        config_path: 설정 파일 경로
        log_level: 로그 레벨 (설정 파일보다 우선)
        
    Returns:
        설정된 로거
    """
    # 이미 설정된 로거가 있으면 반환
    if name in logging.Logger.manager.loggerDict:
        return logging.getLogger(name)
    
    # 설정 파일 로드
    config = _load_logging_config(config_path)
    
    # 로거 생성
    logger = logging.getLogger(name)
    
    # 로그 레벨 설정
    level = log_level or config.get("level", "INFO")
    logger.setLevel(getattr(logging, level.upper()))
    
    # 기존 핸들러 제거 (중복 방지)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 콘솔 핸들러 추가
    console_handler = _create_console_handler(config)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 추가
    file_handler = _create_file_handler(config)
    if file_handler:
        logger.addHandler(file_handler)
    
    # 부모 로거로부터 로그 전파 방지
    logger.propagate = False
    
    return logger


def _load_logging_config(config_path: str) -> dict:
    """로깅 설정 로드"""
    default_config = {
        "level": "INFO",
        "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "max_file_size": "10MB",
        "backup_count": 5
    }
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get("logging", default_config)
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return default_config


def _create_console_handler(config: dict) -> logging.Handler:
    """컬러 콘솔 핸들러 생성"""
    # 컬러 포맷터 설정
    color_formatter = colorlog.ColoredFormatter(
        fmt='%(log_color)s%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt=config.get("date_format", "%Y-%m-%d %H:%M:%S"),
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    console_handler = colorlog.StreamHandler(sys.stdout)
    console_handler.setFormatter(color_formatter)
    
    return console_handler


def _create_file_handler(config: dict) -> Optional[logging.Handler]:
    """파일 핸들러 생성"""
    try:
        # 로그 폴더 생성
        log_folder = config.get("log_folder", "./logs")
        os.makedirs(log_folder, exist_ok=True)
        
        # 로그 파일 경로
        log_file = os.path.join(log_folder, "selenium_automation.log")
        
        # 파일 크기 파싱
        max_bytes = _parse_file_size(config.get("max_file_size", "10MB"))
        backup_count = config.get("backup_count", 5)
        
        # 회전 파일 핸들러 생성
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        # 파일 포맷터 설정
        file_formatter = logging.Formatter(
            fmt=config.get("format", "%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
            datefmt=config.get("date_format", "%Y-%m-%d %H:%M:%S")
        )
        
        file_handler.setFormatter(file_formatter)
        
        return file_handler
        
    except Exception as e:
        print(f"파일 핸들러 생성 실패: {e}")
        return None


def _parse_file_size(size_str: str) -> int:
    """파일 크기 문자열을 바이트로 변환"""
    size_str = size_str.upper().strip()
    
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        # 숫자만 있으면 바이트로 간주
        return int(size_str)


def log_execution_time(func):
    """함수 실행 시간을 로깅하는 데코레이터"""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = datetime.now()
        
        try:
            logger.info(f"{func.__name__} 시작")
            result = func(*args, **kwargs)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"{func.__name__} 완료 (실행시간: {execution_time:.2f}초)")
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} 실패 (실행시간: {execution_time:.2f}초): {e}")
            raise
    
    return wrapper


def log_function_call(func):
    """함수 호출을 로깅하는 데코레이터"""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        # 인수 정보 (민감 정보 제외)
        safe_args = []
        for arg in args[1:]:  # self 제외
            if isinstance(arg, str) and len(arg) > 50:
                safe_args.append(f"{arg[:47]}...")
            else:
                safe_args.append(str(arg))
        
        safe_kwargs = {}
        for key, value in kwargs.items():
            if 'password' in key.lower() or 'secret' in key.lower():
                safe_kwargs[key] = "***"
            elif isinstance(value, str) and len(value) > 50:
                safe_kwargs[key] = f"{value[:47]}..."
            else:
                safe_kwargs[key] = value
        
        logger.debug(f"호출: {func.__name__}({', '.join(safe_args)}, {safe_kwargs})")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} 성공")
            return result
            
        except Exception as e:
            logger.error(f"{func.__name__} 실패: {e}")
            raise
    
    return wrapper


def create_session_logger(session_id: str = None) -> logging.Logger:
    """세션별 로거 생성"""
    if session_id is None:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logger_name = f"selenium_session_{session_id}"
    logger = setup_logger(logger_name)
    
    # 세션 시작 로그
    logger.info(f"=== Selenium 자동화 세션 시작 (ID: {session_id}) ===")
    
    return logger


class LogContext:
    """로그 컨텍스트 매니저"""
    
    def __init__(self, logger: logging.Logger, message: str, level: str = "INFO"):
        self.logger = logger
        self.message = message
        self.level = level.upper()
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        log_func = getattr(self.logger, self.level.lower())
        log_func(f"시작: {self.message}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            log_func = getattr(self.logger, self.level.lower())
            log_func(f"완료: {self.message} (실행시간: {execution_time:.2f}초)")
        else:
            self.logger.error(f"실패: {self.message} (실행시간: {execution_time:.2f}초) - {exc_val}")


# 전역 로거 인스턴스
default_logger = setup_logger("selenium_automation")