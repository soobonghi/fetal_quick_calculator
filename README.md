# Fetal Quick Calculator v14 — single-file deployment

## Update instructions
1. Upload **app.py** to the ROOT of the GitHub repository, replacing the previous app.py.
2. Commit changes.
3. Streamlit Cloud app should redeploy automatically. If needed reboot the app.

Only app.py and requirements.txt are required for v14. Old reference_calc.py, reference_data.py, reference_extra.py, calculations.py may remain in GitHub but are no longer imported by app.py.

This bundle includes the user-provided reference tables. Confirm copyright permissions before publishing them in a public repository. The values and clinical criteria require independent clinical validation.


v15: Thymic diameter moved to Heart; Kidney length moved to Digestive & Urinary; remaining EFW/AFI tab renamed Growth & Amniotic Fluid. Existing calculations preserved.


## v17 changes
- CTCR and CTAR: both two-decimal unitless ratios, no percent suffix.
- GOSE: show ratio score and Grade together.
- PLAS: show normal mean ± SD (0.62 ± 0.19) and separate TAPVC screening cutoff ≥1.27. The former is not a reference interval; the latter is not a stand-alone diagnosis. Sources: Kawazu et al., Prenat Diagn 2019 (PMID 30615216); ISUOG VISUOG TAPVR.
- Stomach: shorter label in copyable result.
- Kidney: separate Rt/Lt inputs, one copyable combined line with GA-specific P5/P95.
