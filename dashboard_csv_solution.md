# 대시보드 CSV 업로드 가격 수정 방법

## 현재 상황
- Render 웹 서비스: https://cafe24-automation.onrender.com
- 현재 CSV 업로드 기능이 구현되어 있지 않음
- API 직접 수정도 작동하지 않음

## 즉시 사용 가능한 방법

### 1. 웹 대시보드에서 CSV 다운로드 → Cafe24 업로드
1. **마진율 대시보드 접속**
   - https://cafe24-automation.onrender.com/margin-dashboard

2. **CSV/엑셀 파일 생성**
   - "📋 가격수정 엑셀 생성" 버튼 클릭
   - 엑셀 파일 다운로드

3. **가격 수정**
   - 다운로드된 파일 열기
   - [인생]점보떡볶이1490g 찾기 (상품코드: P00000IB)
   - 판매가를 13500으로 수정

4. **Cafe24 관리자에서 업로드**
   - https://manwonyori.cafe24.com/admin 접속
   - 상품관리 > 상품일괄등록/수정
   - '상품일괄수정' 탭 선택
   - 수정한 CSV 파일 업로드

### 2. 이미 생성된 CSV 사용
파일: `price_update_209_20250805_153818.csv`

## CSV 업로드 기능 추가하기 (개발자용)

### 필요한 수정사항:

1. **app.py에 엔드포인트 추가**
```python
@app.route('/api/upload-price-csv', methods=['POST'])
def upload_price_csv():
    # CSV 파일 받아서 가격 수정
```

2. **margin_dashboard.html에 업로드 UI 추가**
- 파일 선택 버튼
- 업로드 진행 상태 표시
- 결과 표시

### 하지만 현재는:
- GitHub에 코드 추가 필요
- Render에 재배포 필요
- 시간이 걸림

## 🎯 권장 방법

**지금 당장은:**
1. 웹 대시보드에서 CSV 다운로드
2. 엑셀에서 가격 수정
3. Cafe24 관리자에서 업로드

이 방법이 가장 빠르고 확실합니다!

## CSV 파일 형식
```
상품코드,판매가
P00000IB,13500
```

주의: 상품코드는 반드시 정확해야 합니다.