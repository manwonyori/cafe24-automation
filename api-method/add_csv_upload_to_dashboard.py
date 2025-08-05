#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
대시보드에 CSV 업로드 기능 추가
"""

# 1. app.py에 추가할 엔드포인트
app_endpoint = '''
@app.route('/api/upload-price-csv', methods=['POST'])
@handle_errors
def upload_price_csv():
    """CSV 파일로 가격 일괄 수정"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'CSV 파일을 선택해주세요'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'CSV 파일을 선택해주세요'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'CSV 파일만 업로드 가능합니다'}), 400
        
        # CSV 파일 읽기
        df = pd.read_csv(file, encoding='utf-8-sig')
        
        # 필수 컬럼 확인
        required_columns = ['상품코드', '판매가']
        if not all(col in df.columns for col in required_columns):
            return jsonify({
                'success': False, 
                'error': f'필수 컬럼이 없습니다. 필요: {required_columns}'
            }), 400
        
        success_count = 0
        failed_count = 0
        errors = []
        
        headers = get_headers()
        mall_id = get_mall_id()
        
        # 각 행 처리
        for idx, row in df.iterrows():
            try:
                product_no = str(row['상품코드'])
                new_price = str(int(float(row['판매가'])))
                
                # 상품번호로 조회 (product_code가 아닌 product_no 찾기)
                search_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products"
                params = {'product_code': product_no, 'limit': 1}
                response = requests.get(search_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    products = response.json().get('products', [])
                    if products:
                        actual_product_no = products[0].get('product_no')
                        
                        # 가격 수정
                        update_url = f"https://{mall_id}.cafe24api.com/api/v2/admin/products/{actual_product_no}"
                        update_data = {
                            "request": {
                                "product": {
                                    "price": new_price
                                }
                            }
                        }
                        
                        response = requests.put(update_url, headers=headers, json=update_data)
                        if response.status_code == 200:
                            success_count += 1
                        else:
                            failed_count += 1
                            errors.append(f"상품 {product_no}: {response.status_code}")
                    else:
                        failed_count += 1
                        errors.append(f"상품 {product_no}: 찾을 수 없음")
                else:
                    failed_count += 1
                    errors.append(f"상품 {product_no}: 조회 실패")
                    
            except Exception as e:
                failed_count += 1
                errors.append(f"행 {idx+1}: {str(e)}")
        
        return jsonify({
            'success': True,
            'success_count': success_count,
            'failed_count': failed_count,
            'errors': errors[:10]  # 처음 10개 에러만
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
'''

# 2. margin_dashboard.html에 추가할 UI 코드
html_code = '''
<!-- CSV 업로드 섹션 추가 (가격수정 엑셀 생성 버튼 다음에) -->
<button class="btn btn-info" onclick="showCSVUploadModal()">
    📤 CSV 업로드로 가격 수정
</button>

<!-- CSV 업로드 모달 추가 -->
<div class="modal" id="csvUploadModal">
    <div class="modal-content">
        <div class="modal-header">
            <h3>CSV 파일로 가격 일괄 수정</h3>
            <button class="modal-close" onclick="closeCSVUploadModal()">×</button>
        </div>
        <div class="modal-body">
            <div class="upload-info">
                <h4>📋 CSV 파일 형식</h4>
                <p>다음 컬럼이 필수입니다:</p>
                <ul>
                    <li><strong>상품코드</strong>: 제품의 상품코드 (예: P0000XXX)</li>
                    <li><strong>판매가</strong>: 새로운 판매 가격</li>
                </ul>
                
                <h4>💡 사용 방법</h4>
                <ol>
                    <li>'가격수정 엑셀 생성'으로 템플릿 다운로드</li>
                    <li>엑셀에서 가격 수정</li>
                    <li>CSV 형식으로 저장</li>
                    <li>아래에서 파일 선택 후 업로드</li>
                </ol>
            </div>
            
            <div class="file-upload-area">
                <input type="file" id="csvFile" accept=".csv" onchange="handleFileSelect(event)">
                <div id="fileInfo" style="margin-top: 10px;"></div>
            </div>
            
            <div class="upload-buttons">
                <button class="btn btn-primary" onclick="uploadCSV()">
                    업로드 및 가격 수정
                </button>
                <button class="btn btn-secondary" onclick="closeCSVUploadModal()">
                    취소
                </button>
            </div>
            
            <div id="uploadResult" style="margin-top: 20px; display: none;">
                <!-- 업로드 결과 표시 -->
            </div>
        </div>
    </div>
</div>

<script>
// CSV 업로드 모달 표시
function showCSVUploadModal() {
    document.getElementById('csvUploadModal').classList.add('active');
}

// CSV 업로드 모달 닫기
function closeCSVUploadModal() {
    document.getElementById('csvUploadModal').classList.remove('active');
    document.getElementById('csvFile').value = '';
    document.getElementById('fileInfo').innerHTML = '';
    document.getElementById('uploadResult').style.display = 'none';
}

// 파일 선택 처리
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        document.getElementById('fileInfo').innerHTML = 
            `선택된 파일: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
    }
}

// CSV 업로드
async function uploadCSV() {
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('CSV 파일을 선택해주세요.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const button = event.target;
        button.disabled = true;
        button.innerHTML = '⏳ 업로드 중...';
        
        const response = await fetch('/api/upload-price-csv', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            const resultDiv = document.getElementById('uploadResult');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h4>✅ 업로드 완료!</h4>
                    <p>성공: ${data.success_count}개</p>
                    <p>실패: ${data.failed_count}개</p>
                    ${data.errors && data.errors.length > 0 ? 
                        '<h5>오류 내역:</h5><ul>' + 
                        data.errors.map(err => `<li>${err}</li>`).join('') + 
                        '</ul>' : ''}
                </div>
            `;
            
            // 3초 후 모달 닫고 데이터 새로고침
            setTimeout(() => {
                closeCSVUploadModal();
                loadMarginAnalysis(); // 데이터 새로고침
            }, 3000);
        } else {
            alert('업로드 실패: ' + data.error);
        }
    } catch (error) {
        alert('업로드 중 오류가 발생했습니다.');
        console.error(error);
    } finally {
        event.target.disabled = false;
        event.target.innerHTML = '업로드 및 가격 수정';
    }
}
</script>

