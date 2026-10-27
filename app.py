from __future__ import annotations
import math
import streamlit as st


# ===== Bundled calculations.py =====
import math


def _valid(*values: float) -> None:
    if not values or any(not math.isfinite(x) or x <= 0 for x in values):
        raise ValueError("측정값은 모두 0보다 큰 유한한 숫자여야 합니다.")


def ratio(numerator: float, denominator: float) -> float:
    _valid(numerator, denominator)
    return numerator / denominator


def fl_foot(fl_mm: float, foot_mm: float) -> float:
    return ratio(fl_mm, foot_mm)


def fl_ac(fl_mm: float, ac_mm: float) -> float:
    return ratio(fl_mm, ac_mm)


def tc_ac(tc_mm: float, ac_mm: float) -> float:
    return ratio(tc_mm, ac_mm)


def plas_index(posterior_la_to_dao_mm: float, dao_diameter_mm: float) -> float:
    return ratio(posterior_la_to_dao_mm, dao_diameter_mm)


def gose_ratio(ra_area_cm2: float, atrialized_rv_area_cm2: float,
               functional_rv_area_cm2: float, la_area_cm2: float,
               lv_area_cm2: float) -> float:
    """Celermajer/GOSE area ratio (RA + atrialized RV)/(functional RV + LA + LV)."""
    _valid(ra_area_cm2, atrialized_rv_area_cm2, functional_rv_area_cm2,
           la_area_cm2, lv_area_cm2)
    return (ra_area_cm2 + atrialized_rv_area_cm2) / (
        functional_rv_area_cm2 + la_area_cm2 + lv_area_cm2)


# ===== Bundled reference_calc.py =====
import math


def at_ga(table: dict, weeks: int, days: int):
    """Linear interpolation between nearest published GA knots; never extrapolate.

    Supports both weekly and alternate-week tables. None cells remain unavailable.
    """
    if not 0 <= days <= 6:
        raise ValueError('days must be 0–6')
    ga = weeks + days / 7
    knots = sorted(table)
    if not knots or ga < knots[0] or ga > knots[-1]:
        return None
    if days == 0 and weeks in table:
        return table[weeks]
    lower = max((w for w in knots if w <= ga), default=None)
    upper = min((w for w in knots if w >= ga), default=None)
    if lower is None or upper is None:
        return None
    if lower == upper:
        return table[lower]
    weight = (ga - lower) / (upper - lower)
    a, b = table[lower], table[upper]
    return [None if x is None or y is None else x + (y - x) * weight for x,y in zip(a,b)]


def percentile_band(value: float, percentiles: list[int], reference: list[float | None]):
    """Return only a percentile *interval*, never a fabricated exact percentile."""
    if not math.isfinite(value) or value <= 0:
        raise ValueError('Invalid measurement')
    valid = [(p, v) for p,v in zip(percentiles, reference) if v is not None]
    if not valid:
        return 'Reference unavailable'
    if value < valid[0][1]:
        return f'< P{valid[0][0]}'
    for (p0,v0),(p1,v1) in zip(valid, valid[1:]):
        if value == v0:
            return f'P{p0}'
        if value < v1:
            return f'P{p0}–P{p1}'
    if value == valid[-1][1]:
        return f'P{valid[-1][0]}'
    return f'> P{valid[-1][0]}'


def gose_grade(ratio: float) -> int:
    """Celermajer/GOSE area ratio grades; 1.5 allocated to Grade 4."""
    if not math.isfinite(ratio) or ratio <= 0:
        raise ValueError('Invalid GOSE ratio')
    if ratio < .5: return 1
    if ratio < 1.0: return 2
    if ratio < 1.5: return 3
    return 4


def nearest_reference_percentile(value, percentiles, reference):
    """Nearest published percentile knot; never pretend this is an exact percentile."""
    valid=[(p,v) for p,v in zip(percentiles,reference) if v is not None]
    return min(valid,key=lambda pair: abs(pair[1]-value)) if valid else None

