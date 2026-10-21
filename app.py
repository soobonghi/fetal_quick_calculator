from __future__ import annotations

import streamlit as st
from calculations import fl_foot, fl_ac, tc_ac, ratio, plas_index, gose_ratio

st.set_page_config(page_title="Fetal Quick Calculator", page_icon="📐", layout="wide")

st.markdown("""<style>
.block-container {max-width: 1080px; padding-top: 2rem}
[data-testid="stMetricValue"] {font-size: 1.65rem}
</style>""", unsafe_allow_html=True)

st.title("Fetal Quick Calculator")
st.caption("태아 초음파 검사자를 위한 측정 비율 계산 및 ViewPoint 기록 초안 · Prototype v2")
st.info("임상 검증 전 시제품입니다. 환자 식별정보를 입력하지 마세요. 결과는 검사자가 측정 기준·단위·참고문헌을 확인한 후 사용해야 합니다.")


def num(label: str, key: str, unit: str = "mm", help_text: str | None = None):
    """Optional positive numeric input; empty means not measured."""
    raw = st.text_input(f"{label} ({unit})", key=key, placeholder="측정값 입력", help=help_text)
    if not raw.strip():
        return None
    try:
        value = float(raw.strip())
        if not (0 < value < float("inf")):
            raise ValueError
        return value
    except ValueError:
        st.warning(f"{label}: 0보다 큰 숫자를 입력해 주세요.")
        return None


def result(label, value, unit="", percent=False):
    if value is None:
        return
    st.metric(label, f"{value:.3f}{unit}")
    if percent:
        st.caption(f"백분율 표현: {value * 100:.1f}%")
    lines.append(f"{label}: {value:.3f}{unit}")


def pair_result(label, a, b, percent=False):
    if a is not None and b is not None:
        result(label, ratio(a, b), percent=percent)


lines = []
tabs = st.tabs(["🦴 근골격계·흉곽", "🫀 심방·심실", "🫀 판막·지표", "📚 참고치 (추가 예정)"])

with tabs[0]:
    st.subheader("근골격계 및 흉곽")
    st.caption("길이 및 둘레는 모두 mm로 입력합니다. Ratio는 무단위입니다.")
    c1, c2 = st.columns(2)
    with c1:
        fl = num("FL", "fl")
        foot = num("Foot length", "foot")
        ac = num("AC", "ac")
    with c2:
        tc = num("TC (Thoracic circumference)", "tc")
    st.divider()
    r1, r2, r3 = st.columns(3)
    with r1:
        if fl is not None and foot is not None:
            result("FL/Foot", fl_foot(fl, foot))
    with r2:
        if fl is not None and ac is not None:
            result("FL/AC", fl_ac(fl, ac), percent=True)
    with r3:
        if tc is not None and ac is not None:
            result("TC/AC", tc_ac(tc, ac))

with tabs[1]:
    st.subheader("심실 및 심방 비율")
    st.caption("같은 비율의 분자·분모는 반드시 동일한 측정 방식과 단위를 사용하세요. 아래 기본 입력은 길이(mm)입니다.")
    c1, c2 = st.columns(2)
    with c1:
        rv = num("RV dimension", "rv")
        ra = num("RA dimension", "ra")
    with c2:
        lv = num("LV dimension", "lv")
        la = num("LA dimension", "la")
    c1, c2 = st.columns(2)
    with c1:
        pair_result("RV/LV", rv, lv)
    with c2:
        pair_result("RA/LA", ra, la)

with tabs[2]:
    st.subheader("판막 비율")
    st.caption("판막 직경은 동일한 시기·측정 기준의 mm 값으로 입력하세요.")
    c1, c2 = st.columns(2)
    with c1:
        tv = num("TV annulus", "tv")
        pv = num("PV annulus", "pv")
    with c2:
        mv = num("MV annulus", "mv")
        av = num("AV annulus", "av")
    c1, c2 = st.columns(2)
    with c1:
        pair_result("TV/MV", tv, mv)
    with c2:
        pair_result("PV/AV", pv, av)

    st.divider()
    st.subheader("PLAS index · TAPVR 관련")
    st.caption("LA 후벽과 descending aorta 사이 거리 / descending aorta 직경. 동일한 영상면과 측정 기준 확인이 필요합니다.")
    c1, c2 = st.columns(2)
    with c1:
        plas_dist = num("Post-LA distance", "plas_dist")
    with c2:
        dao = num("Descending aorta diameter", "dao")
    if plas_dist is not None and dao is not None:
        result("PLAS index", plas_index(plas_dist, dao))

    st.divider()
    st.subheader("GOSE / Celermajer area ratio · Ebstein 관련")
    st.caption("(RA area + atrialized RV area) / (functional RV area + LA area + LV area). 면적은 cm²로 통일합니다. 임상 등급 판정은 제공하지 않습니다.")
    c1, c2 = st.columns(2)
    with c1:
        ra_area = num("RA area", "g_ra", "cm²")
        arv_area = num("Atrialized RV area", "g_arv", "cm²")
        frv_area = num("Functional RV area", "g_frv", "cm²")
    with c2:
        la_area = num("LA area", "g_la", "cm²")
        lv_area = num("LV area", "g_lv", "cm²")
    vals = [ra_area, arv_area, frv_area, la_area, lv_area]
    if all(v is not None for v in vals):
        result("GOSE area ratio", gose_ratio(*vals))
    st.caption("※ GOSE 측정 범위 및 기관별 기록 방식은 담당 교수·원내 프로토콜과 최종 대조해 주세요.")

with tabs[3]:
    st.subheader("참고치 계산 · 병원 자료 수령 후 구현")
    st.write("아래 세 항목은 메뉴를 미리 준비했습니다. 현재는 백분위나 정상·이상 판정을 계산하지 않습니다.")
    for title, desc in [
        ("Kidney length", "임신 주수별 P5 / P50 / P95"),
        ("EFW percentile", "임신 주수별 체중 백분위"),
        ("AFI percentile", "임신 주수별 P5 / P50 / P95"),
    ]:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(f"{desc} · 병원 참고표 및 출처 확인 후 활성화 예정")
    st.warning("참고문헌마다 기준 집단·주수 범위·단위·백분위 계산법이 달라 임의 수치를 넣지 않았습니다.")

st.divider()
st.subheader("ViewPoint 기록용 결과")
if lines:
    report = "\n".join(lines)
    st.code(report, language=None)
    st.caption("위 텍스트 오른쪽 복사 아이콘을 눌러 복사할 수 있습니다. 미입력 항목은 결과에 포함되지 않습니다.")
    st.download_button("TXT 파일 저장", data=report.encode("utf-8"), file_name="fetal_quick_results.txt", mime="text/plain")
else:
    st.caption("측정값을 입력하면 계산 결과가 이곳에 자동으로 정리됩니다.")
