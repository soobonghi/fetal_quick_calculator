from __future__ import annotations
import math
import streamlit as st
from calculations import ratio, plas_index, gose_ratio
from reference_calc import at_ga, percentile_band, median_equivalent_ga, nearest_reference_percentile
from reference_data import EFW_SINGLE, EFW_DC, EFW_MC, AFI, FOOT_CM, THYMUS_CM, KIDNEY_MM, REFERENCE_INFO
from reference_extra import DESCENDING_RECTUM, SMALL_BOWEL_COLON, STOMACH, NASAL_BONE, EAR_LENGTH, EXTRA_SOURCES

st.set_page_config(page_title='Fetal Quick Calculator', page_icon='📐', layout='wide')
st.markdown('<style>.block-container{max-width:1100px;padding-top:1.5rem}</style>', unsafe_allow_html=True)

INPUT_KEYS = ('rv','lv','ra','la','plas_dist','dao',
              'g_ra','g_arv','g_frv','g_la','g_lv','card_circ','thor_circ','card_area','thor_area','fl','foot_rt','foot_lt','ac','tc',
              'kidney','efw','efw_a','efw_b','afi','thymus',
              'descending_colon','rectum','small_bowel','colon','stomach',
              'nasal_bone','ear_rt','ear_lt')

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

def show_ratio(name, a, b, show_percent=False):
    if a is None or b is None:
        return
    val = ratio(a,b)
    st.code(f'{name}: {val:.2f}', language=None)
    if show_percent:
        st.caption(f'{val*100:.1f}%')

c1,c2=st.columns([5,1.5],vertical_alignment='bottom')
with c1:
    st.title('Fetal Quick Calculator')
    st.caption('심장 · 근골격계 · 임신 주수별 참고치')
with c2:
    st.button('↺ 전체 수치 리셋',on_click=reset_inputs,use_container_width=True)

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


heart, musculo, digestive, face, refs=st.tabs(['🫀 심장','🦴 근골격계·흉곽','🩺 소화기계','👶 얼굴 계측','📚 참고치'])
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
    else:
        st.caption('RV와 LV를 모두 입력하면 기록용 문구가 나타납니다.')
    st.markdown('**심방 비율 (LA/RA)**')
    c1,c2=st.columns(2)
    with c1: la=number('LA dimension','la')
    with c2: ra=number('RA dimension','ra')
    if ra is not None and la is not None:
        la_ra=ratio(la,ra)
        st.markdown('**기록용 결과 — LA/RA**')
        la_ra_text=f'LA/RA = {la_ra:.2f}'
        st.code(la_ra_text,language=None)
    else:
        st.caption('RA와 LA를 모두 입력하면 기록용 문구가 나타납니다.')
    st.divider()
    st.markdown('**CTCR · CTAR**')
    st.caption('CTCR = Cardiac circumference / Thoracic circumference · CTAR = Cardiac area / Thoracic area')
    with st.container(border=True):
        st.markdown('**CTCR (Cardiothoracic Circumference Ratio)**')
        c1,c2=st.columns(2)
        with c1: card_circ=number('Cardiac circumference','card_circ')
        with c2: thor_circ=number('Thoracic circumference','thor_circ')
        if card_circ is not None and thor_circ is not None:
            st.code(f'CTCR: {ratio(card_circ,thor_circ):.2f}',language=None)
    with st.container(border=True):
        st.markdown('**CTAR (Cardiothoracic Area Ratio)**')
        c1,c2=st.columns(2)
        with c1: card_area=number('Cardiac area','card_area','cm²')
        with c2: thor_area=number('Thoracic area','thor_area','cm²')
        if card_area is not None and thor_area is not None:
            st.code(f'CTAR: {ratio(card_area,thor_area):.2f} ({ratio(card_area,thor_area)*100:.1f}%)',language=None)
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
        st.code(f'GOSE Grade: {grade}',language=None)
    st.divider()
    st.markdown('**PLAS Index (TAPVR 관련)**')
    c1,c2=st.columns(2)
    with c1: dist=number('Post-LA distance','plas_dist')
    with c2: dao=number('Descending aorta diameter','dao')
    if dist is not None and dao is not None:
        val=plas_index(dist,dao)
        st.code(f'PLAS Index: {val:.2f}',language=None)

