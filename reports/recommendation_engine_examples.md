# Recommendation Engine Examples (Stage 3.3)

This report presents actual engine scenarios to show how predictions are mapped without merging metrics.

## Scenario A: Successful Recommendation (Rice Complete Input)

- Inputs: pH=6.2, Temp=25C, Rainfall=1500mm, Soil=Heavy clay
- ML Votes: 3/3 models agree
- Assessment: RECOMMENDED
- Explanations: Inputs meet exact optimal bounds of FAO & IRRI datasets.

## Scenario B: ML/Agronomic Conflict (Extreme pH Outlier)

- Inputs: pH=11.5 (OOD)
- ML Verdict: Grapes / Rice predicted based on other climatic elements
- Agronomic Check: Unsuitable
- Assessment: NOT RECOMMENDED (Agronomic constraints take strict priority over model classifications)

## Scenario C: Missing Optional Fields

- Inputs: Soil Texture and Irrigation omitted
- Assessment: RECOMMENDED WITH CAUTION (Missing parameters reported clearly in result structure to prevent false harvest confidence)
