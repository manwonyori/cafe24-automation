# Cafe24 Automation System 🚀

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-enabled-brightgreen.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🎯 Cafe24 쇼핑몰 운영을 위한 완전 자동화 시스템 - API와 Selenium 두 가지 방식 제공

## 📋 프로젝트 개요

이 프로젝트는 Cafe24 쇼핑몰의 상품 관리, 가격 수정, 재고 관리 등을 자동화하는 통합 시스템입니다. **API 방식**과 **Selenium 방식** 두 가지 방법을 제공하여 상황에 맞게 선택할 수 있습니다.

## 🏗️ 프로젝트 구조

```
cafe24-automation/
├── api-method/          # API 기반 자동화 (빠르지만 제한적)
├── selenium-method/     # 브라우저 자동화 (느리지만 완전함)
├── docs/               # 통합 문서
│   ├── comparison/     # 두 방식 비교 분석
│   └── guides/         # 사용 가이드
└── README.md          # 현재 문서
```

## 🔄 두 가지 자동화 방식

### 1️⃣ API 방식 (`api-method/`)

#### ✅ 장점
- ⚡ **빠른 속도**: 직접 API 호출로 빠른 응답
- 💻 **서버 리소스 절약**: 브라우저 불필요
- 🔄 **대량 처리 우수**: 동시 다중 요청 가능
- 🌐 **웹 대시보드 제공**: 사용하기 편한 UI

#### ❌ 단점
- 🚫 **가격 수정 제한**: API 버그로 실제 적용 안됨
- 🔑 **토큰 관리 필요**: 주기적 갱신 필요
- 📊 **일부 기능 제한**: CSV 업로드 불가

#### 💡 적합한 경우
- 상품 목록 조회
- 재고 확인 및 모니터링
- 주문 내역 관리
- 매출 통계 분석

### 2️⃣ Selenium 방식 (`selenium-method/`)

#### ✅ 장점
- ✨ **모든 기능 사용 가능**: 관리자가 할 수 있는 모든 작업
- 💰 **가격 수정 완벽 지원**: API 제한 우회
- 📁 **CSV 업로드 가능**: 대량 상품 수정
- 🔧 **복잡한 설정 가능**: UI 기반 모든 설정

#### ❌ 단점
- 🐌 **상대적으로 느림**: 페이지 로딩 대기
- 🖥️ **브라우저 리소스 필요**: Chrome 필요
- 📝 **순차 처리**: 동시 작업 제한

#### 💡 적합한 경우
- **가격 수정** (특히 중요!)
- CSV 파일 업로드
- 상품 일괄 등록/수정
- 복잡한 설정 변경

## 🚀 빠른 시작

### API 방식 사용
```bash
cd api-method
pip install -r requirements.txt
python app.py
```
- 웹 대시보드: http://localhost:5000
- API 문서: http://localhost:5000/docs

### Selenium 방식 사용
```bash
cd selenium-method
pip install -r requirements.txt
python main.py --task price_update --csv ../data/price_update.csv
```

## 📊 성능 비교

| 기능 | API 방식 | Selenium 방식 | 권장 사항 |
|------|----------|---------------|-----------|
| **상품 조회** | ✅ 0.5초 | ⚠️ 3초 | API 사용 |
| **가격 수정** | ❌ 작동 안함 | ✅ 완벽 지원 | **Selenium 사용** |
| **재고 수정** | ✅ 지원 | ✅ 지원 | API 사용 |
| **CSV 업로드** | ❌ 불가 | ✅ 가능 | Selenium 사용 |
| **대량 처리** | ✅ 우수 | ⚠️ 순차 처리 | 용도별 선택 |
| **자동화 안정성** | ⚠️ 토큰 관리 | ✅ 안정적 | Selenium 사용 |

## 🎯 사용 시나리오

### 📌 시나리오 1: 매일 가격 업데이트
```bash
# 🚫 API 방식은 가격 수정이 제대로 안됨!
# ✅ Selenium 방식 사용 (확실함)
cd selenium-method
python price_updater.py --csv daily_prices.csv
```

### 📌 시나리오 2: 실시간 재고 모니터링
```bash
# ✅ API 방식 추천 (빠른 속도)
cd api-method
python inventory_monitor.py --interval 60
```

### 📌 시나리오 3: 대량 상품 등록
```bash
# ✅ Selenium 방식 사용 (CSV 업로드)
cd selenium-method
python bulk_upload.py --csv new_products.csv
```

## ⚠️ 중요 참고사항

### 🔴 API 방식의 한계
1. **가격 수정 API 버그**: 200 OK 응답하지만 실제로 변경 안됨
2. **옵션 상품 제한**: 변형 상품 가격 수정 복잡
3. **CSV 업로드 불가**: 파일 업로드 API 없음

### 🟢 Selenium 방식 권장 상황
1. **가격 수정이 필요한 모든 경우**
2. CSV 파일로 대량 작업
3. API로 불가능한 작업
4. 100% 확실한 결과가 필요할 때

## 📈 로드맵

### ✅ Phase 1 (완료)
- API 기반 시스템 구축
- 웹 대시보드 개발
- 기본 CRUD 기능

### 🚧 Phase 2 (진행중)
- Selenium 자동화 추가
- 가격 수정 문제 해결
- CSV 업로드 자동화

### 📅 Phase 3 (계획)
- 두 방식 통합 인터페이스
- 자동 방식 선택 (작업별 최적화)
- AI 기반 가격 최적화

## 🔧 설정

### 공통 설정
```json
{
  "cafe24": {
    "mall_id": "manwonyori",
    "admin_url": "https://manwonyori.cafe24.com/admin"
  }
}
```

### API 방식 설정
```bash
# api-method/.env
CAFE24_CLIENT_ID=your_client_id
CAFE24_CLIENT_SECRET=your_client_secret
CAFE24_ACCESS_TOKEN=your_token
```

### Selenium 방식 설정
```json
// selenium-method/config.json
{
  "login": {
    "id": "your_admin_id",
    "password": "your_password"
  },
  "browser": {
    "headless": false,
    "wait_time": 3
  }
}
```

## 🆘 문제 해결

### API 방식 문제
- **가격 수정 안됨**: Selenium 방식 사용하세요!
- **토큰 만료**: `python refresh_token.py`
- **429 에러**: 요청 속도 줄이기

### Selenium 방식 문제
- **로그인 실패**: 2차 인증 확인
- **요소 못찾음**: 페이지 로딩 대기 시간 증가
- **Chrome 에러**: ChromeDriver 버전 확인

## 📚 상세 문서

- [API vs Selenium 상세 비교](docs/comparison/api_vs_selenium.md)
- [API 방식 가이드](api-method/README.md)
- [Selenium 방식 가이드](selenium-method/README.md)
- [마이그레이션 가이드](docs/guides/migration.md)

## 🤝 기여 방법

1. Fork 저장소
2. Feature 브랜치 생성
3. 변경사항 커밋
4. Pull Request 생성

## 📝 라이선스

MIT License - 자유롭게 사용하세요!

## 📞 지원

- GitHub Issues: [문제 신고](https://github.com/manwonyori/cafe24-automation/issues)
- Email: support@manwonyori.com

---

**⚡ Pro Tip**: 가격 수정은 무조건 Selenium 방식을 사용하세요! API는 버그가 있습니다.