# 카페24 쇼핑몰 완전 자동화 시스템

## 🌟 소개

카페24 쇼핑몰 완전 자동화 시스템은 한국어 자연어 명령으로 쇼핑몰을 관리할 수 있는 혁신적인 솔루션입니다.

## 🚀 주요 특징

- **한국어 자연어 처리**: "오늘 주문 보여줘" 같은 자연스러운 명령 인식
- **완전 자동화**: 상품 관리, 주문 처리, 재고 관리 모두 자동화
- **실시간 모니터링**: 매출, 재고, 고객 데이터 실시간 추적
- **높은 성능**: 고성능 캐싱으로 빠른 응답 속도

## 📋 기능 목록

### 상품 관리
- 대량 상품 등록/수정
- 가격 일괄 조정
- SEO 자동 최적화
- 재고 실시간 추적

### 주문 관리
- 주문 상태 자동 추적
- 배송 정보 관리
- 반품/교환 처리
- 매출 통계 분석

### 고객 관리
- 고객 정보 조회
- 구매 패턴 분석
- VIP 고객 관리
- 맞춤 마케팅

## 🛠️ 설치 방법

### 원클릭 배포

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yourusername/cafe24)

### 로컬 설치

```bash
git clone https://github.com/yourusername/cafe24.git
cd cafe24
docker-compose up -d
```

## 📚 문서

- [API 문서](API.md)
- [배포 가이드](DEPLOYMENT.md)
- [마이그레이션 가이드](../MIGRATE_FROM_OLD.md)

## 💻 코드 예제

### Python SDK

```python
from src.cafe24_system import Cafe24System

system = Cafe24System()

# 자연어 명령
result = system.execute("오늘 신규 주문 보여줘")

# 직접 API 호출
products = system.get_products(display='T')
orders = system.get_orders(start_date='2024-01-01')
```

### REST API

```bash
# 자연어 명령 실행
curl -X POST http://localhost:5000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "재고 부족 상품 확인"}'

# 상품 목록 조회
curl http://localhost:5000/api/products?limit=10
```

## 🤝 기여 방법

프로젝트에 기여하고 싶으신가요? 

1. 저장소를 Fork하세요
2. 기능 브랜치를 생성하세요
3. 변경사항을 커밋하세요
4. Pull Request를 보내주세요

## 📝 라이선스

이 프로젝트는 MIT 라이선스로 배포됩니다.

## 📞 지원

- GitHub Issues: [문제 보고](https://github.com/yourusername/cafe24/issues)
- Email: support@example.com