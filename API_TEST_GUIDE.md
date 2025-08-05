# 카페24 API 종합 진단 가이드

카페24 프로젝트의 모든 API 연결과 데이터 흐름을 체계적으로 테스트하고 문제점을 진단하는 도구들입니다.

## 🔧 제공 스크립트

### 1. comprehensive_api_test.py
**전체 시스템 종합 진단 스크립트**
- 12단계에 걸친 완전한 시스템 테스트
- 환경변수, 토큰, API, 모듈, 서비스 등 모든 구성요소 검사
- 상세한 JSON 보고서 생성

### 2. simple_diagnosis_report.py  
**핵심 문제점 빠른 진단**
- 토큰 상태, API 연결, 배포 서비스, 로컬 모듈 확인
- 명확한 문제점과 해결방안 제시
- 긴급도별 우선순위 판정

### 3. token_refresh_helper.py
**토큰 자동 갱신 도구**
- 만료된 토큰 자동 갱신
- refresh_token을 사용한 무중단 토큰 업데이트
- 토큰 상태 실시간 모니터링

### 4. quick_token_exchange.py
**새 토큰 빠른 발급**
- 새 인증 코드로 토큰 즉시 발급
- 자동 토큰 테스트 포함
- 단계별 안내와 즉시 검증

## 🚀 사용 방법

### 현재 상태 빠른 확인
```bash
python simple_diagnosis_report.py
```

### 전체 시스템 완전 진단
```bash
python comprehensive_api_test.py
```

### 토큰 문제 해결
만료된 토큰인 경우:
```bash
# 1단계: 갱신 시도
python token_refresh_helper.py

# 2단계: 갱신 실패시 새 토큰 발급
python quick_token_exchange.py
```

## 📊 진단 결과 해석

### 성공적인 상태
```
[정상] 토큰 상태: 유효
[정상] API 호출 성공
[정상] 서비스 상태: 정상 운영 중
[정상] 모든 모듈 존재
```

### 주요 문제 유형

#### 1. 토큰 만료
```
[만료] 토큰 상태: 만료됨
[실패] 인증 실패: 토큰이 만료되었거나...
```
**해결방법**: `token_refresh_helper.py` 또는 `quick_token_exchange.py` 실행

#### 2. API 연결 실패
```
[실패] API 호출 실패
[실패] API 오류: 401/403/500
```
**해결방법**: 토큰 재발급 또는 API 권한 확인

#### 3. 모듈 누락
```
[누락] 핵심 모듈 없음
```
**해결방법**: 누락된 파일 복구 또는 재배포

#### 4. 네트워크 문제
```
[실패] 서비스 연결 실패
[실패] 로컬 서버 연결 실패
```
**해결방법**: 네트워크 설정 확인 또는 서버 재시작

## 🔍 문제별 대응 매뉴얼

### 데이터가 표시되지 않는 경우

1. **빠른 진단 실행**
   ```bash
   python simple_diagnosis_report.py
   ```

2. **토큰 상태 확인**
   - `[만료]` 표시시 → 토큰 갱신 필요
   - `[정상]` 표시시 → API 호출 문제

3. **토큰 갱신 시도**
   ```bash
   python token_refresh_helper.py
   ```

4. **갱신 실패시 새 토큰 발급**
   ```bash
   python quick_token_exchange.py
   ```
   - 브라우저에서 인증 URL 방문
   - 받은 코드를 스크립트에 입력

5. **전체 재테스트**
   ```bash
   python comprehensive_api_test.py
   ```

### API 응답 코드별 대응

- **200**: 정상 작동
- **401**: 토큰 만료 → 토큰 재발급
- **403**: 권한 부족 → 스코프 확인
- **422**: 데이터 없음 → 정상 (데이터가 실제로 없음)
- **500**: 서버 오류 → 잠시 후 재시도

## 📝 보고서 파일

### comprehensive_test_report_YYYYMMDD_HHMMSS.json
전체 테스트 결과 상세 보고서
- 각 테스트 항목별 성공/실패 여부
- 상세한 오류 메시지와 데이터
- 권장사항과 해결방안

### comprehensive_test.log
테스트 실행 과정 로그
- 각 단계별 실행 내역
- API 호출 상세 정보
- 오류 발생 시점과 원인

## 🎯 자주 발생하는 문제

### 1. "access_token time expired"
- **원인**: 토큰이 2시간마다 만료됨
- **해결**: `token_refresh_helper.py` 실행

### 2. "invalid_client" 
- **원인**: refresh_token도 만료됨 (14일)
- **해결**: `quick_token_exchange.py`로 새 토큰 발급

### 3. 배포 서비스는 정상인데 로컬에서 문제
- **원인**: 로컬 환경변수 또는 토큰 파일 문제
- **해결**: 로컬 `oauth_token.json` 파일 확인

### 4. 모든 API 호출이 401 응답
- **원인**: 토큰 완전 만료
- **해결**: 새 인증 코드로 토큰 재발급 필요

## 🔄 정기 유지보수

### 일일 점검
```bash
python simple_diagnosis_report.py
```

### 주간 전체 점검  
```bash
python comprehensive_api_test.py
```

### 토큰 자동 갱신 설정
`auto_token_manager.py`가 백그라운드에서 자동 실행되도록 설정

## 🆘 긴급 상황 대응

데이터가 전혀 표시되지 않을 때:

1. **즉시 진단**: `python simple_diagnosis_report.py`
2. **토큰 상태 확인**: 만료시 즉시 갱신
3. **API 테스트**: 수동으로 API 호출 테스트
4. **서비스 재시작**: 필요시 서버 재부팅
5. **전체 재배포**: 최후 수단으로 서비스 재배포

---

> **주의사항**: 
> - 인증 코드는 1회용이므로 사용 후 즉시 무효화됩니다
> - 토큰은 2시간마다, refresh_token은 14일마다 갱신이 필요합니다
> - API 호출 제한이 있으므로 과도한 테스트는 피하세요