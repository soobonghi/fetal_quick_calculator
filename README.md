# Fetal Quick Calculator v10

## 변경사항
- 심방 비율을 **LA/RA = LA ÷ RA**로 수정했습니다.
- 각 측정값 아래에만 기록용 결과를 표시하며 하단 전체 ViewPoint 결과 모음은 제거했습니다.
- EFW: `EFW: 634 g, 24w0d size (Ref. 24wks 50th percentile: 634 g)` 형식. 수치는 예시이며 실제 계산값에 따라 달라집니다.
  - `size`는 선택한 Singleton/DC/MC 참고표의 P50 값을 역보간한 **추정 주수**입니다.
  - `Ref.`는 측정값과 가장 가까운 **표에 실제 제공된 백분위 지점**입니다. 정확한 개인별 percentile을 의미하지 않으므로 percentile interval도 표시합니다.
  - DC/MC 참고표는 **출생체중** 자료로, 초음파 EFW 성장곡선과 다릅니다.
- 근골격계 비율에는 정상범위 대신 문헌에 기재된 이상 참고 기준을 표시합니다: FL/Foot <0.90, FL/AC <0.16, TC/AC <0.60. 이 수치만으로 골격이형성증이나 예후를 판정할 수 없습니다.

## 근거
- Krakow et al. Guidelines for the prenatal diagnosis of fetal skeletal dysplasias. Genetics in Medicine (2009). https://pmc.ncbi.nlm.nih.gov/articles/PMC2832320/
- Wood et al. The Reliability of Ultrasound Markers in Identifying Fetuses With a Life-Limiting Skeletal Dysplasia. Prenatal Diagnosis (2024). https://pubmed.ncbi.nlm.nih.gov/39078648/

기존 참고치의 출처와 이용 조건은 각 소스 파일을 확인하세요. 환자 식별정보는 입력하지 마세요. 임상 사용 전 원문 수치 및 계산식 검증이 필요합니다.

## 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```


## v11 변경사항
- 홈페이지 상단의 시제품 경고 문구 삭제 (실제 임상 적용 전 검증 필요성은 동일)
- Singleton은 EFW 1개, DC/MC twin은 Twin A / Twin B EFW 2개 입력
- Twin A / Twin B 각각의 참고치 및 P50 기준 추정 주수 표시
- Twin EFW discordance (%) 자동 계산: |A-B| / max(A,B) × 100
- 전체 입력 초기화 시 임신 주수 및 임신 형태는 유지
\n\n## v13\n- Removed valve ratios (TV/MV, PV/AV).\n- Added CTCR (cardiac circumference / thoracic circumference) and CTAR (cardiac area / thoracic area), with per-item copyable output.\n- EFW per-fetus results now appear directly beneath each input; Kidney, AFI and Thymus show copyable value-and-reference lines beneath their inputs.\n- FL/AC and TC/AC outputs placed beneath their own measurement sections.\n