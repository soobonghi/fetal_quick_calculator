from __future__ import annotations
import math
import streamlit as st
from calculations import ratio, plas_index, gose_ratio
from reference_calc import at_ga, percentile_band
from reference_data import EFW_SINGLE, EFW_DC, EFW_MC, AFI, FOOT_CM, THYMUS_CM, KIDNEY_MM, REFERENCE_INFO

st.set_page_config(page_title='Fetal Quick Calculator', page_icon='📐', layout='wide')
st.markdown('<style>.block-container{max-width:1100px;padding-top:1.5rem}</style>', unsafe_allow_html=True)

INPUT_KEYS = ('rv','lv','ra','la','tv','mv','pv','av','plas_dist','dao',
              'g_ra','g_arv','g_frv','g_la','g_lv','fl','foot','ac','tc',
              'kidney','efw','afi','thymus')

def reset_inputs():
    for key in INPUT_KEYS:
        st.session_state[key] = ''
    # 임신 주수 및 EFW 유형은 유지하고 측정값만 초기화합니다.

def number(label, key, unit='mm'):
    raw = st.text_input(f'{label} ({unit})', key=key, placeholder='측정값 입력')
    if not raw.strip():
        return None
    try:
        val = float(raw)
        if not math.isfinite(val) or val <= 0:
            raise ValueError
        return val
    except ValueError:
        st.error(f'{label}: 0보다 큰 유한한 숫자를 입력해 주세요.')
        return None

reports=[]
def show_ratio(name, a, b, show_percent=False):
    if a is None or b is None:
        return
    val = ratio(a,b)
    st.metric(name, f'{val:.2f}')
    if show_percent:
        st.caption(f'{val*100:.1f}%')
    reports.append(f'{name}: {val:.2f}')

c1,c2=st.columns([5,1.5],vertical_alignment='bottom')
with c1:
    st.title('Fetal Quick Calculator')
    st.caption('심장 · 근골격계 · 임신 주수별 참고치')
with c2:
    st.button('↺ 전체 수치 리셋',on_click=reset_inputs,use_container_width=True)
st.warning('임상 검증 전 시제품입니다. 환자 식별정보를 입력하지 마세요. 참고치는 원문과 대조 후 사용하세요.')

st.markdown('**공통 임신 주수**')
c1,c2=st.columns(2)
with c1: weeks=st.number_input('Weeks',min_value=10,max_value=42,value=None,step=1,key='ga_w',placeholder='주수 입력')
with c2: days=st.number_input('Days',min_value=0,max_value=6,value=None,step=1,key='ga_d',placeholder='일수 입력')
ga=f'{weeks}w{days}d' if weeks is not None and days is not None else 'GA 미입력'
ga_ref=(f'{weeks}wks' if days in (None,0) else f'{weeks}w{days}d') if weeks is not None else 'GA 미입력'

def get_ref(table):
    if weeks is None or days is None:
        return None
    return at_ga(table, weeks, days)

def ref_caption(name):
    st.caption('Ref. ' + REFERENCE_INFO[name])

def show_band(label, value, row, ps, unit):
    if value is None or row is None:
        return
    band = percentile_band(value, ps, row)
    st.metric(label, band)
    reports.append(f'{label}: {value:g} {unit}, {band} ({ga})')