with musculo:
    st.subheader('근골격계·흉곽')
    st.caption('길이·둘레는 mm 단위로 입력합니다.')

    st.markdown('**FL / Foot length**')
    fl=number('FL','fl')
    c1,c2=st.columns(2)
    with c1: foot_rt=number('Foot length Rt','foot_rt')
    with c2: foot_lt=number('Foot length Lt','foot_lt')
    foot_values=[v for v in (foot_rt,foot_lt) if v is not None]
    foot_for_ratio=(sum(foot_values)/len(foot_values)) if foot_values else None

    if fl is not None and foot_for_ratio is not None:
        fl_foot_value=ratio(fl,foot_for_ratio)
        fl_foot_text=f'FL/Foot: {fl_foot_value:.2f} (Abnormal cutoff: <0.90)'
        st.code(fl_foot_text,language=None)
        if len(foot_values)==2:
            st.caption('FL/Foot 비율은 Rt·Lt foot length의 평균으로 계산했습니다.')
        else:
            st.caption('FL/Foot 비율은 입력된 한쪽 foot length로 계산했습니다.')
    else:
        st.caption('FL과 Rt/Lt foot length 중 하나 이상을 입력하면 FL/Foot 결과가 나타납니다.')

    # 측정한 Rt/Lt 길이와 주수별 5th percentile을 한 문장으로 복사할 수 있게 표시.
    foot_row=get_ref(FOOT_CM)
    if foot_row is None:
        st.caption('Foot length 참고치: 15–37주 (마지막 주는 0일). 공통 임신 주수를 입력해 주세요.')
    else:
        foot_p5_mm=foot_row[0]*10  # published table is in cm
        if foot_values:
            rt_text=f'{foot_rt:g}' if foot_rt is not None else '—'
            lt_text=f'{foot_lt:g}' if foot_lt is not None else '—'
            foot_text=(f'Foot length: Rt {rt_text} mm, Lt {lt_text} mm '
                       f'(Ref. {ga_ref} 5th percentile: {foot_p5_mm:.1f} mm)')
            st.markdown('**기록용 결과 — Foot length**')
            st.code(foot_text,language=None)
        else:
            st.caption(f'Ref. {ga_ref} 5th percentile: {foot_p5_mm:.1f} mm')
        ref_caption('FOOT_CM')

    st.divider()
    st.markdown('**FL/AC**')
    ac=number('AC','ac')
    if fl is not None and ac is not None:
        st.code(f'FL/AC: {ratio(fl,ac):.2f} (Abnormal cutoff: <0.16)',language=None)
    else:
        st.caption('FL과 AC를 입력하면 바로 아래에 결과가 표시됩니다.')
    st.divider()
    st.markdown('**TC/AC**')
    tc=number('Thoracic circumference','tc')
    if tc is not None and ac is not None:
        st.code(f'TC/AC: {ratio(tc,ac):.2f} (Abnormal cutoff: <0.60)',language=None)
    else:
        st.caption('TC와 AC를 입력하면 바로 아래에 결과가 표시됩니다.')



def extra_source(name):
    st.caption('Ref. ' + EXTRA_SOURCES[name])

def reference_line(title, value, reference_text, label=None):
    """Present a copyable report line directly below its measurement."""
    if value is None:
        st.caption(reference_text)
        return
    line=f'{title}: {value:g} mm ({reference_text})'
    st.code(line,language=None)

def pair_reference_line(title, right, left, reference_text):
    if right is None and left is None:
        st.caption(reference_text)
        return
    r=f'{right:g}' if right is not None else '—'
    l=f'{left:g}' if left is not None else '—'
    line=f'{title}: Rt {r} mm, Lt {l} mm ({reference_text})'
    st.code(line,language=None)