def median_equivalent_ga(weight_g, table):
    """Interpolate GA using P50 weight curve; return completed weeks and days."""
    points=sorted((w, row[len(row)//2]) for w,row in table.items() if row[len(row)//2] is not None)
    if not points or weight_g < points[0][1] or weight_g > points[-1][1]:
        return None
    for (w0,v0),(w1,v1) in zip(points,points[1:]):
        if v0 <= weight_g <= v1 and v1 > v0:
            total_days=round((w0+(weight_g-v0)/(v1-v0)*(w1-w0))*7)
            return divmod(total_days,7)
    if weight_g == points[-1][1]: return points[-1][0],0
    return None


# ===== Bundled reference_data.py =====

# Singleton EFW (g): NICHD Fetal Growth Studies, Asian cohort; P3, P5, P10, P50, P90, P95, P97.
# Source photo contains an apparent typographic error at GA 21 P97 ('380' < P95 467);
# this cell is withheld rather than silently corrected.
EFW_SINGLE = {
10:[18,19,20,24,30,31,33],11:[26,27,28,34,41,43,44],12:[36,38,39,47,55,58,60],
13:[50,51,53,63,74,77,79],14:[66,68,71,83,97,101,104],15:[86,88,92,108,125,131,135],
16:[110,113,118,138,160,167,172],17:[139,143,149,173,202,211,216],18:[172,177,185,215,250,261,269],
19:[211,217,227,264,307,321,330],20:[257,264,275,320,373,389,400],21:[308,317,331,385,447,467,None],
22:[367,378,394,458,532,556,571],23:[434,446,466,541,628,656,674],24:[509,524,546,634,737,769,790],
25:[594,611,637,740,859,896,921],26:[690,709,740,859,997,1040,1069],27:[796,818,853,990,1149,1199,1232],
28:[913,938,978,1136,1318,1375,1413],29:[1039,1068,1114,1293,1501,1566,1609],
30:[1175,1208,1260,1463,1698,1772,1821],31:[1318,1355,1414,1642,1908,1991,2047],
32:[1467,1508,1574,1830,2129,2222,2284],33:[1620,1667,1740,2026,2360,2464,2534],
34:[1778,1829,1911,2229,2600,2717,2795],35:[1938,1995,2085,2438,2851,2980,3067],
36:[2100,2162,2262,2653,3111,3255,3352],37:[2259,2327,2437,2869,3376,3536,3644],
38:[2408,2483,2604,3077,3637,3814,3933],39:[2539,2621,2752,3269,3884,4078,4210],
40:[2643,2731,2873,3434,4105,4318,4462],
}
# Ananth et al 1998, smoothed birth weight percentiles (g) for twins: P5 P10 P50 P90 P95.
EFW_DC = {
23:[477,513,632,757,801],24:[538,578,712,853,903],25:[606,652,803,962,1018],
26:[684,735,906,1085,1148],27:[771,829,1021,1223,1294],28:[870,935,1152,1379,1459],
29:[980,1054,1298,1554,1645],30:[1102,1186,1460,1748,1850],31:[1235,1328,1635,1958,2072],
32:[1374,1477,1819,2179,2306],33:[1515,1630,2007,2403,2543],34:[1653,1778,2190,2622,2775],
35:[1781,1916,2359,2825,2989],36:[1892,2035,2506,3001,3176],37:[1989,2139,2634,3155,3339],
38:[2079,2236,2753,3297,3489],39:[2167,2331,2870,3437,3637],40:[2258,2428,2990,3581,3790],
41:[2352,2530,3115,3731,3948],
}
EFW_MC = {
23:[392,431,533,648,683],24:[456,501,620,758,794],25:[530,582,720,875,922],
26:[615,676,836,1017,1072],27:[713,784,970,1178,1242],28:[823,904,1119,1360,1433],
29:[944,1037,1282,1559,1643],30:[1072,1178,1457,1771,1867],31:[1204,1323,1637,1990,2097],
32:[1335,1467,1814,2205,2325],33:[1457,1601,1980,2407,2537],34:[1562,1716,2123,2580,2720],
35:[1646,1808,2237,2719,2866],36:[1728,1899,2349,2855,3009],37:[1831,2012,2489,3025,3189],
38:[1957,2150,2660,3233,3408],39:[2100,2307,2854,3469,3657],40:[2255,2478,3065,3726,3927],
41:[2422,2661,3292,4001,4217],
}
# Moore & Cayle 1990, AFI (mm) P3 P5 P50 P95 P97
AFI = {
16:[73,79,121,185,201],17:[77,83,127,194,211],18:[80,87,133,202,220],
19:[83,90,137,207,225],20:[86,93,141,212,230],21:[88,95,143,214,233],
22:[89,97,145,216,235],23:[90,98,146,218,237],24:[90,98,147,219,238],
25:[89,97,147,221,240],26:[89,97,147,223,242],27:[85,95,146,226,245],
28:[86,94,146,228,249],29:[84,92,145,231,254],30:[82,90,145,234,258],
31:[79,88,144,238,263],32:[77,86,144,242,269],33:[74,83,143,245,274],
34:[72,81,142,248,278],35:[70,79,140,249,279],36:[68,77,138,249,279],
37:[66,75,135,244,275],38:[65,73,132,239,269],39:[64,72,127,226,255],
40:[63,71,123,214,240],41:[63,70,116,194,216],42:[63,69,110,175,192],
}
# Foot length in cm P5 P10 P50 P90 P95, from photo, Meriowitz/Ananth/Smulian J Ultrasound Med 2000
FOOT_CM = {
15:[1.4,1.5,1.8,2.2,2.3],16:[1.6,1.7,2.1,2.5,2.6],17:[1.9,2.0,2.4,2.8,2.9],
18:[2.2,2.3,2.7,3.1,3.2],19:[2.5,2.6,3.0,3.3,3.4],20:[2.8,2.9,3.2,3.6,3.7],
21:[3.1,3.2,3.5,3.9,4.0],22:[3.4,3.5,3.9,4.2,4.3],23:[3.7,3.8,4.2,4.6,4.7],
24:[4.0,4.1,4.5,4.9,5.0],25:[4.3,4.4,4.8,5.1,5.2],26:[4.6,4.7,5.1,5.4,5.5],
27:[4.8,4.9,5.3,5.7,5.8],28:[5.1,5.2,5.6,5.9,6.0],29:[5.3,5.4,5.8,6.2,6.3],
30:[5.6,5.7,6.1,6.4,6.5],31:[5.8,5.9,6.3,6.7,6.8],32:[6.0,6.1,6.5,6.9,7.0],
33:[6.3,6.4,6.8,7.1,7.2],34:[6.5,6.6,7.0,7.4,7.5],35:[6.8,6.9,7.3,7.6,7.7],
36:[7.0,7.1,7.5,7.9,8.0],37:[7.3,7.4,7.7,8.1,8.2],
}
# UOG 2007 29:634-638, thymic diameter cm: mean and lower/upper 95% reference limits.
# The lower bound is NOT a published fifth percentile.
THYMUS_CM = {
19:[1.2,0.6,1.8],20:[1.4,0.7,2.0],21:[1.5,0.9,2.1],22:[1.6,1.0,2.3],
23:[1.8,1.2,2.4],24:[1.9,1.3,2.6],25:[2.1,1.5,2.7],26:[2.2,1.6,2.9],
27:[2.4,1.8,3.0],28:[2.5,1.9,3.2],29:[2.7,2.0,3.3],30:[2.8,2.2,3.5],
31:[3.0,2.3,3.6],32:[3.1,2.5,3.7],33:[3.3,2.6,3.9],34:[3.4,2.8,4.0],
35:[3.6,2.9,4.2],36:[3.7,3.1,4.3],37:[3.9,3.2,4.5],38:[4.0,3.4,4.6],
}
# Kidney length (mm): P5 P50 P95; GA 16-41, Table S2 from source photo.
KIDNEY_MM = {
16:[11.5,14.2,17.0],17:[12.9,15.7,18.4],18:[14.3,17.1,19.9],19:[15.7,18.5,21.3],
20:[17.1,19.9,22.7],21:[18.4,21.3,24.1],22:[19.7,22.6,25.6],23:[21.0,24.0,27.0],
24:[22.3,25.3,28.4],25:[23.5,26.6,29.8],26:[24.7,27.9,31.1],27:[25.9,29.2,32.5],
28:[27.1,30.5,33.9],29:[28.3,31.7,35.2],30:[29.4,33.0,36.5],31:[30.5,34.2,37.9],
32:[31.6,35.4,39.2],33:[32.7,36.6,40.5],34:[33.8,37.8,41.7],35:[34.8,38.9,43.0],
36:[35.9,40.1,44.3],37:[36.9,41.2,45.5],38:[37.9,42.3,46.8],39:[38.9,43.4,48.0],
40:[39.8,44.5,49.2],41:[40.7,45.5,50.4],
}

REFERENCE_INFO = {
'EFW_SINGLE':'NICHD Fetal Growth Studies, Asian-specific fetal anthropometric percentiles (Table B-I).',
'EFW_DC':'Ananth et al. (1998), smoothed birthweight percentiles for dichorionic twins (Table III-3).',
'EFW_MC':'Ananth et al. (1998), smoothed birthweight percentiles for monochorionic twins (Table III-4).',
'AFI':'Moore & Cayle (1990), Am J Obstet Gynecol 162:1168, Table C-1.',
'FOOT_CM':'Meriowitz/Ananth/Smulian et al., Foot length in fetuses with abnormal growth, J Ultrasound Med 19:201 (2000), Table A-23; bibliographic spelling to verify.',
'THYMUS_CM':'Ultrasound in Obstetrics & Gynecology (2007) 29:634–638, predicted fetal thymic diameter 95% reference range (Table 2).',
'KIDNEY_MM':'Fitted centiles of fetal kidney length (Table S2, GA 16–41); full paper bibliographic details pending.',
}


# ===== Bundled reference_extra.py =====
# UOG 2003;21:161-164: GA: [mean descending colon, CI lower, CI upper, mean rectum, CI lower, CI upper], mm.
# 19-20 weeks are a single reported band, used unchanged for weeks 19 and 20.
DESCENDING_RECTUM = {
19:[3.52,.79,6.26,3.64,1.45,5.82],20:[3.52,.79,6.26,3.64,1.45,5.82],
21:[3.59,.86,6.32,3.79,1.61,5.97],22:[3.59,.96,6.41,3.95,1.78,6.13],
23:[3.82,1.09,6.54,4.14,1.97,6.31],24:[3.98,1.26,6.70,4.34,2.17,6.52],
25:[4.18,1.46,6.90,4.57,2.40,6.74],26:[4.43,1.70,7.15,4.82,2.64,6.99],
27:[4.71,1.99,7.43,5.08,2.91,7.26],28:[5.04,2.32,7.76,5.38,3.20,7.55],
29:[5.42,2.69,8.14,5.69,3.52,7.87],30:[5.84,3.12,8.57,6.04,3.86,8.21],
31:[6.32,3.60,9.05,6.41,4.23,8.58],32:[6.86,4.13,9.58,6.80,4.63,8.98],
33:[7.45,4.72,10.17,7.23,5.05,9.40],34:[8.10,5.37,10.82,7.68,5.51,9.85],
35:[8.81,6.09,11.53,8.17,5.99,10.34],36:[9.59,6.87,12.31,8.68,6.51,10.85],
37:[10.44,7.71,13.16,9.23,7.06,11.40],38:[11.35,8.63,14.08,9.81,7.64,11.98],
39:[12.34,9.61,15.07,10.43,8.25,12.61],40:[13.40,10.66,16.15,11.08,2.89,13.26],
}
# 40-week rectal CI lower 2.89 is as photographed but unusually low; withhold until checked.
DESCENDING_RECTUM[40][4] = None

# Lap et al., Reference curves for the normal fetal small bowel and colon diameters.
# GA: [small bowel mean, PI low, PI high, colon mean, PI low, PI high], mm.
SMALL_BOWEL_COLON = {
20:[1.7,.4,3.5,1.8,None,None], # 20wk colon 0.0-0.4 in image conflicts with mean 1.8: withhold interval
22:[2.1,.7,3.9,2.9,.8,5.5],24:[2.4,.9,4.3,3.9,1.5,6.7],
26:[2.7,1.2,4.7,4.8,2.2,7.8],28:[3.1,1.4,5.1,5.7,3.0,8.8],
30:[3.4,1.7,5.5,6.6,3.7,9.8],32:[3.8,2.0,5.9,7.7,4.6,11.0],
34:[4.1,2.2,6.3,8.9,5.6,12.5],36:[4.4,2.5,6.7,10.4,6.8,14.3],
38:[4.8,2.8,7.1,12.3,8.2,16.5],40:[5.1,3.0,7.6,14.5,9.8,19.4],
}
# Kassif et al., stomach axial diameter modelled centiles, GA: P1 P3 P5 P10 P25 P50 P75 P90 P95 P97 P99 (mm)
STOMACH = {
14:[2.1,2.7,3.0,3.5,4.3,5.2,6.1,6.9,7.3,7.6,8.2],
15:[2.7,3.3,3.6,4.1,5.0,5.9,6.8,7.7,8.2,8.5,9.1],
16:[3.2,3.9,4.2,4.7,5.6,6.6,7.6,8.5,9.0,9.4,10.1],
17:[3.6,4.3,4.7,5.3,6.3,7.3,8.4,9.4,10.0,10.3,11.1],
18:[4.0,4.8,5.2,5.8,6.9,8.1,9.2,10.3,10.9,11.3,12.2],
19:[4.3,5.2,5.6,6.3,7.5,8.8,10.1,11.2,11.9,12.4,13.3],
20:[4.4,5.3,6.0,6.8,8.1,9.5,10.9,12.2,13.0,13.6,14.4],
21:[4.6,5.6,6.4,7.2,8.6,10.2,11.8,13.2,14.0,14.7,15.6],
22:[4.8,5.9,6.7,7.6,9.2,10.9,12.6,14.1,15.1,15.9,16.8],
23:[4.9,6.2,7.0,8.0,9.7,11.6,13.4,15.1,16.1,17.0,18.0],
24:[5.1,6.4,7.3,8.4,10.2,12.2,14.2,16.1,17.1,18.1,19.2],
25:[5.2,6.6,7.6,8.8,10.7,12.9,15.1,17.0,18.2,19.2,20.4],
26:[5.3,6.9,7.9,9.2,11.2,13.5,15.8,17.9,19.2,20.2,21.5],
27:[5.5,7.1,8.2,9.6,11.7,14.2,16.6,18.8,20.1,21.2,22.6],
28:[5.7,7.4,8.6,9.9,12.2,14.8,17.3,19.6,21.0,22.2,23.7],
29:[5.9,7.7,8.9,10.3,12.7,15.4,18.0,20.4,21.9,23.1,24.8],
30:[6.1,8.0,9.2,10.7,13.2,16.0,18.7,21.2,22.7,24.0,25.5],
31:[6.4,8.3,9.6,11.1,13.7,16.5,19.3,21.9,23.4,24.7,26.3],
32:[6.8,8.7,10.0,11.6,14.2,17.0,19.9,22.5,24.0,25.4,27.0],
33:[7.2,9.1,10.5,12.0,14.6,17.5,20.4,23.1,24.6,26.0,27.6],
34:[7.7,9.6,11.0,12.5,15.1,18.0,20.9,23.5,25.1,26.4,28.1],
35:[8.3,10.2,11.5,13.0,15.6,18.5,21.3,23.9,25.4,26.8,28.4],
36:[8.9,10.8,12.1,13.6,16.1,18.9,21.7,24.2,25.7,27.0,28.6],
37:[9.7,11.5,12.7,14.2,16.6,19.3,22.0,24.4,25.8,27.1,28.6],
38:[10.6,12.3,13.5,14.8,17.1,19.6,22.2,24.5,25.8,27.0,28.4],
39:[11.6,13.1,14.2,15.5,17.6,20.0,22.3,24.4,25.7,26.8,28.1],
40:[12.7,14.1,15.1,16.2,18.1,20.2,22.4,24.3,25.4,26.4,27.6],
}
# Sonek et al., nasal bone lengths from 3537 fetal US measurements; P2.5 P5 P50 P95 P97.5 (mm)
NASAL_BONE = {
11:[1.3,1.4,2.3,3.3,3.4],12:[1.7,1.8,2.8,4.2,4.3],13:[2.2,2.3,3.1,4.6,4.8],
14:[2.2,2.5,3.8,5.3,5.7],15:[2.8,3.0,4.3,5.7,6.0],16:[3.2,3.4,4.7,6.2,6.2],
17:[3.7,4.0,5.3,6.6,6.9],18:[4.0,4.3,5.7,7.0,7.3],19:[4.6,5.0,6.3,7.9,8.2],
20:[5.0,5.2,6.7,8.3,8.6],21:[5.1,5.6,7.1,9.0,9.3],22:[5.6,5.8,7.5,9.3,10.2],
23:[6.0,6.4,7.9,9.6,9.9],24:[6.6,6.8,9.3,10.0,10.3],25:[6.3,6.5,8.5,10.7,10.8],
26:[6.8,7.4,8.9,10.9,11.3],27:[7.0,7.5,9.2,11.3,11.6],28:[7.2,7.6,9.8,12.1,13.4],
29:[7.2,7.7,9.8,11.8,12.3],30:[7.3,7.9,10.0,12.6,13.2],31:[7.9,8.2,10.4,12.6,13.2],
32:[8.1,8.6,10.5,13.6,13.7],33:[8.6,8.7,10.8,12.8,13.0],34:[9.0,9.1,10.9,12.8,13.5],
35:[7.5,8.5,11.0,14.1,15.0],36:[7.3,7.8,10.8,12.8,13.6],37:[8.4,8.7,11.4,14.5,15.0],
38:[9.2,9.3,11.7,15.7,16.6],39:[9.1,9.2,10.9,14.0,14.8],40:[10.3,10.4,12.1,14.5,14.7],
}
# Chitkara et al., ultrasonographic ear length: P5 P10 P50 P90 P95 (mm)
EAR_LENGTH = {
15:[6.7,7.0,8.5,10.4,10.4],16:[8.2,8.5,10.0,11.2,11.6],17:[8.6,9.0,10.6,12.3,12.9],
18:[9.0,9.8,11.7,13.7,14.3],19:[10.6,11.2,12.9,15.1,15.5],20:[11.5,12.3,14.3,16.4,17.3],
21:[12.2,13.2,15.3,17.4,18.1],22:[13.2,14.2,16.7,18.6,18.9],23:[14.0,14.9,18.1,20.6,21.6],
24:[15.3,15.8,19.7,21.9,22.3],25:[15.7,16.8,21.4,24.2,24.5],26:[16.6,16.8,21.2,23.8,24.2],
27:[19.4,19.6,22.5,26.4,27.8],28:[17.6,19.9,24.4,30.1,31.9],29:[18.7,20.0,25.3,28.2,28.5],
30:[18.3,20.7,25.1,27.9,31.6],31:[21.4,21.9,26.7,29.8,31.2],32:[25.3,25.8,28.1,31.1,33.0],
33:[21.4,23.5,28.6,32.4,32.9],34:[22.7,26.9,29.2,33.3,34.0],35:[23.0,26.7,31.2,33.7,35.0],
36:[23.9,27.5,31.1,33.3,34.5],37:[27.3,28.1,31.9,35.6,36.4],38:[24.8,25.6,32.2,36.9,38.7],
39:[26.2,27.7,33.3,36.2,37.5],40:[28.1,29.3,32.6,35.7,37.6],
}
EXTRA_SOURCES = {
 'DESCENDING_RECTUM':'Fetal colon and rectal development, Ultrasound Obstet Gynecol 2003;21:161–164, Table 1 (95% confidence interval of the mean).',
 'SMALL_BOWEL_COLON':'Lap CC et al. Reference curves for the normal fetal small bowel and colon diameters; Table 1 (95% prediction interval).',
 'STOMACH':'Kassif et al. Stomach axial diameter modelled centiles, Table 2 (P5 and P95). Full bibliographic citation to verify.',
 'NASAL_BONE':'Sonek JD et al. Nasal bone length throughout gestation: normal ranges based on 3537 fetal ultrasound measurements, Table G-2.',
 'EAR_LENGTH':'Chitkara U et al. Ultrasonographic ear length measurement in normal second- and third-trimester fetuses, Table II.',
}



# Doppler reference points transcribed from the user-provided reference photographs.
# UA tuple: RI P5, S/D P5, RI P50, S/D P50, RI P95, S/D P95.
# MCA table: P50 PSV (cm/s), GA 15–40 weeks. The photo's 19-week 1.3-MoM
# entry appears truncated, so only the unaffected P50 values are used.
UMB_DOPPLER = {16: (0.7, 3.39, 0.8, 5.12, 0.9, 10.5), 17: (0.69, 3.27, 0.79, 4.86, 0.89, 9.46), 18: (0.68, 3.16, 0.78, 4.63, 0.88, 8.61), 19: (0.67, 3.06, 0.77, 4.41, 0.87, 7.9), 20: (0.67, 2.97, 0.76, 4.22, 0.86, 7.3), 21: (0.65, 2.88, 0.75, 4.04, 0.85, 6.78), 22: (0.64, 2.79, 0.74, 3.88, 0.84, 6.3), 23: (0.63, 2.71, 0.73, 3.73, 0.83, 5.94), 24: (0.62, 2.64, 0.72, 3.59, 0.82, 5.59), 25: (0.61, 2.57, 0.71, 3.46, 0.81, 5.28), 26: (0.6, 2.5, 0.7, 3.34, 0.8, 5.01), 27: (0.59, 2.44, 0.69, 3.22, 0.79, 4.76), 28: (0.58, 2.38, 0.68, 3.12, 0.78, 4.53), 29: (0.57, 2.32, 0.67, 3.02, 0.77, 4.33), 30: (0.56, 2.26, 0.67, 2.93, 0.76, 4.14), 31: (0.55, 2.21, 0.65, 2.84, 0.75, 3.97), 32: (0.54, 2.16, 0.64, 2.76, 0.74, 3.81), 33: (0.53, 2.11, 0.63, 2.68, 0.73, 3.67), 34: (0.52, 2.07, 0.62, 2.61, 0.72, 3.53), 35: (0.51, 2.03, 0.61, 2.54, 0.71, 3.4), 36: (0.5, 1.98, 0.6, 2.47, 0.7, 3.29), 37: (0.49, 1.94, 0.59, 2.41, 0.69, 3.18), 38: (0.47, 1.9, 0.57, 2.35, 0.67, 3.08), 39: (0.46, 1.87, 0.56, 2.3, 0.67, 2.98), 40: (0.45, 1.83, 0.55, 2.24, 0.65, 2.89), 41: (0.44, 1.8, 0.54, 2.19, 0.64, 2.81), 42: (0.43, 1.76, 0.53, 2.14, 0.63, 2.73)}
MCA_PSV_MEDIAN = {15: [20], 16: [21], 17: [22], 18: [23], 19: [24], 20: [25], 21: [26], 22: [28], 23: [29], 24: [30], 25: [32], 26: [33], 27: [35], 28: [37], 29: [38], 30: [40], 31: [42], 32: [44], 33: [46], 34: [48], 35: [50], 36: [53], 37: [55], 38: [58], 39: [61], 40: [63]}

def estimated_ua_percentile(value, p5, p50, p95):
    # Piecewise interpolation within tabulated percentile anchors only.
    if value < p5: return '<5th'
    if value == p5: return '5th'
    if value < p50: return f'est. {5 + 45*(value-p5)/(p50-p5):.0f}th'
    if value == p50: return '50th'
    if value < p95: return f'est. {50 + 45*(value-p50)/(p95-p50):.0f}th'
    if value == p95: return '95th'
    return '>95th'

def mca_mom_band(mom):
    for lo,hi in [(1.0,1.3),(1.3,1.5),(1.5,1.7),(1.7,2.0)]:
        if lo <= mom < hi: return f'{lo:.1f}–{hi:.1f} MoM'
    return '<1.0 MoM' if mom < 1.0 else '≥2.0 MoM'

def expected_lhr(method, model, ga, lesion_side):
    # Expected LHR equations published by Perinatology.com; GA in decimal weeks.
    # No unsupported model/side combinations are extrapolated.
    if lesion_side == 'Left CDH':
        coeffs = {
          ('Longest','Jani'):(-3.4802,.3995,-.0048),
          ('Longest','Dekoninck'):(-3.480,.399,-.004),
          ('Trace','Jani'):(-2.3271,.27,-.0032),
          ('Trace','Dekoninck'):(-2.356,.272,-.003),
          ('Trace','Peralta'):(-2.2481,.2712,-.0033),
        }
    else:
        coeffs = {
          ('Longest','Jani'):(-2.5957,.3043,-.0042),
          ('Trace','Jani'):(-1.4994,.1778,-.0021),
          ('Trace','Peralta'):(-1.4815,.1824,-.0023),
        }
    coeff=coeffs.get((method,model))
    if coeff is None: return None
    a,b,c=coeff
    val=a+b*ga+c*ga*ga
    return val if val>0 else None

def oe_lhr(lung_area_cm2, hc_cm, ga, side, method, model):
    expected=expected_lhr(method,model,ga,side)
    if expected is None: return None
    # Published LHR = area in mm² / HC in mm; cm inputs are converted.
    observed=lung_area_cm2*10/hc_cm
    return observed/expected*100

# ===== Streamlit application =====
import math
import streamlit as st

st.set_page_config(page_title='Fetal Quick Calculator', page_icon='📐', layout='wide')
st.markdown('<style>.block-container{max-width:1100px;padding-top:1.5rem}</style>', unsafe_allow_html=True)

INPUT_KEYS = ('rv','lv','ra','la','plas_dist','dao',
              'g_ra','g_arv','g_frv','g_la','g_lv','card_circ','thor_circ','card_area','thor_area','fl','foot_rt','foot_lt','ac','tc',
              'kidney_rt','kidney_lt','efw','efw_a','efw_b','afi','thymus',
              'descending_colon','rectum','small_bowel','colon','stomach',
              'nasal_bone','ear_rt','ear_lt','cdh_hc','cdh_lung1','cdh_lung2','cdh_trace','cdh_total_longest','cdh_total_trace','ua_sd','ua_ri','mca_psv')

def reset_inputs():
    for key in INPUT_KEYS:
        st.session_state[key] = ''
    # 임신 주수 및 EFW 유형은 유지하고 측정값만 초기화합니다.

def number(label, key, unit='cm'):
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
    st.caption('심장 · CDH · 근골격 · 소화·비뇨 · 얼굴 · 태아성장·양수·도플러')
with c2:
    st.button('↺ 전체 수치 리셋',on_click=reset_inputs,use_container_width=True)

st.markdown('**임신 주수**')
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


heart, cdh, musculo, digestive, face, refs=st.tabs(['🫀 심장','🫁 CDH','🦴 근골격','🩺 소화·비뇨','👶 얼굴','📈 태아성장·양수·도플러'])
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
            st.code(f'CTAR: {ratio(card_area,thor_area):.2f}',language=None)
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
        st.code(f'GOSE Score: {val:.2f} (Grade {grade})',language=None)
    st.divider()
    st.markdown('**PLAS Index (TAPVR 관련)**')
    c1,c2=st.columns(2)
    with c1: dist=number('Post-LA distance','plas_dist')
    with c2: dao=number('Descending aorta diameter','dao')
    if dist is not None and dao is not None:
        val=plas_index(dist,dao)
        st.code(f'PLAS Index: {val:.2f} (Ref. normal mean: 0.62 ± 0.19; TAPVC screening cutoff: ≥1.27)',language=None)
        st.caption('PLAS index는 TAPVC 의심을 위한 보조 지표이며 단독 진단 기준이 아닙니다.')

    st.divider()
    st.subheader('Thymus 참고치')
    with st.container(border=True):
        st.markdown('**Thymic diameter (cm)**')
        thymus=number('Thymic diameter','thymus')
        row=get_ref(THYMUS_CM)
        if row is None:
            st.caption('참고치 범위: 19–38주 (마지막 주는 0일)')
        else:
            mean,lower,upper=row
            if thymus is not None:
                status=('Below lower limit' if thymus < lower else 'Above upper limit' if thymus > upper else 'Within range')
                st.metric('95% reference range',status)
            text=f'Ref. {ga_ref} lower limit of 95% reference range: {lower:.2f} cm'
            if thymus is not None:
                st.code(f'Thymic diameter: {thymus:g} cm ({text})',language=None)
            else:
                st.caption(text)
            st.caption(f'Mean: {mean:.2f} cm | Upper limit: {upper:.2f} cm')
            ref_caption('THYMUS_CM')

with cdh:
    st.subheader('CDH · LHR / O/E LHR')
    st.caption('HC 및 두 폐 직경: cm · Tracing lung area: cm². 병변 반대쪽 폐를 측정합니다.')
    c1,c2=st.columns(2)
    with c1: cdh_side=st.selectbox('CDH side',('Left CDH','Right CDH'),key='cdh_side')
    with c2: cdh_hc=number('HC','cdh_hc')
    c1,c2,c3=st.columns(3)
    with c1: cdh_lung1=number('Lung longest diameter','cdh_lung1')
    with c2: cdh_lung2=number('Perpendicular diameter','cdh_lung2')
    with c3: cdh_trace=number('Tracing lung area','cdh_trace','cm²')
    st.info('Total trial은 현재 자동 계산되지 않습니다. 공식 TOTALtrial 사이트에서 Longest와 Trace 결과를 확인한 뒤 아래 칸에 입력해 주세요. 공식 계산식이 검증되면 자동 계산으로 전환할 수 있습니다.')
    st.markdown('[TOTALtrial 계산기 열기](https://www.totaltrial.eu/?id=6) · [Jani / Dekoninck 공식 확인](https://perinatology.com/calculators/LHR.htm)')
    t1,t2=st.columns(2)
    with t1: cdh_total_longest=number('TOTALtrial Longest O/E LHR','cdh_total_longest','%')
    with t2: cdh_total_trace=number('TOTALtrial Trace O/E LHR','cdh_total_trace','%')

    def format_oe_line(method, area, total_trial_value):
        if area is None or cdh_hc is None or weeks is None or days is None:
            return None
        ga_value=weeks+days/7
        values=[]
        for model in ('Jani','Dekoninck'):
            result=oe_lhr(area,cdh_hc,ga_value,cdh_side,method,model)
            values.append(f'{result:.1f}% ({model})' if result is not None else f'— ({model}: 공식 없음)')
        values.append(f'{total_trial_value:.1f}% (Total trial)' if total_trial_value is not None else '— (Total trial: 값 입력 필요)')
        return f'{method} : '+', '.join(values)

    longest_area=cdh_lung1*cdh_lung2 if cdh_lung1 is not None and cdh_lung2 is not None else None
    if weeks is None or days is None:
        st.caption('O/E LHR를 계산하려면 상단의 임신 주수를 입력해 주세요.')
    elif cdh_hc is None:
        st.caption('HC를 입력하면 결과가 표시됩니다.')
    else:
        longest_line=format_oe_line('Longest',longest_area,cdh_total_longest)
        trace_line=format_oe_line('Trace',cdh_trace,cdh_total_trace)
        if longest_line is not None or trace_line is not None:
            st.markdown('**O/E LHR**')
            if longest_line is not None: st.code(longest_line,language=None)
            if trace_line is not None: st.code(trace_line,language=None)
            combined='O/E LHR\n'+'\n'.join(x for x in (longest_line,trace_line) if x is not None)
            st.text_area('O/E LHR 전체 복사',value=combined,height=110)
        if cdh_side=='Right CDH':
            st.caption('Right CDH에 대한 Dekoninck 공식은 Perinatology에 제시되어 있지 않습니다.')
    st.caption('Jani / Dekoninck: Perinatology 공식 · Total trial: TOTALtrial 사이트 입력값')



with musculo:
    st.subheader('근골격계·흉곽')
    st.caption('길이·둘레는 cm 단위로 입력합니다.')

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
        st.caption('Foot length 참고치: 15–37주 (마지막 주는 0일). 임신 주수를 입력해 주세요.')
    else:
        foot_p5_cm=foot_row[0]  # published table is in cm
        if foot_values:
            rt_text=f'{foot_rt:g}' if foot_rt is not None else '—'
            lt_text=f'{foot_lt:g}' if foot_lt is not None else '—'
            foot_text=(f'Foot length: Rt {rt_text} cm, Lt {lt_text} cm '
                       f'(Ref. {ga_ref} 5th percentile: {foot_p5_cm:.2f} cm)')
            st.markdown('**기록용 결과 — Foot length**')
            st.code(foot_text,language=None)
        else:
            st.caption(f'Ref. {ga_ref} 5th percentile: {foot_p5_cm:.2f} cm')
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
    line=f'{title}: {value:g} cm ({reference_text})'
    st.code(line,language=None)

def pair_reference_line(title, right, left, reference_text):
    if right is None and left is None:
        st.caption(reference_text)
        return
    r=f'{right:g}' if right is not None else '—'
    l=f'{left:g}' if left is not None else '—'
    line=f'{title}: Rt {r} cm, Lt {l} cm ({reference_text})'
    st.code(line,language=None)

with digestive:
    st.subheader('소화기계 계측')
    st.caption('단위: cm. 95% CI는 평균에 대한 신뢰구간이며 개별 태아의 정상범위가 아닙니다.')
    with st.container(border=True):
        st.markdown('**Stomach**')
        stomach=number('Stomach','stomach')
        row=get_ref(STOMACH)
        if row is None:
            st.caption('참고치 범위: 14–40주. 임신 주수를 입력해 주세요.')
        else:
            reference_line('Stomach',stomach,f'Ref. {ga_ref} 5th percentile: {row[2]/10:.2f} cm; 95th percentile: {row[8]/10:.2f} cm')
            extra_source('STOMACH')
    with st.container(border=True):
        st.markdown('**Small bowel diameter**')
        small_bowel=number('Small bowel diameter','small_bowel')
        row=get_ref(SMALL_BOWEL_COLON)
        if row is None:
            st.caption('참고치 범위: 20–40주.')
        else:
            reference_line('Small bowel diameter',small_bowel,f'Ref. {ga_ref} upper 95% prediction limit: {row[2]/10:.2f} cm')
            st.caption(f'Mean: {row[0]/10:.2f} cm | 95% prediction interval: {row[1]/10:.2f}–{row[2]/10:.2f} cm')
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
                    text=f'Colon diameter: {colon:g} cm (Ref. {ga_ref} mean: {row[3]/10:.2f} cm; prediction limit pending verification)'
                    st.code(text,language=None)
            else:
                reference_line('Colon diameter',colon,f'Ref. {ga_ref} upper 95% prediction limit: {row[5]/10:.2f} cm')
                st.caption(f'Mean: {row[3]/10:.2f} cm | 95% prediction interval: {row[4]/10:.2f}–{row[5]/10:.2f} cm')
            extra_source('SMALL_BOWEL_COLON')
    with st.container(border=True):
        st.markdown('**Descending colon diameter**')
        descending_colon=number('Descending colon diameter','descending_colon')
        row=get_ref(DESCENDING_RECTUM)
        if row is None:
            st.caption('참고치 범위: 19–40주.')
        else:
            reference_line('Descending colon diameter',descending_colon,f'Ref. {ga_ref} mean: {row[0]/10:.2f} cm; 95% CI: {row[1]/10:.2f}–{row[2]/10:.2f} cm')
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
                text=f'Rectal diameter: {rectum:g} cm (Ref. {ga_ref} mean: {row[3]/10:.2f} cm; CI pending verification)'
                st.code(text,language=None)
        else:
            reference_line('Rectal diameter',rectum,f'Ref. {ga_ref} mean: {row[3]/10:.2f} cm; 95% CI: {row[4]/10:.2f}–{row[5]/10:.2f} cm')
        if row is not None:
            extra_source('DESCENDING_RECTUM')

    st.divider()
    st.subheader('비뇨기계 계측')
    with st.container(border=True):
        st.markdown('**Kidney length (cm)**')
        c1,c2=st.columns(2)
        with c1: kidney_rt=number('Kidney Rt','kidney_rt')
        with c2: kidney_lt=number('Kidney Lt','kidney_lt')
        row=get_ref(KIDNEY_MM)
        if row is None:
            st.caption('참고치 범위: 16–41주 (마지막 주는 0일)')
        else:
            p5,p50,p95=[x/10 for x in row]
            reference_text=f'Ref. {ga_ref} 5th percentile: {p5:.2f} cm; 95th percentile: {p95:.2f} cm'
            pair_reference_line('Kidney length',kidney_rt,kidney_lt,reference_text)
            st.caption(f'P50: {p50:.2f} cm')
            ref_caption('KIDNEY_MM')

with face:
    st.subheader('얼굴 계측')
    with st.container(border=True):
        st.markdown('**NB (Nasal bone length)**')
        nasal_bone=number('NB','nasal_bone')
        row=get_ref(NASAL_BONE)
        if row is None:
            st.caption('참고치 범위: 11–40주.')
        else:
            reference_line('NB',nasal_bone,f'Ref. {ga_ref} 5th percentile: {row[1]/10:.2f} cm')
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
            pair_reference_line('Ear length',ear_rt,ear_lt,f'Ref. {ga_ref} 5th percentile: {row[0]/10:.2f} cm')
            extra_source('EAR_LENGTH')

with refs:
    st.subheader('태아성장 · 양수 · 도플러')
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
                st.code(f'{label}: {efw:g} g (Percentile unavailable: reference GA {min(t)}–{max(t)}w)',language=None)
                return
            band=percentile_band(efw,ps,row)
            closest=nearest_reference_percentile(efw,ps,row)
            size=median_equivalent_ga(efw,t)
            size_text=f', {size[0]}w{size[1]}d size' if size is not None else ''
            if closest is not None:
                pct,ref_g=closest
                suffix='rd' if pct==3 else 'th'
                st.code(f'{label}: {efw:g} g{size_text} ({band}; Ref. {ga_ref} nearest {pct}{suffix} percentile: {ref_g:.0f} g)',language=None)
                st.caption('표시된 백분위수는 구간이며, nearest는 가장 가까운 참고표 수치입니다. size는 P50 기준 추정 주수입니다.')
            else:
                st.code(f'{label}: {efw:g} g{size_text} (Ref. unavailable)',language=None)

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
        if row is None and weeks is not None and days is not None:
            st.info(f'선택한 {weeks}주 {days}일의 참고치가 없습니다. {refname.replace("EFW_", "")} 참고표 제공 범위는 {min(t)}–{max(t)}주이므로, 이 주수의 EFW 백분위수는 산출하지 않습니다.')
        if row is not None:
            st.caption(' | '.join(f'P{pct}: {val:.0f} g' for pct,val in zip(ps,row) if val is not None))
            ref_caption(refname)
            if group.startswith('Singleton') and weeks==21:
                st.caption('21주 P97은 제공된 표에 값의 불일치가 있어 표시하지 않았습니다.')
            if not group.startswith('Singleton'):
                st.caption('DC/MC 자료는 초음파 추정체중 성장곡선이 아닌 쌍태아 출생체중 참고표입니다.')
    with st.container(border=True):
        st.markdown('**AFI (cm)**')
        afi=number('AFI','afi')
        row=get_ref(AFI)
        if row is None:
            st.caption('참고치 범위: 16–42주 (마지막 주는 0일)')
        else:
            show_band('AFI percentile interval',afi,[x/10 for x in row],[3,5,50,95,97],'cm')
            if afi is not None:
                nearest=nearest_reference_percentile(afi,[3,5,50,95,97],[x/10 for x in row])
                if nearest is not None:
                    pct,ref_mm=nearest
                    st.code(f'AFI: {afi:g} cm (Ref. {ga_ref} {pct}th percentile: {ref_mm:.2f} cm)',language=None)
                else:
                    st.code(f'AFI: {afi:g} cm (Ref. unavailable)',language=None)
            st.caption(' | '.join(f'P{pct}: {val/10:.2f} cm' for pct,val in zip([3,5,50,95,97],row)))
            ref_caption('AFI')

    st.divider()
    st.subheader('Umbilical artery · MCA Doppler')
    with st.container(border=True):
        st.markdown('**Umbilical artery Doppler**')
        ua_sd=number('Umbilical artery S/D ratio','ua_sd','ratio')
        ua_row=get_ref(UMB_DOPPLER)
        if ua_row is None:
            st.caption('Umbilical artery 참고치: 16–42주. 임신 주수를 입력해 주세요.')
        else:
            if ua_sd is not None:
                sd_pct=estimated_ua_percentile(ua_sd,ua_row[1],ua_row[3],ua_row[5])
                prefix='Elevated umbilical artery S/D ratio' if ua_sd>ua_row[5] else 'Umbilical artery S/D ratio'
                st.code(f'{prefix}: {ua_sd:.2f} ({sd_pct} percentile)',language=None)
                st.caption(f'Ref. {ga_ref} S/D P5 {ua_row[1]:.2f} · P50 {ua_row[3]:.2f} · P95 {ua_row[5]:.2f}')
            st.caption('P5–P50–P95 사이 percentile은 선형 추정치이며, 실제 분포 기반 정밀 백분위수가 아닙니다.')
    with st.container(border=True):
        st.markdown('**MCA Doppler**')
        mca_psv=number('MCA PSV','mca_psv','cm/s')
        mca_row=get_ref(MCA_PSV_MEDIAN)
        if mca_row is None:
            st.caption('MCA PSV 참고치: 15–40주. 임신 주수를 입력해 주세요.')
        elif mca_psv is not None:
            mca_mom=mca_psv/mca_row[0]
            st.code(f'MCA PSV: {mca_psv:.1f} cm/s ({mca_mom:.2f} MoM; {mca_mom_band(mca_mom)})',language=None)
            st.caption(f'Ref. {ga_ref} median: {mca_row[0]:.1f} cm/s · 1.5 MoM: {mca_row[0]*1.5:.1f} cm/s')
    st.caption('Doppler 참고치: 사용자가 제공한 Umbilical artery S/D 및 MCA PSV 표 (출처 표기: 2000).')