heart, musculo, refs=st.tabs(['🫀 심장','🦴 근골격계·흉곽','📚 참고치'])
with heart:
    st.subheader('심장 계산기')
    st.markdown('**심실 비율 (RV/LV)**')
    c1,c2=st.columns(2)
    with c1: rv=number('RV dimension','rv')
    with c2: lv=number('LV dimension','lv')
    if rv is not None and lv is not None:
        rv_lv=ratio(rv,lv)
        rv_lv_text=(f'Rt dominant heart (RV:LV = {rv_lv:.2f})'
                    if rv_lv >= 1.5 else
                    f'Not definite Rt dominant heart (RV:LV = {rv_lv:.2f})')
        st.markdown('**기록용 결과 — RV/LV**')
        st.code(rv_lv_text, language=None)
        reports.append(rv_lv_text)
    else:
        st.caption('RV와 LV를 모두 입력하면 기록용 문구가 나타납니다.')
    st.markdown('**심방 비율 (RA/LA)**')
    c1,c2=st.columns(2)
    with c1: ra=number('RA dimension','ra')
    with c2: la=number('LA dimension','la')
    if ra is not None and la is not None:
        ra_la=ratio(ra,la)
        st.markdown('**기록용 결과 — RA/LA**')
        ra_la_text=f'RA/LA = {ra_la:.2f}'
        st.code(ra_la_text,language=None)
        reports.append(ra_la_text)
    else:
        st.caption('RA와 LA를 모두 입력하면 기록용 문구가 나타납니다.')
    st.divider()
    st.markdown('**판막 비율**')
    c1,c2=st.columns(2)
    with c1: tv=number('TV annulus','tv')
    with c2: mv=number('MV annulus','mv')
    show_ratio('TV/MV',tv,mv)
    c1,c2=st.columns(2)
    with c1: pv=number('PV annulus','pv')
    with c2: av=number('AV annulus','av')
    show_ratio('PV/AV',pv,av)
    st.divider()
    st.markdown('**GOSE Score (Ebstein 관련)**')
    st.caption('면적 단위 cm². (RA + atrialized RV) / (functional RV + LA + LV)')
    c1,c2=st.columns(2)
    with c1:
        gra=number('RA area','g_ra','cm²'); garv=number('Atrialized RV area','g_arv','cm²'); gfrv=number('Functional RV area','g_frv','cm²')
    with c2:
        gla=number('LA area','g_la','cm²'); glv=number('LV area','g_lv','cm²')
    if all(v is not None for v in (gra,garv,gfrv,gla,glv)):
        val=gose_ratio(gra,garv,gfrv,gla,glv)
        grade=1 if val<.5 else 2 if val<1 else 3 if val<1.5 else 4
        st.metric('GOSE Grade',str(grade))
        reports.append(f'GOSE Grade: {grade}')
    st.divider()
    st.markdown('**PLAS Index (TAPVR 관련)**')
    c1,c2=st.columns(2)
    with c1: dist=number('Post-LA distance','plas_dist')
    with c2: dao=number('Descending aorta diameter','dao')
    if dist is not None and dao is not None:
        val=plas_index(dist,dao)
        st.metric('PLAS Index',f'{val:.2f}')
        reports.append(f'PLAS Index: {val:.2f}')

with musculo:
    st.subheader('근골격계·흉곽')
    st.caption('길이·둘레는 mm 단위로 입력합니다.')
    c1,c2=st.columns(2)
    with c1:
        fl=number('FL','fl'); foot=number('Foot length','foot'); ac=number('AC','ac')
    with c2: tc=number('Thoracic circumference','tc')
    c1,c2,c3=st.columns(3)
    with c1: show_ratio('FL/Foot',fl,foot)
    with c2: show_ratio('FL/AC',fl,ac,True)
    with c3: show_ratio('TC/AC',tc,ac)
    st.divider()
    st.markdown('**Foot length 참고치**')
    foot_row = get_ref(FOOT_CM)
    if foot_row is None:
        st.caption('Foot length 참고치: 15–37주 (마지막 주는 0일)')
    else:
        foot_mm = [v*10 for v in foot_row]
        show_band('Foot length percentile interval', foot, foot_mm, [5,10,50,90,95], 'mm')
        st.caption(' | '.join(f'P{pct}: {val:.1f} mm' for pct,val in zip([5,10,50,90,95],foot_mm)))
        ref_caption('FOOT_CM')