with digestive:
    st.subheader('소화기계 계측')
    st.caption('단위: mm. 95% CI는 평균에 대한 신뢰구간이며 개별 태아의 정상범위가 아닙니다.')
    with st.container(border=True):
        st.markdown('**Stomach axial diameter**')
        stomach=number('Stomach axial diameter','stomach')
        row=get_ref(STOMACH)
        if row is None:
            st.caption('참고치 범위: 14–40주. 공통 임신 주수를 입력해 주세요.')
        else:
            reference_line('Stomach axial diameter',stomach,f'Ref. {ga_ref} 5th percentile: {row[2]:.1f} mm; 95th percentile: {row[8]:.1f} mm')
            extra_source('STOMACH')
    with st.container(border=True):
        st.markdown('**Small bowel diameter**')
        small_bowel=number('Small bowel diameter','small_bowel')
        row=get_ref(SMALL_BOWEL_COLON)
        if row is None:
            st.caption('참고치 범위: 20–40주.')
        else:
            reference_line('Small bowel diameter',small_bowel,f'Ref. {ga_ref} upper 95% prediction limit: {row[2]:.1f} mm')
            st.caption(f'Mean: {row[0]:.1f} mm | 95% prediction interval: {row[1]:.1f}–{row[2]:.1f} mm')
            extra_source('SMALL_BOWEL_COLON')
    with st.container(border=True):
        st.markdown('**Colon diameter**')
        colon=number('Colon diameter','colon')
        row=get_ref(SMALL_BOWEL_COLON)
        if row is None:
            st.caption('참고치 범위: 20–40주.')
        else:
            if row[5] is None:
                st.caption(f'{ga_ref}: 원표의 20주 colon 95% prediction interval 값이 평균과 모순되어 참고치 출력을 보류했습니다.')
                if colon is not None:
                    text=f'Colon diameter: {colon:g} mm (Ref. {ga_ref} mean: {row[3]:.1f} mm; prediction limit pending verification)'
                    st.code(text,language=None)
            else:
                reference_line('Colon diameter',colon,f'Ref. {ga_ref} upper 95% prediction limit: {row[5]:.1f} mm')
                st.caption(f'Mean: {row[3]:.1f} mm | 95% prediction interval: {row[4]:.1f}–{row[5]:.1f} mm')
            extra_source('SMALL_BOWEL_COLON')
    with st.container(border=True):
        st.markdown('**Descending colon diameter**')
        descending_colon=number('Descending colon diameter','descending_colon')
        row=get_ref(DESCENDING_RECTUM)
        if row is None:
            st.caption('참고치 범위: 19–40주.')
        else:
            reference_line('Descending colon diameter',descending_colon,f'Ref. {ga_ref} mean: {row[0]:.2f} mm; 95% CI: {row[1]:.2f}–{row[2]:.2f} mm')
            extra_source('DESCENDING_RECTUM')
    with st.container(border=True):
        st.markdown('**Rectal diameter**')
        rectum=number('Rectal diameter','rectum')
        row=get_ref(DESCENDING_RECTUM)
        if row is None:
            st.caption('참고치 범위: 19–40주.')
        elif row[4] is None:
            st.caption('40주 rectal 95% CI 하한은 원표의 오기 가능성이 있어 표시하지 않습니다.')
            if rectum is not None:
                text=f'Rectal diameter: {rectum:g} mm (Ref. {ga_ref} mean: {row[3]:.2f} mm; CI pending verification)'
                st.code(text,language=None)
        else:
            reference_line('Rectal diameter',rectum,f'Ref. {ga_ref} mean: {row[3]:.2f} mm; 95% CI: {row[4]:.2f}–{row[5]:.2f} mm')
        if row is not None:
            extra_source('DESCENDING_RECTUM')

