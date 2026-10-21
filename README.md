# Fetal Quick Calculator v3

Streamlit 기반 태아 초음파 비율 계산기 시제품입니다.

## v3 변경 사항
- 심장 계산기를 **첫 번째 탭**으로 이동
- 심방·심실, 판막, PLAS, GOSE를 **하나의 심장 탭**에 통합
- 화면 상단에 **전체 수치 리셋** 버튼 추가 (모든 입력값 삭제)
- 두 번째 탭: 근골격계·흉곽 / 세 번째 탭: Kidney·EFW·AFI 참고치 준비 중

## 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

## GitHub 업데이트
저장소 `soobonghi/fetal_quick_calculator`에서 **Add file → Upload files**로
`app.py`, `calculations.py`, `requirements.txt`, `README.md`를 업로드하고
기존 파일을 덮어쓴 뒤 **Commit changes** 하세요.

환자 개인정보를 입력하지 마세요. 임상 검증 전 시제품입니다.
