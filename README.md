# Fetal Quick Calculator v2

태아 초음파 검사자용 Streamlit 계산기 시제품. 확정된 10개 항목(일부 묶음) 중 **7개 계산 그룹 구현**, **3개 참고치 그룹 대기**.

## 설치/실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

GitHub 저장소에 `app.py`, `calculations.py`, `requirements.txt`를 업로드하고 Streamlit Community Cloud에서 `app.py`를 메인 파일로 설정할 수 있습니다.

## 구현된 계산 그룹

1. FL/Foot = FL / Foot length
2. FL/AC = FL / AC (ratio와 %)
3. TC/AC = TC / AC
4. RV/LV 및 RA/LA = 같은 단위·측정법의 비율
5. TV/MV 및 PV/AV = 판막 직경 비율
6. PLAS index = post-LA distance / descending aorta diameter
7. GOSE/Celermajer area ratio = (RA area + atrialized RV area) / (functional RV area + LA area + LV area)

입력 단위: 길이/둘레/판막/PLAS는 mm, GOSE 면적은 cm². 분자와 분모는 같은 단위·측정 방식이어야 합니다.

## 아직 계산하지 않는 항목

- Kidney length GA별 P5/P50/P95
- EFW percentile
- AFI GA별 P5/P50/P95

병원에서 사용하는 표/참고문헌을 확인한 후 개발합니다. 임의의 percentile, cutoff 또는 정상·이상 판정은 표시하지 않습니다.

## 안전·품질

- 환자 개인정보를 입력하지 마세요. 계산기에는 데이터베이스/서버 저장 로직이 없습니다.
- 수치 계산의 단위·반올림·측정면 및 GOSE/PLAS 정의를 임상 책임자와 검증하세요.
- 임상 검증 전 시제품으로, 단독 진단 또는 진료 결정에 사용하지 마세요.
- ViewPoint 출력은 단순 결과 텍스트이며 실제 원내 결과 양식은 추가로 조정할 수 있습니다.
