# Cafe24 CSV 템플릿 API 호환성 분석

## manwonyori_20250805_201_f879_producr_template.csv 기준

### ✅ API로 가능한 작업

#### 1. **다운로드 (Export)**
```
GET /api/csv/export
- 현재 상품을 Cafe24 CSV 형식으로 다운로드
- 모든 필드 구조 유지
- 진열상태 T/F → Y/N 자동 변환
```

#### 2. **업로드 (Import)**
```
POST /api/csv/import
- Cafe24 CSV 파일 업로드
- 신규 등록 & 기존 수정 자동 판별
- 상품코드 있음 → 수정
- 상품코드 없음 → 신규 등록
```

### ❌ API로 불가능한 필드 (CSV 전용)

| 필드 | 이유 | 대안 |
|------|------|------|
| 상품분류 번호 | 별도 카테고리 API 필요 | 상품 등록 후 카테고리 API |
| 재고수량 | 재고 API 별도 | POST /api/v2/admin/products/{product_no}/inventories |
| 이미지등록 | 이미지 업로드 API 별도 | POST /api/v2/admin/products/{product_no}/images |
| 옵션 관련 | 옵션 API 별도 | POST /api/v2/admin/products/{product_no}/options |
| 상품 상세설명 | HTML 에디터 필요 | 별도 처리 |
| SEO 설정 | SEO API 별도 | PUT /api/v2/admin/products/{product_no}/seo |

### 📋 필드 매핑 규칙

| CSV 필드 | API 필드 | 변환 규칙 |
|----------|----------|-----------|
| 진열상태 | display | Y → T, N → F |
| 판매상태 | selling | Y → T, N → F |
| 과세구분 | tax_type | "A\|10" → "A" |
| 판매가 | price | 숫자 → 문자열 |
| 공급가 | supply_price | 숫자 → 문자열 |
| 상품분류 번호 | - | 99\|109 형식 (API 미지원) |

### 🔄 업로드/다운로드 프로세스

#### **다운로드 시나리오**
1. API로 전체 상품 조회
2. Cafe24 CSV 템플릿 구조로 변환
3. 누락 필드는 빈 값 처리
4. UTF-8 BOM 인코딩으로 저장

#### **업로드 시나리오**
1. CSV 파일 업로드
2. 각 행별 처리:
   - 상품코드 확인
   - 필드 매핑 & 변환
   - API 호출 (POST/PUT)
3. 결과 리포트:
   - 신규 등록 수
   - 수정 성공 수
   - 실패 및 오류

### 🚨 주의사항

1. **상품코드 규칙**
   - P로 시작 = 기존 상품
   - 비어있음 = 신규 등록

2. **필수 필드**
   - 신규: 상품명, 판매가, 진열상태, 판매상태
   - 수정: 상품코드 필수

3. **제한사항**
   - 한 번에 100개 제한 권장
   - 이미지는 URL만 가능
   - 재고는 별도 업데이트

### 📊 구현 현황

```python
# 구현 완료
- CSV Export (다운로드) ✅
- CSV Import (업로드) ✅
- 템플릿 다운로드 ✅
- 필드 자동 매핑 ✅
- 값 변환 규칙 ✅

# 추가 필요
- 관련상품 CSV 처리
- 옵션 CSV 처리
- 에러 상세 리포트
- 진행률 표시
```

**결론**: Cafe24 CSV 템플릿의 핵심 필드들은 API로 처리 가능하며, 
업로드/다운로드 기능 구현 가능. 단, 일부 고급 기능은 별도 API 필요.