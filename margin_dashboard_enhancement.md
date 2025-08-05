# 마진 대시보드 가격 수정 기능 개선

## 현재 구현된 기능 ✅
1. **마진율 구간별 상품 분석**
2. **다중 상품 선택**
3. **목표 마진율 입력 → 일괄 가격 수정**
4. **API를 통한 실시간 가격 변경**

## 추가 구현 가능한 기능 🔄

### 1. **단일 상품 마진율 수정**
```javascript
// 각 상품 행에 개별 마진율 입력 필드 추가
<input type="number" 
       class="single-margin-input" 
       placeholder="목표%" 
       onchange="updateSingleProductMargin(${product.product_no}, this.value)">
```

### 2. **CSV Export 기능 (Cafe24 템플릿 형식)**
```javascript
// 마진율 수정된 상품들을 CSV로 다운로드
async function exportMarginUpdatedProducts() {
    const response = await fetch('/api/margin/export-updated', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            product_nos: Array.from(selectedProducts),
            target_margin: targetMargin,
            update_type: updateType
        })
    });
    
    // 파일 다운로드
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `margin_update_${targetMargin}pct_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
}
```

### 3. **변경 사항 미리보기**
```javascript
// 가격 변경 전 미리보기
async function previewMarginChanges() {
    const response = await fetch('/api/margin/preview-changes', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            product_nos: Array.from(selectedProducts),
            target_margin: targetMargin,
            update_type: updateType
        })
    });
    
    const data = await response.json();
    showPreviewModal(data.preview);
}
```

## 구현 플로우

### 📊 일괄 수정 프로세스
```
1. 마진율 구간 선택 (예: 10-20%)
   ↓
2. 해당 구간 상품 표시
   ↓
3. 수정할 상품 선택 (체크박스)
   ↓
4. 목표 마진율 입력 (예: 25%)
   ↓
5. [미리보기] → 변경될 가격 확인
   ↓
6. [적용] → API로 가격 수정
   ↓
7. [CSV 다운로드] → 수정된 내용 저장
```

### 🎯 단일 수정 프로세스
```
1. 상품 목록에서 개별 마진율 입력
   ↓
2. Enter 또는 포커스 아웃
   ↓
3. 즉시 API 호출하여 수정
   ↓
4. 성공/실패 표시
```

## CSV Export 형식 유지

```csv
상품코드,자체 상품코드,진열상태,판매상태,...,공급가,판매가,...
P00000JT,,Y,Y,...,4940.00,6300.00,...
```

- **manwonyori_20250805_201_f879_producr_template.csv** 형식 완벽 호환
- 수정된 가격만 업데이트, 나머지 필드는 그대로 유지
- 진열상태 T/F → Y/N 자동 변환

## 추가 기능 아이디어

### 1. **가격 시뮬레이터**
- 마진율 변경 시 예상 수익 계산
- 재고 × 새 마진 = 예상 이익

### 2. **변경 이력 관리**
- 가격 변경 히스토리 저장
- 이전 가격으로 롤백 기능

### 3. **조건부 가격 설정**
- "공급가 10,000원 이상인 상품만"
- "재고 50개 이하인 상품 제외"

### 4. **스케줄 가격 변경**
- 특정 날짜/시간에 자동 적용
- 시즌 세일 자동화

## 기술적 검증 ✅

1. **API 지원**: PUT /api/v2/admin/products/{product_no}
2. **필드 수정 가능**: price, supply_price
3. **CSV 형식 호환**: 템플릿 구조 그대로 유지
4. **일괄 처리**: 최대 100개씩 처리 가능

**결론**: 모든 요구사항 구현 가능하며, Cafe24 CSV 템플릿 형식을 완벽히 지원하면서 마진율 기반 가격 수정이 가능합니다.