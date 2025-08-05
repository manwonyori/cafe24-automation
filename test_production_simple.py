#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
프로덕션 서버 기능 테스트 (Unicode 없는 버전)
"""
import requests
import json
from datetime import datetime

# 프로덕션 URL
BASE_URL = "https://cafe24-automation.onrender.com"

def test_csv_template():
    """CSV 템플릿 다운로드"""
    print("1. CSV Template Download Test...")
    try:
        response = requests.get(f"{BASE_URL}/api/csv/template")
        if response.status_code == 200:
            print("   [OK] Success - Template downloaded")
            return True
        else:
            print(f"   [FAIL] Failed - Status: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False

def test_margin_preview():
    """마진 미리보기 테스트"""
    print("\n2. Margin Preview Test...")
    try:
        # 임의의 상품번호로 테스트
        preview_data = {
            "product_nos": ["171", "170", "169"],  # 실제 상품번호
            "target_margin": 30,
            "update_type": "selling"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/margin/preview-changes",
            json=preview_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   [OK] Success - Preview generated")
                preview_count = len(data.get('preview', []))
                print(f"   - Preview items: {preview_count}")
                return True
            else:
                print(f"   [FAIL] Failed: {data.get('error')}")
                return False
        else:
            print(f"   [FAIL] Failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False

def test_csv_export():
    """CSV Export 테스트"""
    print("\n3. CSV Export Test...")
    try:
        response = requests.get(f"{BASE_URL}/api/csv/export")
        
        if response.status_code == 200:
            print("   [OK] Success - CSV exported")
            # Content-Type 확인
            content_type = response.headers.get('Content-Type', '')
            if 'csv' in content_type or 'octet-stream' in content_type:
                print("   - Correct content type")
            return True
        else:
            print(f"   [FAIL] Failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False

def test_margin_dashboard():
    """마진 대시보드 페이지 테스트"""
    print("\n4. Margin Dashboard Page Test...")
    try:
        response = requests.get(f"{BASE_URL}/margin-dashboard")
        
        if response.status_code == 200:
            # 새로운 기능이 포함되어 있는지 확인
            content = response.text
            has_preview = "previewMarginChanges" in content
            has_export = "exportMarginUpdatedProducts" in content
            
            print("   [OK] Page loaded successfully")
            print(f"   - Preview function: {'[OK]' if has_preview else '[FAIL]'}")
            print(f"   - Export function: {'[OK]' if has_export else '[FAIL]'}")
            
            return has_preview and has_export
        else:
            print(f"   [FAIL] Failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False

def main():
    print("="*60)
    print("Cafe24 Production Server Feature Test")
    print(f"Server: {BASE_URL}")
    print("="*60)
    
    tests = {
        "CSV Template Download": test_csv_template(),
        "Margin Preview API": test_margin_preview(),
        "CSV Export API": test_csv_export(),
        "Margin Dashboard UI": test_margin_dashboard()
    }
    
    print("\n" + "="*60)
    print("Test Results:")
    print("="*60)
    
    passed = sum(1 for result in tests.values() if result)
    failed = len(tests) - passed
    
    for test_name, result in tests.items():
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{test_name:25} : {status}")
    
    print("="*60)
    print(f"Total: {len(tests)} | Passed: {passed} | Failed: {failed}")
    
    if failed > 0:
        print("\n[WARNING] Some tests failed. Checking deployment status...")
        # 배포 상태 확인
        try:
            status_response = requests.get(f"{BASE_URL}/api/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"Server status: {status_data.get('status')}")
                print(f"Token valid: {status_data.get('token_status', {}).get('valid')}")
        except:
            pass
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())