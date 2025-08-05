#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render API를 통한 Cafe24 환경변수 자동 설정 및 배포
"""

import os
import json
import requests
import time
from datetime import datetime


class RenderAutoDeployer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('RENDER_API_KEY')
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def load_cafe24_config(self):
        """Cafe24 설정 파일 로드"""
        # 여러 경로에서 config 파일 찾기
        config_paths = [
            "C:\\Users\\8899y\\Documents\\카페24_프로젝트\\01_ACTIVE_PROJECT\\config\\oauth_token.json",
            "config/oauth_token.json",
            "../카페24_프로젝트/01_ACTIVE_PROJECT/config/oauth_token.json"
        ]
        
        for path in config_paths:
            if os.path.exists(path):
                print(f"Found config at: {path}")
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
                    
        raise FileNotFoundError("Cafe24 config file not found")
        
    def get_services(self):
        """Render 서비스 목록 조회"""
        response = requests.get(
            f"{self.base_url}/services",
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get services: {response.text}")
            
        return response.json()
        
    def find_cafe24_service(self):
        """cafe24-automation 서비스 찾기"""
        services = self.get_services()
        
        for service in services:
            if 'cafe24' in service.get('name', '').lower():
                return service
                
        raise Exception("cafe24-automation service not found")
        
    def update_env_vars(self, service_id, env_vars):
        """환경변수 업데이트"""
        # 현재 환경변수 조회
        response = requests.get(
            f"{self.base_url}/services/{service_id}/env-vars",
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get env vars: {response.text}")
            
        current_vars = response.json()
        
        # 새 환경변수 추가/업데이트
        env_var_list = []
        for key, value in env_vars.items():
            env_var_list.append({
                "key": key,
                "value": value
            })
            
        # 환경변수 설정
        response = requests.put(
            f"{self.base_url}/services/{service_id}/env-vars",
            headers=self.headers,
            json=env_var_list
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to update env vars: {response.text}")
            
        return response.json()
        
    def trigger_deploy(self, service_id):
        """수동 배포 트리거"""
        response = requests.post(
            f"{self.base_url}/services/{service_id}/deploys",
            headers=self.headers,
            json={"clearCache": "clear"}
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to trigger deploy: {response.text}")
            
        return response.json()
        
    def wait_for_deploy(self, service_id, deploy_id, max_wait=600):
        """배포 완료 대기"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = requests.get(
                f"{self.base_url}/services/{service_id}/deploys/{deploy_id}",
                headers=self.headers
            )
            
            if response.status_code != 200:
                print(f"Failed to check deploy status: {response.text}")
                time.sleep(10)
                continue
                
            deploy = response.json()
            status = deploy.get('status')
            
            print(f"Deploy status: {status}")
            
            if status == 'live':
                return True
            elif status in ['failed', 'canceled']:
                raise Exception(f"Deploy failed with status: {status}")
                
            time.sleep(10)
            
        return False
        
    def run(self):
        """전체 프로세스 실행"""
        print("=" * 60)
        print("Render Cafe24 자동 배포 시작")
        print(f"시작 시간: {datetime.now()}")
        print("=" * 60)
        
        try:
            # 1. Cafe24 설정 로드
            print("\n1. Cafe24 설정 로드 중...")
            config = self.load_cafe24_config()
            
            # 환경변수 매핑
            env_vars = {
                "CAFE24_MALL_ID": config.get('mall_id'),
                "CAFE24_CLIENT_ID": config.get('client_id'),
                "CAFE24_CLIENT_SECRET": config.get('client_secret'),
                "CAFE24_REDIRECT_URI": "https://cafe24-automation.onrender.com/callback",
                "CAFE24_ACCESS_TOKEN": config.get('access_token'),
                "CAFE24_REFRESH_TOKEN": config.get('refresh_token')
            }
            
            print("   로드된 설정:")
            print(f"   - Mall ID: {env_vars['CAFE24_MALL_ID']}")
            print(f"   - Client ID: {env_vars['CAFE24_CLIENT_ID'][:10]}...")
            print(f"   - Access Token: {env_vars['CAFE24_ACCESS_TOKEN'][:10]}...")
            
            # 2. Render 서비스 찾기
            print("\n2. Render 서비스 검색 중...")
            service = self.find_cafe24_service()
            service_id = service['id']
            print(f"   서비스 찾음: {service['name']} (ID: {service_id})")
            
            # 3. 환경변수 업데이트
            print("\n3. 환경변수 업데이트 중...")
            self.update_env_vars(service_id, env_vars)
            print("   ✓ 환경변수 설정 완료")
            
            # 4. 배포 트리거
            print("\n4. 배포 시작 중...")
            deploy = self.trigger_deploy(service_id)
            deploy_id = deploy['id']
            print(f"   배포 시작됨 (ID: {deploy_id})")
            
            # 5. 배포 완료 대기
            print("\n5. 배포 완료 대기 중...")
            print("   (약 2-5분 소요)")
            
            if self.wait_for_deploy(service_id, deploy_id):
                print("\n✅ 배포 성공!")
                print(f"   URL: https://{service.get('serviceDetails', {}).get('url', 'cafe24-automation.onrender.com')}")
                
                # 6. 배포 확인
                print("\n6. 배포 확인 중...")
                time.sleep(10)  # 안정화 대기
                
                test_url = f"https://{service.get('serviceDetails', {}).get('url', 'cafe24-automation.onrender.com')}"
                response = requests.get(test_url)
                
                if response.status_code == 200:
                    data = response.json()
                    mode = data.get('mode', 'unknown')
                    print(f"   시스템 모드: {mode}")
                    
                    if mode == 'production':
                        print("\n🎉 Production 모드 활성화 성공!")
                    else:
                        print("\n⚠️ 여전히 Demo 모드입니다. 환경변수를 확인하세요.")
                        
            else:
                print("\n❌ 배포 시간 초과")
                
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            
        print("\n" + "=" * 60)
        print("완료!")


