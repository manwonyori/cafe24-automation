# CSV 파일 폴더 구조 설계

## 📁 전체 폴더 구조

```
csv_files/
├── downloads/              # 다운로드한 파일들
│   ├── products/          # 상품 데이터
│   │   └── 2025-08-05/
│   │       ├── products_143022.csv
│   │       └── products_143022.csv.meta.json
│   ├── related_products/  # 관련상품
│   │   └── 2025-08-05/
│   ├── inventory/         # 재고
│   ├── categories/        # 카테고리
│   └── templates/         # 템플릿
│
├── uploads/               # 업로드 파일들
│   ├── pending/          # 대기중
│   ├── processing/       # 처리중
│   ├── completed/        # 완료
│   │   └── 2025-08-05/
│   └── failed/           # 실패
│       └── error_files/
│
├── backups/              # 백업
│   ├── daily/           # 일별
│   ├── weekly/          # 주별
│   └── monthly/         # 월별
│
└── logs/                # 로그
    ├── upload/          # 업로드 로그
    ├── download/        # 다운로드 로그
    └── errors/          # 에러 로그
```

## 🔄 워크플로우

### 다운로드 프로세스
```python
1. 사용자 요청
   ↓
2. 데이터 조회 (API)
   ↓
3. CSV 생성
   ↓
4. 폴더 자동 생성
   downloads/products/2025-08-05/
   ↓
5. 파일 저장
   products_143022.csv
   products_143022.csv.meta.json (메타데이터)
```

### 업로드 프로세스
```python
1. 파일 업로드
   → uploads/pending/
   
2. 유효성 검사
   → uploads/processing/
   
3. API 처리
   성공 → uploads/completed/2025-08-05/
   실패 → uploads/failed/
   
4. 메타데이터 기록
   .meta.json 파일에 처리 결과 저장
```

## 📊 메타데이터 구조

```json
{
  "type": "products",
  "original_name": "products.csv",
  "timestamp": "2025-08-05T14:30:22",
  "size": 125840,
  "records": 171,
  "status": "completed",
  "processing_time": 3.2,
  "errors": [],
  "user": "admin"
}
```

## 🎯 주요 기능

### 1. **자동 폴더 생성**
- 날짜별 자동 분류
- 파일 타입별 분리

### 2. **파일 추적**
- 모든 파일에 메타데이터
- 처리 상태 실시간 추적

### 3. **백업 관리**
- 일/주/월 단위 자동 백업
- 오래된 파일 자동 정리

### 4. **통계 제공**
```python
# 폴더별 통계
{
  "downloads": {
    "file_count": 156,
    "total_size_mb": 45.2
  },
  "uploads": {
    "completed": 142,
    "failed": 8,
    "success_rate": 94.7
  }
}
```

## 💻 구현 코드 통합

```python
# app.py에 추가
from csv_folder_structure import CSVFolderManager

# 초기화
csv_manager = CSVFolderManager("csv_files")

# 다운로드 시
@app.route('/api/csv/export')
def export_csv():
    # CSV 생성
    csv_content = generate_csv()
    
    # 폴더에 저장
    filepath = csv_manager.save_download_file(
        file_type="products",
        filename="products.csv",
        content=csv_content
    )
    
    return send_file(filepath)

# 업로드 시
@app.route('/api/csv/import', methods=['POST'])
def import_csv():
    file = request.files['file']
    
    # 1. pending으로 저장
    processing_path = csv_manager.process_upload_file(
        source_path=file,
        file_type="products"
    )
    
    # 2. 처리
    try:
        result = process_csv(processing_path)
        # 3. 완료
        csv_manager.complete_upload(processing_path, success=True)
    except Exception as e:
        # 3. 실패
        csv_manager.complete_upload(
            processing_path, 
            success=False,
            error_msg=str(e)
        )
```

## 🔧 관리 기능

### 1. **폴더 정리**
```bash
# 30일 이상 된 파일 자동 삭제
python -c "from csv_folder_structure import CSVFolderManager; CSVFolderManager().cleanup_old_files(30)"
```

### 2. **백업 실행**
```bash
# 일별 백업 실행
python -c "from csv_folder_structure import CSVFolderManager; CSVFolderManager().create_daily_backup()"
```

### 3. **통계 확인**
```bash
# 폴더 통계 보기
python csv_folder_structure.py
```

## 📌 장점

1. **체계적 관리**: 날짜/타입별 자동 분류
2. **추적 가능**: 모든 파일의 이력 관리
3. **에러 처리**: 실패 파일 별도 보관
4. **확장성**: 새로운 파일 타입 쉽게 추가
5. **자동화**: 백업/정리 자동 실행

이 구조로 CSV 파일을 체계적으로 관리할 수 있습니다!