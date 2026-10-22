# Fetal Quick Calculator v6

태아 초음파 계산기(Streamlit). 측정값은 기본적으로 비어 있으며, 임신 주수는 Weeks/Days로 입력합니다.

## v6 변경 사항
- 심장 탭: GOSE Grade를 PLAS Index 위로 이동. GOSE는 Grade만 표시.
- 홈페이지에서 요청한 GOSE 안내 문구와 Foot length 공개 버전 안내 문구 제거.
- Singleton(NICHD Asian) 기본 / DC twin / MC twin EFW 참고치, AFI, kidney length, thymic diameter, foot length 참고치 추가.
- Kidney P5/P95와 thymic lower 95% reference limit 복사 가능한 문구 표시.
- RV/LV >= 1.5는 `Rt dominant heart (RV:LV = 0.00)`, 미만은 `Not definite Rt dominant heart (RV:LV = 0.00)` 형식. 소수점 둘째 자리.
- RV → LV → RA → LA 입력 순서 유지, 측정값만 초기화.

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 참고자료 및 주의
- 출처 설명은 `reference_data.py`의 `REFERENCE_INFO`를 참고하세요.
- NICHD Fetal Growth Studies Asian cohort, EFW 표.
- Ananth et al. (1998), DC/MC twin smoothed birthweight percentiles. **초음파 EFW 성장곡선이 아닌 출생체중 분포**입니다.
- Moore & Cayle (1990), AFI reference percentiles.
- Foot length, J Ultrasound Med 2000 (제공된 표; 서지정보 확인 필요).
- Thymic diameter, Ultrasound Obstet Gynecol 2007;29:634–638. 표의 95% reference range 하한은 **5th percentile과 동일하다고 볼 수 없습니다**.
- Fetal kidney length fitted centiles, Table S2 (정확한 원문 서지정보 확인 필요).

주+일 참고치는 주별 값의 선형보간이며 논문에서 직접 제공한 값은 아닙니다. 제공된 사진과 코드의 전수 원문 대조, 계산식의 임상 검증 및 원문 표 데이터 재사용·공개 권한 확인이 필요합니다. 환자 식별정보를 입력하지 마세요.
