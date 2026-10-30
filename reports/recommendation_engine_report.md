# Recommendation Engine Technical Report (Stage 3.3)

## A. Objective
Integrate the ML models and rule-based agronomic suitability system into a unified recommendation decision boundary.

## B. Architecture
Modular design separating `agronomic_rules.py` and ML architectures inside `recommendation_engine.py`. Strict change control protocols preserve downstream transparency.

## C. Model Agreement & Ranking Logic
- ML models vote independently on crop features.
- If any evaluated parameter falls outside biological safety limits, the crop category becomes **NOT RECOMMENDED** regardless of model prediction confidence.
- Category ranking levels: RECOMMENDED > RECOMMENDED WITH CAUTION > INSUFFICIENT INFORMATION > NOT RECOMMENDED.

## D. ML Models Verification
- ANN retrained: NO
- Random Forest retrained: NO
- SVM retrained: NO
- No combined formulas used.
