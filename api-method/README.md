# API 자동화 방식

> ⚡ Cafe24 Open API를 활용한 빠른 자동화 시스템

## 📋 개요

Cafe24에서 제공하는 Open API를 통해 상품, 주문, 고객 정보를 관리하는 시스템입니다. 빠른 속도와 효율성이 장점이지만, 일부 기능(특히 가격 수정)에 제한이 있습니다.

## ⚠️ 중요 알림: API 한계점

### 🔴 가격 수정 API 문제
- **증상**: API가 200 OK를 반환하지만 실제로 가격이 변경되지 않음
- **원인**: Cafe24 API의 알려진 버그 또는 제한사항
- **해결**: 가격 수정이 필요한 경우 Selenium 방식 사용

### 🟡 기타 제한사항
- CSV 파일 업로드 불가
- 일부 상세 설정 변경 불가
- API 호출 제한 (분당 300회)

## ✅ 잘 작동하는 기능

### 📊 상품 관리
- 상품 목록 조회 ✅
- 상품 상세 정보 조회 ✅
- 재고 수정 ✅
- 상품 등록 (제한적) ⚠️

### 📦 주문 관리
- 주문 목록 조회 ✅
- 주문 상태 변경 ✅
- 배송 정보 업데이트 ✅

### 👥 고객 관리
- 고객 목록 조회 ✅
- 고객 정보 수정 ✅
- 포인트/적립금 관리 ✅

### 📈 통계 및 분석
- 매출 통계 ✅
- 베스트셀러 분석 ✅
- 재고 현황 리포트 ✅

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. API 키 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
CAFE24_MALL_ID=your_mall_id
CAFE24_CLIENT_ID=your_client_id
CAFE24_CLIENT_SECRET=your_client_secret
CAFE24_ACCESS_TOKEN=your_access_token
```

### 3. 서버 실행
```bash
python app.py
```

웹 대시보드: http://localhost:5000

## 💻 사용 방법

### 웹 대시보드
1. http://localhost:5000 접속
2. 메뉴에서 원하는 기능 선택
3. 필터 및 옵션 설정
4. 실행

### API 직접 호출
```python
import requests

# 상품 목록 조회
response = requests.get('http://localhost:5000/api/products')
products = response.json()

# 재고 수정 (작동함!)
response = requests.put('http://localhost:5000/api/products/123/inventory', 
    json={'quantity': 100})

# 가격 수정 (작동 안함!)
# 이 기능은 Selenium 방식을 사용하세요
```

## 📂 프로젝트 구조

```
api-method/
├── app.py              # Flask 메인 앱
├── config.py           # 설정 관리
├── requirements.txt    # 의존성
├── templates/          # 웹 UI 템플릿
│   ├── dashboard.html
│   ├── margin_dashboard.html
│   └── vendor_dashboard.html
├── static/            # 정적 파일
├── src/               # 핵심 모듈
│   ├── api_client.py  # API 통신
│   ├── nlp_processor.py # 자연어 처리
│   └── cache_manager.py # 캐싱
└── logs/             # 로그 파일
```

## 🌟 주요 기능

### 1. 마진율 대시보드
- 실시간 마진율 계산
- 수익성 분석
- 가격 최적화 제안

### 2. 재고 관리
- 재고 부족 알림
- 자동 발주 제안
- 재고 회전율 분석

### 3. 자연어 명령
```
"오늘 주문 보여줘"
"재고 10개 이하 상품"
"이번달 매출 통계"
```

## 📊 API 엔드포인트

| 엔드포인트 | 메소드 | 설명 | 상태 |
|-----------|--------|------|------|
| `/api/products` | GET | 상품 목록 | ✅ |
| `/api/products/{id}` | GET | 상품 상세 | ✅ |
| `/api/products/{id}/price` | PUT | 가격 수정 | ❌ |
| `/api/products/{id}/inventory` | PUT | 재고 수정 | ✅ |
| `/api/orders` | GET | 주문 목록 | ✅ |
| `/api/orders/{id}/status` | PUT | 주문 상태 변경 | ✅ |

## 🔧 고급 설정

### 캐싱 설정
```python
# config.py
CACHE_ENABLED = True
CACHE_DURATION = 300  # 5분
```

### API 호출 제한
```python
# config.py
API_RATE_LIMIT = 300  # 분당 호출 수
API_RETRY_COUNT = 3
API_RETRY_DELAY = 1
```

## 🐛 문제 해결

### 토큰 만료
```bash
python refresh_token.py
```

### 429 에러 (Too Many Requests)
- API_RATE_LIMIT 값 줄이기
- 캐싱 활성화

### 가격 수정 안됨
- **해결책**: Selenium 방식 사용 (`../selenium-method/`)

## 📈 성능 최적화

1. **캐싱 활용**: 반복 조회 최소화
2. **배치 처리**: 여러 요청을 하나로
3. **비동기 처리**: 동시 다중 요청
4. **필드 선택**: 필요한 필드만 요청

## 🚀 배포

### Render.com
```bash
# render.yaml 파일 있음
git push origin main
```

### Docker
```bash
docker-compose up -d
```

## 📝 라이선스

MIT License

## 🆘 지원

- API 문제: Cafe24 개발자센터
- 시스템 문제: GitHub Issues