# Agronomic Suitability Engine Evaluation Examples

This document presents real evaluation scenarios produced by the rule-based suitability engine, showcasing how input conditions are mapped transparently against documented evidence without combined machine learning probability scaling.

---

## Example 1: Rice Evaluation (Optimal Conditions)

### Input Conditions:
- **pH**: 6.1
- **Temperature**: 24.5 °C
- **Rainfall**: 1500 mm
- **Soil Texture**: Heavy clay

### Agronomic Checks:
*   **pH**: Input = 6.1 -> **Highly Suitable**
    - *Reason*: Falls within preferred optimal range of 5.5-6.5 pH.
    - *Source*: FAO Crop Water Information
*   **Temperature**: Input = 24.5 °C -> **Highly Suitable**
    - *Reason*: Falls within optimal range of 22-32 °C.
    - *Source*: International Rice Research Institute (IRRI)
*   **Rainfall**: Input = 1500 mm -> **Highly Suitable**
    - *Reason*: Falls within acceptable range of 1000-2500 mm.
    - *Source*: IRRI Rice Knowledge Bank

### Final Assessment:
**Highly Suitable**

### Supporting Reasons:
- pH is in preferred range.
- Temperature is in preferred range.
- Rainfall is within acceptable range.

### Warnings:
*None*

### Missing Information:
- Irrigation availability

---

## Example 2: Grapes Evaluation (Qualitative Evaluation & Traceability)

### Input Conditions:
- **pH**: 6.5
- **Temperature**: 28.0 °C
- **Rainfall**: 600 mm

### Final Assessment:
**Suitable**

### Missing Information:
- Soil Drainage
- Climate seasonality

---

## Example 3: Maize (Unsuitable Conditions)

### Input Conditions:
- **pH**: 4.0
- **Temperature**: 25.0 °C
- **Rainfall**: 600 mm

### Final Assessment:
**Unsuitable**

### Rejection Reason:
- **pH (Input: 4.0)** is outside the documented acceptable range of 5.5 to 7.5.
- *Source*: USDA NRCS
