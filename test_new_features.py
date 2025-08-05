#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새로운 기능 테스트
"""
import requests
import json
import os
from datetime import datetime

# 로컬 테스트 URL
BASE_URL = "http://localhost:5000"

def test_api_status():
    """API 상태 확인"""
    print("1. API 상태 확인...")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        data = response.json()
        print(f"   - Status: {data.get('status')}")
        print(f"   - Token valid: {data.get('token_status', {}).get('valid')}")
        return data.get('token_status', {}).get('valid', False)
    except Exception as e:
        print(f"   - Error: {e}")
        return False

def test_csv_template_download():
    """CSV 템플릿 다운로드 테스트"""
    print("\n2. CSV 템플릿 다운로드 테스트...")
    try:
        response = requests.get(f"{BASE_URL}/api/csv/template")
        if response.status_code == 200:
            print("   - Success: Template downloaded")
            # 파일 저장
            with open("test_template.csv", "wb") as f:
                f.write(response.content)
            print("   - Saved as: test_template.csv")
            return True
        else:
            print(f"   - Failed: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"   - Error: {e}")
        return False

def test_margin_preview():
    """마진 변경 미리보기 테스트"""
    print("\n3. 마진 변경 미리보기 테스트...")
    try:
        # 먼저 상품 목록 가져오기
        response = requests.get(f"{BASE_URL}/api/products/advanced?limit=5")
        if response.status_code != 200:
            print("   - Failed to get products")
            return False
        
        products = response.json().get('products', [])
        if not products:
            print("   - No products found")
            return False
        
        # 처음 3개 상품으로 테스트
        product_nos = [p['product_no'] for p in products[:3]]
        
        # 미리보기 요청
        preview_data = {
            "product_nos": product_nos,
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
                print("   - Success: Preview generated")
                for item in data.get('preview', [])[:2]:
                    print(f"     * {item['product_name']}: {item['current_price']} → {item['new_price']} ({item['change_percent']}%)")
                return True
            else:
                print(f"   - Failed: {data.get('error')}")
                return False
        else:
            print(f"   - Failed: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   - Error: {e}")
        return False

def test_margin_export():
    """마진 수정 CSV Export 테스트"""
    print("\n4. 마진 수정 CSV Export 테스트...")
    try:
        # 상품 목록 가져오기
        response = requests.get(f"{BASE_URL}/api/products/advanced?limit=3")
        if response.status_code != 200:
            print("   - Failed to get products")
            return False
        
        products = response.json().get('products', [])
        if not products:
            print("   - No products found")
            return False
        
        product_nos = [p['product_no'] for p in products]
        
        # Export 요청
        export_data = {
            "product_nos": product_nos,
            "target_margin": 25,
            "update_type": "selling"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/margin/export-updated",
            json=export_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("   - Success: CSV exported")
            # 파일 저장
            filename = f"margin_export_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"   - Saved as: {filename}")
            
            # CSV 내용 간단히 확인
            import pandas as pd
            df = pd.read_csv(filename, encoding='utf-8-sig', nrows=1)
            print(f"   - Columns: {len(df.columns)}")
            print(f"   - First product: {df.iloc[0]['상품명'] if '상품명' in df.columns else 'N/A'}")
            return True
        else:
            print(f"   - Failed: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   - Error: {e}")
        return False

def test_csv_export():
    """전체 상품 CSV Export 테스트"""
    print("\n5. 전체 상품 CSV Export 테스트...")
    try:
        response = requests.get(f"{BASE_URL}/api/csv/export")
        
        if response.status_code == 200:
            print("   - Success: Products exported to CSV")
            # 파일 저장
            filename = f"products_export_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"   - Saved as: {filename}")
            
            # CSV 확인
            import pandas as pd
            df = pd.read_csv(filename, encoding='utf-8-sig')
            print(f"   - Total products: {len(df)}")
            print(f"   - Columns: {len(df.columns)}")
            return True
        else:
            print(f"   - Failed: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   - Error: {e}")
        return False

def main():
    print("="*60)
    print("Cafe24 새로운 기능 테스트")
    print("="*60)
    
    # 결과 저장
    results = {
        "API Status": test_api_status(),
        "CSV Template": test_csv_template_download(),
        "Margin Preview": test_margin_preview(),
        "Margin Export": test_margin_export(),
        "CSV Export": test_csv_export()
    }
    
    print("\n" + "="*60)
    print("테스트 결과 요약:")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("="*60)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("="*60)
    
    # 실패한 테스트가 있으면 종료 코드 1
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())