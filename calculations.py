"""Arithmetic for fetal ultrasound quick-reference calculations.

No reference percentiles, diagnostic cutoffs, or clinical interpretation are
included. Inputs for each ratio must use the same units and measurement type.
"""
from __future__ import annotations

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
