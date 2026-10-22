"""Safe table lookup/interpolation for gestational-age-specific published reference knots."""
from __future__ import annotations
import math


def at_ga(table: dict, weeks: int, days: int):
    """Linear interpolation between published completed-week table rows; no extrapolation."""
    if not 0 <= days <= 6:
        raise ValueError('days must be 0–6')
    if weeks not in table:
        return None
    if days == 0:
        return table[weeks]
    if weeks + 1 not in table:
        return None
    weight = days / 7
    a, b = table[weeks], table[weeks + 1]
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
