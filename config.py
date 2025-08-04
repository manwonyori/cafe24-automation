#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cafe24 API 설정 - 중요한 상수들을 한 곳에서 관리
"""
import os

# API 버전 - 매우 중요! 변경하지 마세요
CAFE24_API_VERSION = '2024-06-01'  # 유효한 버전만 사용

# OAuth 설정
OAUTH_CONFIG = {
    'client_id': os.environ.get('CAFE24_CLIENT_ID', '9bPpABwHB5mtkCEAfIeuNK'),
    'client_secret': os.environ.get('CAFE24_CLIENT_SECRET', 'qtnWtUk2OZzua1SRa7gN3A'),
    'redirect_uri': os.environ.get('CAFE24_REDIRECT_URI', 'https://cafe24-automation.onrender.com/auth/callback'),
    'scope': 'mall.read_product,mall.write_product,mall.read_order,mall.read_supply,mall.write_supply'
}

# 기본 Mall ID
DEFAULT_MALL_ID = 'manwonyori'

# 토큰 설정
TOKEN_REFRESH_INTERVAL = 30  # 분 단위
TOKEN_REFRESH_BUFFER = 30    # 만료 전 갱신할 시간 (분)

# API 설정
API_CACHE_DURATION = 60  # 초 단위
API_TIMEOUT = 10  # 초 단위

# 로깅 설정
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FILE = 'app.log'