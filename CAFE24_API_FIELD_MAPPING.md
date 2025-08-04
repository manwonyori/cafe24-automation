# Cafe24 API 필드 매핑 가이드

## 개요
이 문서는 Cafe24 API의 정확한 필드명과 각 필드의 형식, 필수 여부를 설명합니다.

## 1. 상품 등록 (POST /api/v2/admin/products)

### 필수 필드
| API 필드명 | 한글명 | 형식 | 설명 |
|------------|--------|------|------|
| product_name | 상품명 | 문자열 | [카테고리] 형식 권장 |
| price | 판매가 | 숫자(문자열) | "10000" 형식으로 전송 |
| display | 진열상태 | T/F | T: 진열, F: 미진열 |
| selling | 판매상태 | T/F | T: 판매중, F: 판매안함 |

### 선택 필드 (자주 사용)
| API 필드명 | 한글명 | 형식 | 설명 |
|------------|--------|------|------|
| product_code | 상품코드 | 문자열 | 중복 불가 |
| custom_product_code | 자체상품코드 | 문자열 | 내부 관리용 |
| model_name | 모델명 | 문자열 | |
| supply_price | 공급가 | 숫자(문자열) | |
| retail_price | 소비자가 | 숫자(문자열) | |
| summary_description | 상품요약설명 | 문자열 | |
| quantity | 재고수량 | 숫자 | 0 이상의 정수 |
| weight | 상품중량 | 문자열 | 그램(g) 단위 |
| brand_code | 브랜드코드 | 문자열 | 예: B000000A |
| manufacturer_code | 제조사코드 | 문자열 | 예: M000000A |
| supplier_code | 공급사코드 | 문자열 | 예: S000000A |
| made_in_code | 원산지코드 | 문자열 | KR, CN, US 등 |
| tax_type | 세금타입 | 문자열 | A:과세, B:면세, C:영세 |
| use_naverpay | 네이버페이 사용 | T/F | |
| product_tag | 상품태그 | 문자열 | 쉼표로 구분 |
| shipping_fee_by_product | 개별배송비 | T/F | |
| shipping_fee_type | 배송비타입 | 문자열 | T:무료, R:고정배송비 |

## 2. 상품 수정 (PUT /api/v2/admin/products/{product_no})

### 필수 필드
| API 필드명 | 한글명 | 형식 | 설명 |
|------------|--------|------|------|
| product_no | 상품번호 | 숫자 | URL 파라미터로 전송 |

### 수정 가능 필드
- product_name
- price
- display
- selling
- quantity
- supply_price
- summary_description
- product_tag

## 3. 재고 수정 (PUT /api/v2/admin/products/{product_no}/variants/quantity)

### 필수 필드
| API 필드명 | 한글명 | 형식 | 설명 |
|------------|--------|------|------|
| product_no | 상품번호 | 숫자 | URL 파라미터 |
| quantity | 재고수량 | 숫자 | 변경할 수량 |

### 선택 필드
| API 필드명 | 한글명 | 형식 | 설명 |
|------------|--------|------|------|
| variant_code | 품목코드 | 문자열 | 옵션상품인 경우 |
| safety_quantity | 안전재고 | 숫자 | |
| use_inventory | 재고관리 사용 | T/F | |

## 4. 가격 수정 (PUT /api/v2/admin/products/{product_no})

### 필수 필드
| API 필드명 | 한글명 | 형식 | 설명 |
|------------|--------|------|------|
| product_no | 상품번호 | 숫자 | URL 파라미터 |
| price | 판매가 | 숫자(문자열) | "12000" 형식 |

### 선택 필드
| API 필드명 | 한글명 | 형식 | 설명 |
|------------|--------|------|------|
| retail_price | 소비자가 | 숫자(문자열) | |
| supply_price | 공급가 | 숫자(문자열) | |
| price_content | 가격설명 | 문자열 | |
| price_update_date | 가격수정일 | 날짜 | YYYY-MM-DD |

## 중요 사항

1. **데이터 형식**
   - 가격 관련 필드는 문자열로 전송 (예: "10000")
   - 재고는 숫자로 전송
   - 날짜는 YYYY-MM-DD 형식

2. **코드 형식**
   - 브랜드코드: B + 7자리 숫자 (예: B000000A)
   - 제조사코드: M + 7자리 숫자 (예: M000000A)
   - 공급사코드: S + 7자리 숫자 (예: S000000A)

3. **API 버전**
   - X-Cafe24-Api-Version: 2025-06-01

4. **엑셀 템플릿**
   - 기본 템플릿: 한글 필드명 사용 (사용자 친화적)
   - API 형식 템플릿: 영문 API 필드명 사용 (직접 연동용)