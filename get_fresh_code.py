#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새 인증 코드 받기
"""
import webbrowser
import time

def get_new_auth_code():
    """새 인증 코드 받기"""
    print("=" * 80)
    print("새 인증 코드 받기")
    print("=" * 80)
    
    auth_url = "https://manwonyori.cafe24api.com/api/v2/oauth/authorize?response_type=code&client_id=9bPpABwHB5mtkCEAfIeuNK&redirect_uri=https://cafe24-automation.onrender.com/callback&scope=mall.read_product,mall.write_product,mall.read_order,mall.write_order,mall.read_customer"
    
    print(f"\n1. 이 URL을 브라우저에서 열어주세요:")
    print(f"{auth_url}")
    print(f"\n2. Cafe24에 로그인하고 앱을 승인하세요")
    print(f"3. 리다이렉트된 URL에서 code= 뒤의 코드를 복사하세요")
    print(f"   예: https://cafe24-automation.onrender.com/callback?code=ABC123")
    print(f"   여기서 ABC123 부분만 복사")
    print(f"\n⚠️ 주의: 코드는 10분 후 만료됩니다!")
    
    # 브라우저 열기 시도
    try:
        webbrowser.open(auth_url)
        print(f"\n✓ 브라우저가 자동으로 열렸습니다")
    except:
        print(f"\n× 브라우저를 수동으로 열어주세요")
    
    return input(f"\n새 인증 코드를 입력하세요: ").strip()

if __name__ == "__main__":
    code = get_new_auth_code()
    if code:
        print(f"\n받은 코드: {code}")
        print(f"이제 이 코드를 저에게 알려주세요!")
    else:
        print(f"\n코드가 입력되지 않았습니다")