with refs:
    st.subheader('임신 주수별 참고치')
    st.caption('임신 주수(Weeks, Days)를 입력하면 해당 주수의 참고치를 조회합니다. 주+일은 인접 주수 간 선형보간한 값입니다.')
    with st.container(border=True):
        st.markdown('**EFW (g)**')
        group=st.selectbox('임신 형태',('Singleton (NICHD Asian)','DC twin (Ananth 1998)','MC twin (Ananth 1998)'),key='efw_group')
        efw=number('EFW','efw','g')
        if group.startswith('Singleton'):
            t,ps,refname=EFW_SINGLE,[3,5,10,50,90,95,97],'EFW_SINGLE'
        elif group.startswith('DC'):
            t,ps,refname=EFW_DC,[5,10,50,90,95],'EFW_DC'
        else:
            t,ps,refname=EFW_MC,[5,10,50,90,95],'EFW_MC'
        row=get_ref(t)
        if row is None:
            st.caption(f'참고치 범위: {min(t)}–{max(t)}주 (마지막 주는 0일)')
        else:
            show_band('EFW percentile interval',efw,row,ps,'g')
            st.caption(' | '.join(f'P{pct}: {val:.0f} g' for pct,val in zip(ps,row) if val is not None))
            ref_caption(refname)
            if group.startswith('Singleton') and weeks==21:
                st.caption('21주 P97은 제공된 표에 값의 불일치가 있어 표시하지 않았습니다.')
            if not group.startswith('Singleton'):
                st.caption('DC/MC 자료는 초음파 추정체중 성장곡선이 아닌 쌍태아 출생체중 참고표입니다.')
    with st.container(border=True):
        st.markdown('**Kidney length (mm)**')
        kidney=number('Kidney length','kidney')
        row=get_ref(KIDNEY_MM)
        if row is None:
            st.caption('참고치 범위: 16–41주 (마지막 주는 0일)')
        else:
            p5,p50,p95=row
            show_band('Kidney length percentile interval',kidney,row,[5,50,95],'mm')
            text=f'Ref. {ga_ref} 5th percentile: {p5:.1f} mm\nRef. {ga_ref} 95th percentile: {p95:.1f} mm'
            st.code(text,language=None)
            if kidney is not None:
                reports.extend(text.splitlines())
            st.caption(f'P50: {p50:.1f} mm')
            ref_caption('KIDNEY_MM')
    with st.container(border=True):
        st.markdown('**AFI (mm)**')
        afi=number('AFI','afi')
        row=get_ref(AFI)
        if row is None:
            st.caption('참고치 범위: 16–42주 (마지막 주는 0일)')
        else:
            show_band('AFI percentile interval',afi,row,[3,5,50,95,97],'mm')
            st.caption(' | '.join(f'P{pct}: {val:.1f} mm' for pct,val in zip([3,5,50,95,97],row)))
            ref_caption('AFI')
    with st.container(border=True):
        st.markdown('**Thymic diameter (mm)**')
        thymus=number('Thymic diameter','thymus')
        row=get_ref(THYMUS_CM)
        if row is None:
            st.caption('참고치 범위: 19–38주 (마지막 주는 0일)')
        else:
            mean,lower,upper=[v*10 for v in row]
            if thymus is not None:
                status=('Below lower limit' if thymus < lower else 'Above upper limit' if thymus > upper else 'Within range')
                st.metric('95% reference range',status)
                reports.append(f'Thymic diameter: {thymus:g} mm ({ga}); {status}')
            text=f'Ref. {ga_ref} lower limit of 95% reference range: {lower:.1f} mm'
            st.code(text,language=None)
            if thymus is not None:
                reports.append(text)
            st.caption(f'Mean: {mean:.1f} mm | Upper limit: {upper:.1f} mm')
            ref_caption('THYMUS_CM')

st.divider()
st.subheader('ViewPoint 복사용 결과')
if reports:
    st.code('\n'.join(reports),language=None)
    st.download_button('TXT 파일 저장',data='\n'.join(reports).encode('utf-8'),file_name='fetal_quick_results.txt',mime='text/plain')
else:
    st.caption('측정값을 입력하면 계산 결과가 여기에 나타납니다.')
