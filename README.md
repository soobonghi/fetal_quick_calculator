# Fetal Quick Calculator — Public version

Streamlit 기반 태아 초음파 측정값 비율 계산기입니다.

## 기능
- 심장: RV/LV, RA/LA, TV/MV, PV/AV, PLAS index, GOSE Grade(사망률 미표시)
- 근골격계: FL/Foot, FL/AC, TC/AC
- 참고치 입력 UI: EFW (Singleton 기본, DC/MC 선택), Kidney length, AFI, Thymic diameter
- 전체 입력 초기화, ViewPoint 복사용 텍스트 및 TXT 저장

## 공개 배포를 위한 변경 사항
- 원문 표에서 옮긴 수치와 백분위 데이터 파일을 **완전히 제외**했습니다.
- EFW/Kidney/AFI/Foot/Thymus percentile 계산은 **비활성화**했습니다. 값이 없는데도 임의의 참고치를 표시하지 않습니다.
- 논문 표의 이미지·전체 표·백분위 데이터는 포함하지 않습니다.
- 의학적 계산식/등급은 독립적으로 원문 검증이 필요합니다.

## 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 주의
교육·개발용 시제품으로, 임상 진단 및 의사결정에 사용하기 전 검증이 필요합니다. 환자 식별정보를 입력하지 마세요. 참고치 데이터를 제외하더라도 공개 사용에 대한 모든 법적 문제가 자동 해결되는 것은 아닙니다.
