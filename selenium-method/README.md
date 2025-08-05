# Selenium 자동화 방식

> 🤖 Cafe24 관리자 페이지를 브라우저로 자동 제어하는 완전 자동화 시스템

## 📋 개요

API 방식의 한계(특히 가격 수정)를 극복하기 위한 Selenium 기반 자동화입니다. 관리자가 수동으로 하는 모든 작업을 자동화할 수 있습니다.

## 🚀 주요 기능

### ✅ 가격 수정 (완벽 지원!)
- CSV 파일로 대량 가격 수정
- 개별 상품 가격 변경
- 옵션 상품 가격 수정

### 📁 CSV 업로드
- 상품 일괄 등록
- 상품 정보 일괄 수정
- 재고 일괄 업데이트

### 🔧 기타 기능
- 자동 로그인
- 주문 처리
- 통계 다운로드
- 설정 변경

## 📂 폴더 구조

```
selenium-method/
├── config/
│   ├── settings.json      # 브라우저 설정
│   └── credentials.json   # 로그인 정보 (git ignore)
├── modules/
│   ├── browser.py        # 브라우저 관리
│   ├── login.py          # 로그인 처리
│   ├── navigation.py     # 페이지 이동
│   ├── price_updater.py  # 가격 수정
│   └── csv_uploader.py   # CSV 업로드
├── utils/
│   ├── logger.py         # 로깅
│   ├── wait_helper.py    # 대기 함수
│   └── error_handler.py  # 에러 처리
├── data/
│   ├── csv/             # CSV 파일
│   └── screenshots/     # 스크린샷
├── logs/                # 로그 파일
├── tests/               # 테스트
├── main.py             # 메인 실행
└── requirements.txt    # 의존성
```

## 🛠️ 설치 방법

### 1. Chrome 및 ChromeDriver 설치
```bash
# Windows
winget install Google.Chrome
# ChromeDriver는 자동 설치됨 (selenium 4.x)

# macOS
brew install --cask google-chrome
```

### 2. Python 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 설정 파일 생성
```bash
cp config/credentials.example.json config/credentials.json
# 파일 편집하여 로그인 정보 입력
```

## 💻 사용 방법

### 기본 사용법
```bash
# 가격 수정
python main.py --task price_update --csv price_list.csv

# 상품 등록
python main.py --task product_upload --csv new_products.csv

# 재고 업데이트
python main.py --task inventory_update --csv inventory.csv
```

### 고급 옵션
```bash
# 헤드리스 모드 (백그라운드 실행)
python main.py --task price_update --csv price.csv --headless

# 디버그 모드
python main.py --task price_update --csv price.csv --debug

# 스크린샷 저장
python main.py --task price_update --csv price.csv --screenshot
```

## 📊 CSV 파일 형식

### 가격 수정 CSV
```csv
상품코드,판매가
P00000IB,13500
P00000IC,25000
```

### 상품 등록 CSV
```csv
상품명,판매가,공급가,재고,카테고리
신상품A,30000,20000,100,의류
신상품B,25000,15000,50,액세서리
```

## ⚙️ 설정 파일

### config/settings.json
```json
{
  "browser": {
    "headless": false,
    "window_size": [1920, 1080],
    "implicit_wait": 10,
    "page_load_timeout": 30
  },
  "cafe24": {
    "admin_url": "https://manwonyori.cafe24.com/admin",
    "max_retries": 3,
    "retry_delay": 5
  },
  "paths": {
    "csv_folder": "./data/csv",
    "screenshot_folder": "./data/screenshots",
    "log_folder": "./logs"
  }
}
```

## 🔒 보안 주의사항

1. **credentials.json은 절대 커밋하지 마세요**
2. 환경변수 사용 권장
3. 2차 인증 사용 시 수동 입력 필요

## 🐛 문제 해결

### 로그인 실패
- 아이디/비밀번호 확인
- 2차 인증 여부 확인
- IP 차단 여부 확인

### 요소를 찾을 수 없음
- 페이지 로딩 대기 시간 증가
- 선택자 업데이트 필요
- Cafe24 UI 변경 확인

### 속도가 너무 느림
- 헤드리스 모드 사용
- 불필요한 이미지 로딩 차단
- 병렬 처리 고려

## 📈 성능 팁

1. **적절한 대기 시간**: 너무 빠르면 차단될 수 있음
2. **배치 처리**: 한 번에 너무 많은 작업 X
3. **로그 확인**: 정기적으로 로그 확인
4. **백업**: 작업 전 데이터 백업

## 🚀 로드맵

- [ ] 병렬 처리 지원
- [ ] GUI 인터페이스
- [ ] 스케줄러 통합
- [ ] API 방식과 통합

## 📝 라이선스

MIT License