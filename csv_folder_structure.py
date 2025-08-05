#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV 업로드/다운로드 폴더 구조 관리 시스템
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
import json

class CSVFolderManager:
    def __init__(self, base_path="csv_files"):
        self.base_path = Path(base_path)
        self.setup_folder_structure()
        
    def setup_folder_structure(self):
        """기본 폴더 구조 생성"""
        # 메인 폴더들
        folders = [
            # 다운로드 폴더
            "downloads/products",          # 상품 정보
            "downloads/related_products",  # 관련상품
            "downloads/inventory",         # 재고
            "downloads/categories",        # 카테고리
            "downloads/templates",         # 템플릿
            
            # 업로드 폴더
            "uploads/pending",            # 대기중
            "uploads/processing",         # 처리중
            "uploads/completed",          # 완료
            "uploads/failed",             # 실패
            
            # 백업 폴더
            "backups/daily",              # 일별 백업
            "backups/weekly",             # 주별 백업
            "backups/monthly",            # 월별 백업
            
            # 로그 폴더
            "logs/upload",                # 업로드 로그
            "logs/download",              # 다운로드 로그
            "logs/errors"                 # 에러 로그
        ]
        
        for folder in folders:
            folder_path = self.base_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            
        # README 파일 생성
        self.create_readme_files()
        
    def create_readme_files(self):
        """각 폴더에 README 파일 생성"""
        readme_contents = {
            "downloads": """# 다운로드 폴더
- products/: 상품 데이터 다운로드
- related_products/: 관련상품 데이터
- inventory/: 재고 데이터
- categories/: 카테고리 데이터
- templates/: 빈 템플릿 파일
""",
            "uploads": """# 업로드 폴더
- pending/: 업로드 대기 파일
- processing/: 처리 중인 파일
- completed/: 처리 완료 파일 (날짜별 정리)
- failed/: 처리 실패 파일
""",
            "backups": """# 백업 폴더
- daily/: 매일 자동 백업
- weekly/: 주간 백업
- monthly/: 월간 백업
""",
            "logs": """# 로그 폴더
- upload/: 업로드 작업 로그
- download/: 다운로드 작업 로그
- errors/: 에러 로그
"""
        }
        
        for folder, content in readme_contents.items():
            readme_path = self.base_path / folder / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def get_download_path(self, file_type, include_date=True):
        """다운로드 파일 경로 생성"""
        base_folder = self.base_path / "downloads" / file_type
        
        if include_date:
            date_folder = datetime.now().strftime("%Y-%m-%d")
            folder = base_folder / date_folder
        else:
            folder = base_folder
            
        folder.mkdir(parents=True, exist_ok=True)
        return folder
    
    def get_upload_path(self, status="pending"):
        """업로드 파일 경로 생성"""
        folder = self.base_path / "uploads" / status
        
        if status == "completed":
            # 완료된 파일은 날짜별로 정리
            date_folder = datetime.now().strftime("%Y-%m-%d")
            folder = folder / date_folder
            
        folder.mkdir(parents=True, exist_ok=True)
        return folder
    
    def save_download_file(self, file_type, filename, content):
        """다운로드 파일 저장"""
        folder = self.get_download_path(file_type)
        
        # 타임스탬프 추가
        timestamp = datetime.now().strftime("%H%M%S")
        name, ext = os.path.splitext(filename)
        filename_with_time = f"{name}_{timestamp}{ext}"
        
        filepath = folder / filename_with_time
        
        # 파일 저장
        if isinstance(content, bytes):
            with open(filepath, 'wb') as f:
                f.write(content)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # 메타데이터 저장
        self.save_metadata(filepath, {
            'type': file_type,
            'original_name': filename,
            'download_time': datetime.now().isoformat(),
            'size': os.path.getsize(filepath)
        })
        
        return filepath
    
    def process_upload_file(self, source_path, file_type):
        """업로드 파일 처리"""
        filename = os.path.basename(source_path)
        
        # 1. pending으로 이동
        pending_folder = self.get_upload_path("pending")
        pending_path = pending_folder / filename
        shutil.copy2(source_path, pending_path)
        
        # 2. processing으로 이동
        processing_folder = self.get_upload_path("processing")
        processing_path = processing_folder / filename
        shutil.move(str(pending_path), str(processing_path))
        
        # 메타데이터 저장
        self.save_metadata(processing_path, {
            'type': file_type,
            'upload_time': datetime.now().isoformat(),
            'status': 'processing'
        })
        
        return processing_path
    
    def complete_upload(self, processing_path, success=True, error_msg=None):
        """업로드 완료 처리"""
        filename = os.path.basename(processing_path)
        
        if success:
            # 성공: completed로 이동
            completed_folder = self.get_upload_path("completed")
            final_path = completed_folder / filename
            status = "completed"
        else:
            # 실패: failed로 이동
            failed_folder = self.get_upload_path("failed")
            final_path = failed_folder / filename
            status = "failed"
        
        shutil.move(str(processing_path), str(final_path))
        
        # 메타데이터 업데이트
        self.update_metadata(final_path, {
            'status': status,
            'completed_time': datetime.now().isoformat(),
            'error': error_msg
        })
        
        return final_path
    
    def save_metadata(self, filepath, metadata):
        """파일 메타데이터 저장"""
        meta_path = str(filepath) + ".meta.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def update_metadata(self, filepath, updates):
        """메타데이터 업데이트"""
        meta_path = str(filepath) + ".meta.json"
        
        # 기존 메타데이터 읽기
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {}
        
        # 업데이트
        metadata.update(updates)
        
        # 저장
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def create_daily_backup(self):
        """일별 백업 생성"""
        date_str = datetime.now().strftime("%Y%m%d")
        backup_folder = self.base_path / "backups" / "daily" / date_str
        backup_folder.mkdir(parents=True, exist_ok=True)
        
        # downloads 폴더 백업
        downloads_folder = self.base_path / "downloads"
        if downloads_folder.exists():
            shutil.copytree(
                downloads_folder,
                backup_folder / "downloads",
                dirs_exist_ok=True
            )
        
        return backup_folder
    
    def get_folder_stats(self):
        """폴더 통계 정보"""
        stats = {}
        
        for folder_type in ["downloads", "uploads", "backups", "logs"]:
            folder_path = self.base_path / folder_type
            if folder_path.exists():
                file_count = sum(1 for f in folder_path.rglob('*') if f.is_file() and not f.name.endswith('.meta.json'))
                total_size = sum(f.stat().st_size for f in folder_path.rglob('*') if f.is_file())
                
                stats[folder_type] = {
                    'file_count': file_count,
                    'total_size': total_size,
                    'size_mb': round(total_size / 1024 / 1024, 2)
                }
        
        return stats
    
    def cleanup_old_files(self, days=30):
        """오래된 파일 정리"""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        cleaned_files = []
        
        # uploads/completed와 uploads/failed 폴더 정리
        for status in ["completed", "failed"]:
            folder = self.base_path / "uploads" / status
            if folder.exists():
                for file in folder.rglob('*'):
                    if file.is_file() and file.stat().st_mtime < cutoff_date:
                        cleaned_files.append(str(file))
                        file.unlink()
        
        return cleaned_files

# 사용 예시
if __name__ == "__main__":
    # 폴더 매니저 생성
    manager = CSVFolderManager()
    
    # 폴더 구조 확인
    print("폴더 구조가 생성되었습니다.")
    print("\n폴더 통계:")
    stats = manager.get_folder_stats()
    for folder, info in stats.items():
        print(f"  {folder}: {info['file_count']}개 파일, {info['size_mb']}MB")