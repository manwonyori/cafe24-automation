# Cafe24 상품 API 기능 정리

## 현재 구현된 상품 수정 기능

### 1. 마진율 기준 가격 일괄 수정 (/api/margin/update-prices)
- **용도**: 목표 마진율에 맞춰 여러 상품의 가격을 일괄 수정
- **기능**:
  - 공급가 기준으로 판매가 자동 계산
  - 판매가 기준으로 공급가 역산
  - 100원 단위 반올림
- **제한**: 공급가가 설정된 상품만 가능

### 2. 상품 일괄 업데이트 (/api/products/bulk-update)
- **수정 가능한 필드**:
  - price (판매가)
  - quantity (재고수량)
  - display (진열상태: T/F)
  - selling (판매상태: T/F)
- **특징**: 여러 상품을 한 번에 수정 가능

### 3. 개별 상품 수정 (PUT /api/v2/admin/products/{product_no})
- **수정 가능한 모든 필드**:
  - product_name (상품명)
  - price (판매가)
  - supply_price (공급가)
  - retail_price (소비자가)
  - quantity (재고수량)
  - display (진열상태)
  - selling (판매상태)
  - product_code (상품코드)
  - custom_product_code (자체상품코드)
  - model_name (모델명)
  - summary_description (요약설명)
  - weight (중량)
  - brand_code (브랜드)
  - manufacturer_code (제조사)
  - supplier_code (공급사)
  - made_in_code (원산지)
  - tax_type (과세구분)
  - use_naverpay (네이버페이 사용)
  - product_tag (태그)
  - shipping_fee_type (배송비 타입)

## 수정할 수 없는 항목
- product_no (상품번호) - 시스템 자동 생성
- created_date (등록일)
- updated_date (수정일) - 자동 갱신

## 상품 등록 기능 (현재 미구현)
현재 시스템에는 새 상품을 등록하는 기능이 구현되어 있지 않습니다.
필요시 POST /api/v2/admin/products 엔드포인트를 추가해야 합니다.

## 마진 대시보드에서 사용 가능한 기능
1. **마진율 분석** - 전체 상품의 마진율 현황 파악
2. **구간별 상품 조회** - 특정 마진율 구간의 상품 필터링
3. **가격 일괄 수정** - 선택한 상품들의 가격을 목표 마진율에 맞춰 조정

## API 사용시 주의사항
1. 가격은 문자열로 전송해야 함 (예: "10000")
2. 진열/판매 상태는 "T" 또는 "F"로 전송
3. 한 번에 수정 가능한 상품 수는 100개 제한
4. 공급가가 없는 상품은 마진율 계산 불가

## 추가 개발이 필요한 기능
1. 새 상품 등록 (POST)
2. 상품 삭제 (DELETE)
3. 상품 옵션(변형) 수정
4. 상품 이미지 업로드/수정
5. 상품 상세설명 HTML 편집
6. 카테고리 일괄 변경
7. SEO 메타데이터 수정