with face:
    st.subheader('얼굴 계측')
    with st.container(border=True):
        st.markdown('**Nasal bone length**')
        nasal_bone=number('Nasal bone length','nasal_bone')
        row=get_ref(NASAL_BONE)
        if row is None:
            st.caption('참고치 범위: 11–40주.')
        else:
            reference_line('Nasal bone length',nasal_bone,f'Ref. {ga_ref} 5th percentile: {row[1]:.1f} mm')
            extra_source('NASAL_BONE')
    with st.container(border=True):
        st.markdown('**Ear length**')
        c1,c2=st.columns(2)
        with c1: ear_rt=number('Ear length Rt','ear_rt')
        with c2: ear_lt=number('Ear length Lt','ear_lt')
        row=get_ref(EAR_LENGTH)
        if row is None:
            st.caption('참고치 범위: 15–40주.')
        else:
            pair_reference_line('Ear length',ear_rt,ear_lt,f'Ref. {ga_ref} 5th percentile: {row[0]:.1f} mm')
            extra_source('EAR_LENGTH')

with refs:
    st.subheader('임신 주수별 참고치')
    st.caption('임신 주수(Weeks, Days)를 입력하면 해당 주수의 참고치를 조회합니다. 주+일은 인접 주수 간 선형보간한 값입니다.')
    with st.container(border=True):
        st.markdown('**EFW (g)**')
        group=st.selectbox('임신 형태',('Singleton (NICHD Asian)','DC twin (Ananth 1998)','MC twin (Ananth 1998)'),key='efw_group')
        if group.startswith('Singleton'):
            t,ps,refname=EFW_SINGLE,[3,5,10,50,90,95,97],'EFW_SINGLE'
        elif group.startswith('DC'):
            t,ps,refname=EFW_DC,[5,10,50,90,95],'EFW_DC'
        else:
            t,ps,refname=EFW_MC,[5,10,50,90,95],'EFW_MC'
        row=get_ref(t)

        def efw_result(label, efw):
            """Print the copyable result directly after its own EFW input."""
            if efw is None:
                return
            if row is None:
                st.caption(f'{label}: {efw:g} g — 주수별 참고치 범위: {min(t)}–{max(t)}주')
                return
            band=percentile_band(efw,ps,row)
            closest=nearest_reference_percentile(efw,ps,row)
            size=median_equivalent_ga(efw,t)
            size_text=f'{size[0]}w{size[1]}d size' if size is not None else 'size unavailable'
            if closest is not None:
                pct,ref_g=closest
                suffix='rd' if pct==3 else 'th'
                st.code(f'{label}: {efw:g} g, {size_text} (Ref. {ga_ref} {pct}{suffix} percentile: {ref_g:.0f} g)',language=None)
                st.caption(f'Percentile interval: {band} · size는 P50 기준 추정 주수')
            else:
                st.code(f'{label}: {efw:g} g, {size_text} (Ref. unavailable)',language=None)

        if group.startswith('Singleton'):
            efw=number('EFW','efw','g')
            efw_result('EFW',efw)
        else:
            c1,c2=st.columns(2)
            with c1:
                efw_a=number('Twin A EFW','efw_a','g')
                efw_result('Twin A EFW',efw_a)
            with c2:
                efw_b=number('Twin B EFW','efw_b','g')
                efw_result('Twin B EFW',efw_b)
            if efw_a is not None and efw_b is not None:
                discordance=abs(efw_a-efw_b)/max(efw_a,efw_b)*100
                st.code(f'EFW discordance: {discordance:.1f}%',language=None)
        if row is not None:
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
            if kidney is not None:
                st.code(f'Kidney length: {kidney:g} mm (Ref. {ga_ref} 5th percentile: {p5:.1f} mm; 95th percentile: {p95:.1f} mm)',language=None)
            else:
                st.caption(text.replace(chr(10),' | '))
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
            if afi is not None:
                st.code(f'AFI: {afi:g} mm (Ref. {ga_ref} 5th percentile: {row[1]:.1f} mm; 95th percentile: {row[3]:.1f} mm)',language=None)
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
            text=f'Ref. {ga_ref} lower limit of 95% reference range: {lower:.1f} mm'
            if thymus is not None:
                st.code(f'Thymic diameter: {thymus:g} mm ({text})',language=None)
            else:
                st.caption(text)
            st.caption(f'Mean: {mean:.1f} mm | Upper limit: {upper:.1f} mm')
            ref_caption('THYMUS_CM')

