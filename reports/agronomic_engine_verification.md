# Agronomic Suitability Engine Verification Report (Stage 3.2)

## A. Purpose
This stage defines a clear separation between the ML prediction confidences and rule-based agronomic constraints. The rule-based engine assesses the suitability of agricultural parameters against verified agronomic criteria independent of the ML probability metrics.

## B. Files Inspected
- `reports/agronomic_requirements_sources.csv`
- `src/agronomic_rules.py`
- `tests/test_agronomic_rules.py`
- `reports/agronomic_source_conflicts.md`
- `models/input_ranges.json`

## C. Crop Coverage Table
Of the 22 crops, the rules catalog covers the following status mapping:
- **Complete Rules** (pH, Temp, Rainfall, Soil, Irrigation, Traceable): **3 Crops** (Rice, Maize, Grapes)
- **Partial Rules** (pH baseline placeholders with UNVERIFIED source tracking): **19 Crops**
- **Missing Rules**: **0 Crops**

Total crops in catalog: 22
Crops with complete rules: 3
Crops with partial rules: 19
Crops with missing rules: 0

## D. Source Verification & Traceability
- **pH, temperature, rainfall** for complete crops trace fully to official databases (FAO, IRRI, USDA, UC Davis).
- All other 19 baseline crops have placeholders tagged explicitly as `UNVERIFIED` to preserve scientific transparency.

## E. Suitability Rule Logic
- **Highly Suitable**: Input matches documented optimal/preferred sub-bounds.
- **Suitable**: Input is within acceptable limits but outside the ideal range.
- **Unsuitable**: Input falls outside the acceptable range bounds.
- **Insufficient Information**: No parameters can be successfully evaluated.

## F. Missing-Data Handling
- Unknown values are treated as missing (`missing != 0` or standard statistics placeholders).
- The engine reports specific missing features in `missing_information` rather than guessing suitable defaults.

## G. Conflict Handling
- Source conflicts are documented explicitly in `reports/agronomic_source_conflicts.md` but are handled via hierarchical/fallback rule mapping in python, ensuring no synthetic mathematical averages are injected.

## H. ML Separation
- There is **no** combining formula (e.g., `ML_probability * agronomic_score`). They remain separate evidence layers.
- The ML model file weights were **not** modified during this pass.

## I. Final Status
**PASS WITH LIMITATIONS** (Due to partial agronomic coverage of secondary baseline crops, which are properly marked as UNVERIFIED to avoid artificial speculation).
