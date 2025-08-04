#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OAuth 인증 라우트
"""
from flask import Blueprint, request, redirect, jsonify, render_template_string
import requests
import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlencode
from config import OAUTH_CONFIG

oauth_bp = Blueprint('oauth', __name__)

@oauth_bp.route('/auth')
def auth():
    """OAuth 인증 시작"""
    mall_id = request.args.get('mall_id', 'manwonyori')
    
    # 인증 페이지 HTML
    auth_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cafe24 OAuth 인증</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f5f7fa;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }
            .auth-container {
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                max-width: 500px;
                width: 90%;
            }
            h1 {
                color: #1a73e8;
                margin-bottom: 20px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
                color: #333;
            }
            input {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 16px;
            }
            .btn {
                background: #1a73e8;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                cursor: pointer;
                width: 100%;
                margin-top: 10px;
            }
            .btn:hover {
                background: #1557b0;
            }
            .info {
                background: #e8f1ff;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
                font-size: 14px;
                color: #1a73e8;
            }
            .status {
                margin-top: 20px;
                padding: 15px;
                border-radius: 6px;
                font-size: 14px;
            }
            .status.success {
                background: #e8f5e9;
                color: #2e7d32;
            }
            .status.error {
                background: #ffebee;
                color: #c62828;
            }
        </style>
    </head>
    <body>
        <div class="auth-container">
            <h1>🔐 Cafe24 OAuth 인증</h1>
            
            <div class="info">
                ℹ️ Cafe24 앱스토어에서 앱을 설치한 후 인증을 진행해주세요.
            </div>
            
            <form method="get" action="/auth/start">
                <div class="form-group">
                    <label for="mall_id">Mall ID</label>
                    <input type="text" id="mall_id" name="mall_id" value="manwonyori" required>
                </div>
                
                <div class="form-group">
                    <label for="client_secret">Client Secret</label>
                    <input type="password" id="client_secret" name="client_secret" placeholder="앱 설정에서 확인" required>
                </div>
                
                <button type="submit" class="btn">인증 시작</button>
            </form>
            
            <div class="status">
                <strong>현재 설정:</strong><br>
                Client ID: """ + OAUTH_CONFIG['client_id'][:10] + """...<br>
                Redirect URI: """ + OAUTH_CONFIG['redirect_uri'] + """
            </div>
        </div>
    </body>
    </html>
    """
    
    return auth_html

@oauth_bp.route('/auth/start')
def auth_start():
    """OAuth 인증 URL로 리다이렉트"""
    mall_id = request.args.get('mall_id', 'manwonyori')
    client_secret = request.args.get('client_secret', '')
    
    # Client Secret 임시 저장 (세션이나 환경변수로 관리 권장)
    os.environ['CAFE24_CLIENT_SECRET'] = client_secret
    
    # OAuth 인증 URL 생성
    auth_params = {
        'response_type': 'code',
        'client_id': OAUTH_CONFIG['client_id'],
        'redirect_uri': OAUTH_CONFIG['redirect_uri'],
        'scope': OAUTH_CONFIG['scope'],
        'state': mall_id  # state에 mall_id 전달
    }
    
    auth_url = f"https://{mall_id}.cafe24api.com/api/v2/oauth/authorize?" + urlencode(auth_params)
    
    return redirect(auth_url)

