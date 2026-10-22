"""Safe table lookup/interpolation for gestational-age-specific published reference knots."""
from __future__ import annotations
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
