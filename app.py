from __future__ import annotations
import math
import streamlit as st
from calculations import ratio, plas_index, gose_ratio

st.set_page_config(page_title='Fetal Quick Calculator', page_icon='📐', layout='wide')
st.markdown('<style>.block-container{max-width:1100px;padding-top:1.5rem}</style>', unsafe_allow_html=True)

INPUT_KEYS = ('rv','lv','ra','la','tv','mv','pv','av','plas_dist','dao',
              'g_ra','g_arv','g_frv','g_la','g_lv','fl','foot','ac','tc',
              'kidney','efw','afi','thymus')

def reset_inputs():
    for key in INPUT_KEYS:
        st.session_state[key] = ''
    st.session_state['ga_w'] = 24
    st.session_state['ga_d'] = 0
    st.session_state['efw_group'] = 'Singleton'

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
    st.metric(name, f'{val:.3f}')
    if show_percent:
        st.caption(f'{val*100:.1f}%')
    reports.append(f'{name}: {val:.3f}')

c1,c2=st.columns([5,1.5],vertical_alignment='bottom')
with c1:
    st.title('Fetal Quick Calculator')
    st.caption('심장 · 근골격계 · 참고치 입력 준비 | Public prototype')
with c2:
    st.button('↺ 전체 수치 리셋',on_click=reset_inputs,use_container_width=True)
st.warning('임상 검증 전 시제품입니다. 환자 식별정보를 입력하지 마세요. 공개 버전에는 논문 참고치 표를 포함하지 않습니다.')

st.markdown('**공통 임신 주수**')
c1,c2=st.columns(2)
with c1: weeks=st.number_input('Weeks',min_value=10,max_value=42,value=24,step=1,key='ga_w')
with c2: days=st.number_input('Days',min_value=0,max_value=6,value=0,step=1,key='ga_d')
ga=f'{weeks}w{days}d'

heart, musculo, refs=st.tabs(['🫀 심장','🦴 근골격계·흉곽','📚 참고치 (준비 중)'])
with heart:
    st.subheader('심장 계산기')
    st.markdown('**심실·심방 비율**')
    c1,c2=st.columns(2)
    with c1:
        rv=number('RV dimension','rv'); ra=number('RA dimension','ra')
    with c2:
        lv=number('LV dimension','lv'); la=number('LA dimension','la')
    c1,c2=st.columns(2)
    with c1: show_ratio('RV/LV',rv,lv)
    with c2: show_ratio('RA/LA',ra,la)
    st.divider()
    st.markdown('**판막 비율**')
    c1,c2=st.columns(2)
    with c1:
        tv=number('TV annulus','tv'); pv=number('PV annulus','pv')
    with c2:
        mv=number('MV annulus','mv'); av=number('AV annulus','av')
    c1,c2=st.columns(2)
    with c1: show_ratio('TV/MV',tv,mv)
    with c2: show_ratio('PV/AV',pv,av)
    st.divider()
    st.markdown('**PLAS Index (TAPVR 관련)**')
    c1,c2=st.columns(2)
    with c1: dist=number('Post-LA distance','plas_dist')
    with c2: dao=number('Descending aorta diameter','dao')
    if dist is not None and dao is not None:
        val=plas_index(dist,dao)
        st.metric('PLAS Index',f'{val:.3f}')
        reports.append(f'PLAS Index: {val:.3f}')
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
    st.caption('Grade만 표시합니다. 예후 수치 및 사망률은 표시하지 않습니다. 측정 기준과 경계값은 임상 검증이 필요합니다.')

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
    st.info('Foot length의 주수별 percentile 참고치는 공개 버전에서 제외했습니다. FL/Foot 계산은 정상 작동합니다.')

with refs:
    st.subheader('임신 주수별 참고치')
    st.caption('참고치 수치 데이터는 공개 저장소에 포함하지 않았습니다. 입력 UI만 제공하며 percentile 판정은 수행하지 않습니다.')
    with st.container(border=True):
        st.markdown('**EFW (g)**')
        group=st.selectbox('임신 형태',('Singleton','DC twin','MC twin'),key='efw_group')
        efw=number('EFW','efw','g')
        if efw is not None: reports.append(f'EFW ({group}): {efw:g} g ({ga}); percentile reference pending')
        st.info('EFW percentile: 참고치 미탑재')
    with st.container(border=True):
        st.markdown('**Kidney length (mm)**')
        kidney=number('Kidney length','kidney')
        if kidney is not None: reports.append(f'Kidney length: {kidney:g} mm ({ga}); reference pending')
        st.caption(f'Ref. {weeks}wks 5th or 95th percentile: 참고치 미탑재')
    with st.container(border=True):
        st.markdown('**AFI (mm)**')
        afi=number('AFI','afi')
        if afi is not None: reports.append(f'AFI: {afi:g} mm ({ga}); reference pending')
        st.info('AFI percentile: 참고치 미탑재')
    with st.container(border=True):
        st.markdown('**Thymic diameter (mm)**')
        thymus=number('Thymic diameter','thymus')
        if thymus is not None: reports.append(f'Thymic diameter: {thymus:g} mm ({ga}); reference pending')
        st.caption(f'Ref. {weeks}wks lower limit of 95% reference range: 참고치 미탑재')
        st.caption('참고: 95% reference range의 하한은 5th percentile과 동일하지 않을 수 있습니다.')

st.divider()
st.subheader('ViewPoint 복사용 결과')
if reports:
    st.code('\n'.join(reports),language=None)
    st.download_button('TXT 파일 저장',data='\n'.join(reports).encode('utf-8'),file_name='fetal_quick_results.txt',mime='text/plain')
else:
    st.caption('측정값을 입력하면 계산 결과가 여기에 나타납니다.')