def manual_setup_guide():
    """수동 설정 가이드"""
    print("\n📋 Render API Key가 없는 경우 수동 설정 방법:")
    print("=" * 60)
    
    # config 로드
    config_path = "C:\\Users\\8899y\\Documents\\카페24_프로젝트\\01_ACTIVE_PROJECT\\config\\oauth_token.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        print("\n1. https://dashboard.render.com 로그인")
        print("2. cafe24-automation 서비스 선택")
        print("3. Environment 탭 클릭")
        print("4. 아래 환경변수 추가:\n")
        
        print(f"CAFE24_MALL_ID={config['mall_id']}")
        print(f"CAFE24_CLIENT_ID={config['client_id']}")
        print(f"CAFE24_CLIENT_SECRET={config['client_secret']}")
        print("CAFE24_REDIRECT_URI=https://cafe24-automation.onrender.com/callback")
        print(f"CAFE24_ACCESS_TOKEN={config['access_token']}")
        print(f"CAFE24_REFRESH_TOKEN={config['refresh_token']}")
        
        print("\n5. Save Changes 클릭")
        print("6. Manual Deploy > Deploy latest commit 클릭")
        print("\n✅ 2-5분 후 Production 모드로 전환됩니다.")
    else:
        print("설정 파일을 찾을 수 없습니다.")
        
    print("=" * 60)


def main():
    """메인 함수"""
    print("Cafe24 API Render 자동 배포 도구")
    print("=" * 60)
    
    # Render API Key 확인
    api_key = os.getenv('RENDER_API_KEY')
    
    if not api_key:
        print("\n⚠️ RENDER_API_KEY 환경변수가 설정되지 않았습니다.")
        print("\nRender API Key 얻는 방법:")
        print("1. https://dashboard.render.com 로그인")
        print("2. Account Settings > API Keys")
        print("3. Create API Key")
        print("4. 환경변수 설정: set RENDER_API_KEY=your-key-here")
        
        manual_setup_guide()
        
        # API Key 입력 옵션
        answer = input("\nAPI Key를 지금 입력하시겠습니까? (y/n): ")
        if answer.lower() == 'y':
            api_key = input("Render API Key: ").strip()
            if api_key:
                deployer = RenderAutoDeployer(api_key)
                deployer.run()
        
    else:
        # 자동 실행
        deployer = RenderAutoDeployer()
        deployer.run()


if __name__ == "__main__":
    main()