@oauth_bp.route('/auth/callback')
def auth_callback():
    """OAuth 콜백 처리"""
    code = request.args.get('code')
    state = request.args.get('state', 'manwonyori')  # state에서 mall_id 복구
    error = request.args.get('error')
    
    if error:
        return jsonify({'error': error, 'error_description': request.args.get('error_description')}), 400
    
    if not code:
        return jsonify({'error': 'No authorization code received'}), 400
    
    # 토큰 교환
    mall_id = state
    client_secret = os.environ.get('CAFE24_CLIENT_SECRET', '')
    
    token_url = f"https://{mall_id}.cafe24api.com/api/v2/oauth/token"
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': OAUTH_CONFIG['redirect_uri']
    }
    
    try:
        response = requests.post(
            token_url,
            data=token_data,
            auth=(OAUTH_CONFIG['client_id'], client_secret)
        )
        
        if response.status_code == 200:
            token_info = response.json()
            
            # 토큰 저장
            now = datetime.now()
            token_data = {
                'mall_id': mall_id,
                'client_id': OAUTH_CONFIG['client_id'],
                'access_token': token_info['access_token'],
                'refresh_token': token_info['refresh_token'],
                'expires_in': token_info.get('expires_in', 7200),
                'refresh_token_expires_in': token_info.get('refresh_token_expires_in', 1209600),
                'token_date': now.isoformat(),
                'expires_at': (now + timedelta(seconds=token_info.get('expires_in', 7200))).isoformat(),
                'refresh_token_expires_at': (now + timedelta(seconds=token_info.get('refresh_token_expires_in', 1209600))).isoformat()
            }
            
            # 파일로 저장
            with open('oauth_token.json', 'w', encoding='utf-8') as f:
                json.dump(token_data, f, ensure_ascii=False, indent=2)
            
            # 영구 저장소에 저장
            try:
                from persistent_token_manager import persistent_token_manager
                persistent_token_manager.save_token(token_data)
                print("[OK] 토큰이 영구 저장소에 저장됨")
            except Exception as e:
                print(f"[WARN] 영구 저장소 저장 실패: {str(e)}")
            
            # 환경 변수로도 설정 (서버 재시작 없이 즉시 반영)
            os.environ['CAFE24_ACCESS_TOKEN'] = token_info['access_token']
            os.environ['CAFE24_REFRESH_TOKEN'] = token_info['refresh_token']
            os.environ['CAFE24_MALL_ID'] = mall_id
            
            # 성공 페이지
            success_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>인증 성공</title>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: #f5f7fa;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        margin: 0;
                    }
                    .success-container {
                        background: white;
                        padding: 40px;
                        border-radius: 12px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        max-width: 500px;
                        text-align: center;
                    }
                    h1 {
                        color: #2e7d32;
                        margin-bottom: 20px;
                    }
                    .btn {
                        background: #1a73e8;
                        color: white;
                        padding: 12px 24px;
                        border: none;
                        border-radius: 6px;
                        font-size: 16px;
                        cursor: pointer;
                        text-decoration: none;
                        display: inline-block;
                        margin-top: 20px;
                    }
                    .info {
                        background: #e8f5e9;
                        padding: 15px;
                        border-radius: 6px;
                        margin: 20px 0;
                        font-size: 14px;
                    }
                </style>
            </head>
            <body>
                <div class="success-container">
                    <h1>✅ 인증 성공!</h1>
                    <p>Cafe24 OAuth 인증이 성공적으로 완료되었습니다.</p>
                    
                    <div class="info">
                        <strong>Mall ID:</strong> """ + mall_id + """<br>
                        <strong>토큰 만료:</strong> """ + str(token_info.get('expires_in', 0) // 60) + """분 후<br>
                        <strong>자동 갱신:</strong> 활성화됨 (30분마다)
                    </div>
                    
                    <a href="/dashboard" class="btn">대시보드로 이동</a>
                </div>
            </body>
            </html>
            """
            
            return success_html
            
        else:
            return jsonify({
                'error': 'Token exchange failed',
                'status_code': response.status_code,
                'response': response.text
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'error': 'Token exchange error',
            'message': str(e)
        }), 500

@oauth_bp.route('/auth/status')
def auth_status():
    """현재 인증 상태 확인"""
    try:
        if os.path.exists('oauth_token.json'):
            with open('oauth_token.json', 'r', encoding='utf-8') as f:
                token_data = json.load(f)
            
            # 민감한 정보 제거
            safe_data = {
                'mall_id': token_data.get('mall_id'),
                'has_token': bool(token_data.get('access_token')),
                'token_date': token_data.get('token_date'),
                'expires_at': token_data.get('expires_at')
            }
            
            return jsonify({
                'authenticated': True,
                'token_info': safe_data
            })
        else:
            return jsonify({
                'authenticated': False,
                'message': 'No token found'
            })
    except Exception as e:
        return jsonify({
            'authenticated': False,
            'error': str(e)
        }), 500

# 라우트 등록 함수
def register_oauth_routes(app):
    """OAuth 라우트를 앱에 등록"""
    app.register_blueprint(oauth_bp)