<style>
/* CSV 업로드 모달 스타일 */
.upload-info {
    background: #f5f5f5;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.upload-info h4 {
    margin-top: 0;
    color: #333;
}

.upload-info ul, .upload-info ol {
    margin: 10px 0;
    padding-left: 20px;
}

.file-upload-area {
    border: 2px dashed #ccc;
    padding: 30px;
    text-align: center;
    border-radius: 8px;
    margin: 20px 0;
}

.file-upload-area input[type="file"] {
    display: block;
    margin: 0 auto;
}

.upload-buttons {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-top: 20px;
}

.alert {
    padding: 15px;
    border-radius: 5px;
    margin-top: 10px;
}

.alert-success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}
</style>
'''

print("=== 대시보드 CSV 업로드 기능 추가 가이드 ===\n")

print("1. app.py에 엔드포인트 추가:")
print("-" * 50)
print(app_endpoint)
print("\n")

print("2. margin_dashboard.html에 UI 추가:")
print("-" * 50)
print("   - 가격수정 엑셀 생성 버튼 옆에 '📤 CSV 업로드로 가격 수정' 버튼 추가")
print("   - 모달 창과 JavaScript 코드 추가")
print("\n")

print("3. 필요한 import 추가 (app.py 상단에):")
print("-" * 50)
print("import pandas as pd")
print("\n")

print("=== 사용 방법 ===")
print("1. 웹 대시보드에서 '가격수정 엑셀 생성' 클릭하여 템플릿 다운로드")
print("2. 엑셀에서 가격 수정 (상품코드와 판매가 컬럼 필수)")
print("3. CSV 형식으로 저장")
print("4. '📤 CSV 업로드로 가격 수정' 버튼 클릭")
print("5. CSV 파일 선택 후 업로드")
print("\n")

print("=== 예시 CSV 형식 ===")
print("상품코드,판매가")
print("P00000IB,13500")
print("P00000IC,25000")

# 샘플 CSV 파일 생성
sample_csv = """상품코드,판매가
P00000IB,13500
"""

with open('price_update_sample.csv', 'w', encoding='utf-8-sig') as f:
    f.write(sample_csv)

print("\n✅ 샘플 CSV 파일 생성됨: price_update_sample.csv")