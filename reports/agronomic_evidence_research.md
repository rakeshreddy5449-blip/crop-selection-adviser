# Agronomic Evidence Research Register

**Research date:** 2026-11-05  
**Crop labels:** The exact 22 labels in `models/metadata.json` and the trained label encoder.  
**Tracked parameters:** pH, temperature, rainfall, soil_texture, irrigation.  
**Evidence standard:** A combination is marked verified only when an accessed, crop-specific source page directly supports the recorded claim. A URL, search snippet, legacy project entry, or general institutional homepage is not sufficient.

## Result

Of the 110 crop/parameter combinations, **1 has sufficiently supported, source-content-verified evidence** in this research pass. The remaining **109 are UNKNOWN**. UNKNOWN means the research pass did not confirm adequate, accessible, crop-specific evidence; it does not mean that the crop has no agronomic requirement.

| Crop label | pH | Temperature | Rainfall | Soil texture | Irrigation |
|---|---|---|---|---|---|
| apple | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| banana | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| blackgram | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| chickpea | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| coconut | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| coffee | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| cotton | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| grapes | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| jute | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| kidneybeans | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| lentil | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| maize | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| mango | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| mothbeans | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| mungbean | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| muskmelon | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| orange | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| papaya | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| pigeonpeas | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| pomegranate | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| rice | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | VERIFIED (context-specific irrigated water input) |
| watermelon | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

## Verified entry: Rice irrigation / water input

- **Publication/page:** “How to manage water”
- **Institution:** International Rice Research Institute (IRRI), Rice Knowledge Bank
- **Direct page:** <http://knowledgebank.irri.org/step-by-step-production/growth/water-management>
- **Relevant sections:** Opening overview, water management, and continuous flooding.
- **Supported claim:** The page states that rice is typically grown in bunded fields with continuous flooding until 7–10 days before harvest. It reports seasonal field water input ranging from 400 mm in heavy clay soils with shallow groundwater to more than 2,000 mm in coarse-textured soils with deep groundwater, and says 1,300–1,500 mm is typical for irrigated rice in Asia.
- **Units and context:** Millimetres of seasonal field water input for lowland irrigated systems; the cited amount varies with soil texture and groundwater depth.
- **Interpretation:** These figures describe context-dependent irrigation/field water input. They are **not rainfall requirements**, and the source does not identify them as an acceptable range or optimal threshold. The research CSV therefore retains the claim and context verbatim in its own fields and leaves universal minimum/maximum as `UNKNOWN`.
- **Verification:** Source content was accessed and supports the statements above (checked 2026-11-05).

## Unknowns and limits

- The IRRI page does not support a rice pH, temperature, or rainfall threshold in the accessed content. Its soil-texture discussion describes effects on water use and puddling; it is not evidence of a preferred soil texture.
- No crop-specific, adequately accessed evidence was confirmed for the remaining 109 combinations. No numeric values were inferred or copied from another crop.
- The project’s existing requirements documents, conflicts report, and source CSV were used only as research leads. Their claims were not promoted to verified findings without supporting source content.
- See [agronomic_evidence_gaps.md](./agronomic_evidence_gaps.md) for all unknown combinations and [agronomic_source_verification.md](./agronomic_source_verification.md) for source checks and limitations. The row-level register is [agronomic_evidence_research.csv](./agronomic_evidence_research.csv).
