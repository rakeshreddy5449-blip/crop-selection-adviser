# Agronomic UNKNOWN Handling Audit

**Audit date:** 2026-11-05  
**Scope:** Current agronomic engine, recommendation integration, Streamlit presentation, focused tests, and `agronomic_evidence_research.csv`.  
**Audit only:** No application, test, source-data, or model files were changed. This report is the only file created for this audit.

## Executive summary

The agronomic engine does **not** load or consult `agronomic_evidence_research.csv`. Its default input is the older `reports/agronomic_requirements_sources.csv` in `AgronomicSuitabilityEngine.__init__` (`src/agronomic_rules.py:92-107`); `RecommendationEngine.__init__` passes that legacy CSV by default (`src/recommendation_engine.py:10-15`). As a result, there is a critical mismatch between the new research status and runtime decisions:

- If a crop/parameter rule is absent from the legacy CSV, `evaluate_crop` reports an insufficient-information check and adds the parameter to `unavailable_rules` (`src/agronomic_rules.py:147-164`).
- If an old legacy row exists with a plausible source name and HTTP(S) URL, the engine treats the reference as “available” and may numerically assess its min/max even when the research register marks that crop/parameter `UNKNOWN`. `reference_available` is a format/presence check, not evidence verification (`src/agronomic_rules.py:47-70, 171-180, 246-290`).
- The research register has 1 source-content-verified entry (rice irrigation/water input) and 109 `UNKNOWN` entries. The engine does not read the register’s `evidence_status`, `verification_status`, claim, or growing-condition context (`reports/agronomic_evidence_research.csv:2-111`).

Thus, missing rules in the *legacy data* are generally gated correctly, but research-register `UNKNOWN` values are not consistently recognized at runtime. Unsupported legacy numerical rules can yield individual “Suitable”, “Highly Suitable”, or “Unsuitable” checks and a misleading crop-level agronomic status. In the current evaluator, missing rule/evidence gaps and qualitative checks usually prevent a final `RECOMMENDED` category, but the code does not enforce the research register as the authority for that gate.

## Answers to audit questions

### 1. When a crop/parameter combination is UNKNOWN, does the engine correctly report insufficient evidence?

**Only when it is also unavailable or unusable in the legacy CSV.** In `evaluate_crop`, no matching legacy row generates an `Insufficient Information` check, records the parameter in `unavailable_rules`, and adds it to `insufficient_evidence` when a farmer supplied a value (`src/agronomic_rules.py:147-164`). A matching row with no structurally usable source is likewise marked insufficient (`src/agronomic_rules.py:171-194`).

However, the research CSV is not consumed. Its `UNKNOWN` status cannot gate a corresponding older row. For example, rice pH, temperature, and rainfall are `UNKNOWN` in the research register (rows 102-104), while the legacy CSV contains rows with numeric ranges and HTTP(S) references. Those values can be assessed as if they were acceptable-range rules. This is **not correct handling of research-register UNKNOWN**.

### 2. Can missing crop rules accidentally be interpreted as suitable?

**A wholly missing legacy rule is not itself rated suitable:** its check assessment is `Insufficient Information`, and `unavailable_rules` prevents the normal positive overall status (`src/agronomic_rules.py:147-164, 318-325`).

But two risks remain:

1. A legacy row can exist even though the corresponding research-register entry is `UNKNOWN`. If its source name and URL pass the structural test, it is assessed as a rule anyway; this affects numeric checks in particular (`src/agronomic_rules.py:47-70, 171-180, 246-290`).
2. `has_unsuitable` is checked before unavailable/insufficient evidence when deriving overall status (`src/agronomic_rules.py:318-321`). An unsupported legacy threshold can therefore make the whole crop `Unsuitable`, and recommendation mapping then emits `NOT RECOMMENDED` before it considers evidence gaps (`src/recommendation_engine.py:136-155`).

### 3. Can the engine label a crop `RECOMMENDED` when agronomic requirements are unknown?

**The current normal flow has defensive gates, but no guarantee tied to the research register.** `recommend` maps an agronomic result with `Insufficient Information`, unavailable rules, insufficient evidence, or invalid information to `INSUFFICIENT INFORMATION`. It only reaches `RECOMMENDED` in the final `else` after those checks (`src/recommendation_engine.py:136-163`).

The current engine also treats supplied qualitative values as insufficient evidence rather than validated comparisons (`src/agronomic_rules.py:198-217`), and any missing tracked rules populate `unavailable_rules`. These usually make the positive category unreachable with current legacy coverage. Nonetheless, because the evidence register is ignored, legacy numerical claims marked `UNKNOWN` can still count as evaluated agronomic constraints. The final category gate is therefore not a reliable assertion that all five requirements are sufficiently supported; it only reflects the legacy engine’s own fields. A future complete-looking legacy CSV could reach `RECOMMENDED` without being reconciled with research verification status.

### 4. Are model predictions kept separate from agronomic suitability?

**Mostly yes at the data/UI presentation boundary.** ANN, Random Forest, and SVM predictions are returned under `model_predictions` (`src/recommendation_engine.py:193-199`) and shown in a separate “Machine Learning Predictions” section (`pages/1_Crop_Adviser.py:305-324`). The engine then creates an ML candidate set and independently calls `evaluate_crop` for each candidate (`src/recommendation_engine.py:105-133`). Recommendation ranking combines category priority with ML vote count (`src/recommendation_engine.py:183-188`).

This separation should be preserved. One clarity limitation is that “Ranked Crop Recommendations” and the final recommendation category combine model candidate selection/agreement and agronomic gating; the UI should explicitly explain that model predictions are not agronomic evidence and that a ranking is not a validated suitability claim.

### 5. Does the UI clearly distinguish model prediction, agronomic evidence, and suitability?

**Partially.** The page has separate model-prediction cards, then a recommendation expander that labels “Agronomic Status”, “Model Agreement”, and “Agronomic Evidence” separately (`pages/1_Crop_Adviser.py:305-380`). It also separately lists missing farmer inputs, unavailable rules, and insufficient evidence (`pages/1_Crop_Adviser.py:389-402`).

However, the visible “Agronomic Status” can say `Suitable`/`Highly Suitable` for legacy numeric rules whose research-register evidence status is `UNKNOWN`. The displayed evidence table uses the engine’s checks; because the research register is not consumed, it cannot show that authoritative status. For references with format-valid URLs, it says “Not independently verified”, but does not show the register’s actual `UNKNOWN`/`VERIFIED` status, verified claim, research context, or distinction between a URL being available and evidence supporting the claim. This risks users interpreting a model candidate and a rule-derived status as proven agronomic advice.

### 6. Does the engine incorrectly treat rainfall and irrigation as interchangeable?

**No direct parameter substitution was observed, but the rainfall rule can still be unsupported.** `rainfall` is in the numerical parameter set, and `irrigation` is a separate qualitative parameter (`src/agronomic_rules.py:9-11`). The evaluator independently matches each parameter and does not copy an irrigation value into rainfall (`src/agronomic_rules.py:136-164, 198-217`).

The research register explicitly says rice’s verified irrigation figures are seasonal field water input, not rainfall requirements (`reports/agronomic_evidence_research.csv:104-106`). The legacy CSV’s rice rainfall row has its own numeric range; because that row is not cross-checked against the research register, the evaluator may use an unverified rainfall rule. The risk is not a direct code-level equivalence but that distinct agronomic quantities are not evidence-status-gated, and the verified irrigation record is not integrated.

### 7. Are source claims and evidence status preserved in the output?

**Source metadata is only partially preserved; research evidence and status are not.** Checks and source entries include source name/URL, source notes, confidence, last checked, a computed `reference_available` flag, and `source_verified=False` (`src/agronomic_rules.py:47-70, 171-180, 330-342`). The assessment reason describes the applied rule/range but does not return the original evidence register’s publication title, page/section, claim text, growing-condition context, or `evidence_status`/`verification_status`.

The UI displays each check’s assessment/reason and source name/URL, labeling available references “Not independently verified” (`pages/1_Crop_Adviser.py:360-387`). It does not show the research register’s verified/unknown status or its qualified claim. Thus, legacy source fields are partly passed through, but source-content verification status and supporting research claims are **not** preserved end-to-end.

### 8. Which tests cover these cases, and which are missing?

**Existing coverage**

- `test_provided_value_without_crop_rule_is_not_reported_missing` checks an unknown crop with a supplied pH: it expects unavailable rule, insufficient evidence, and overall insufficient status (`tests/test_agronomic_rules.py:127-135`).
- `test_missing_numerical_range_is_insufficient_evidence` checks an incomplete numeric range (`tests/test_agronomic_rules.py:150-172`).
- `test_qualitative_inputs_are_not_assumed_suitable` checks that supplied soil texture and irrigation are not marked suitable (`tests/test_agronomic_rules.py:175-191`).
- `test_unverified_source_is_not_returned_as_reference` checks the legacy placeholder source name/URL (`tests/test_agronomic_rules.py:194-208`).
- `test_recommendation_surfaces_unavailable_and_insufficient_agronomic_rules` uses a mocked agronomic response and checks the `INSUFFICIENT INFORMATION` mapping (`tests/test_recommendation_engine.py:51-98`).
- `test_suite_recommendation_engine` checks general valid input, missing model features, missing optional information mapped to caution, and one unsuitable case (`tests/test_recommendation_engine.py:8-48`).

**Important missing coverage**

- No test loads `agronomic_evidence_research.csv` or proves that its 109 `UNKNOWN` records gate legacy rows.
- No regression test supplies the existing rice numeric inputs with pH/temperature/rainfall research statuses `UNKNOWN` and asserts they cannot produce a positive suitability assessment based on legacy data.
- No recommendation test proves that a candidate with any research-register `UNKNOWN` constraint cannot be `RECOMMENDED` (or `NOT RECOMMENDED` based solely on unsupported limits).
- No test checks that `source_verified=False` prevents a numeric rule from being treated as a verified agronomic constraint. Existing tests only check the flag and placeholder filtering.
- No test asserts the rice irrigation claim remains distinct from rainfall and that its context-specific seasonal water input is not used as a rainfall threshold.
- No test verifies source claim, evidence status, context, and verification metadata are preserved from the research CSV through recommendation response to UI.
- No UI test covers the distinction among model predictions, evidence status, agronomic status, and recommendation category.
- Existing expected `Highly Suitable`/`Suitable` results for rice and grapes use the legacy requirements CSV, not the research evidence status (`tests/test_agronomic_rules.py:12-35, 79-80`). They should be revisited once evidence-backed rules become the runtime source; this audit does not change those expectations or implementation.

## Risks

1. **Evidence/runtime divergence:** a newly researched `UNKNOWN` does not invalidate an older numerical row.
2. **False precision or confidence:** a structurally valid URL can make unsupported legacy min/max bounds operational, while `source_verified=False` is merely returned and does not block assessment.
3. **Overstated suitability/rejection:** unsupported numbers can drive individual suitable/unsuitable checks; an unsuitable check takes precedence over evidence gaps in overall status and recommendation mapping.
4. **Incomplete provenance at the user boundary:** displayed reasons and reference URLs do not expose the research register’s qualified claim or evidence status.
5. **Maintenance hazard:** adding rows to the old CSV without linking them to verified evidence can silently increase the number of rules that affect recommendations.

## Recommended corrections (not implemented)

1. Make the research register (or a validated derivative that retains its evidence fields) the runtime source of truth. Treat `evidence_status=UNKNOWN` or any status other than explicitly source-content-verified as insufficient evidence—not as a numeric agronomic rule.
2. Require evidence supporting the exact crop, parameter, claim, and growing context before applying any threshold. Do not equate `reference_available` with verified evidence; keep those as separate concepts.
3. Do not derive `Unsuitable` or `NOT RECOMMENDED` from constraints whose evidence status is unknown. Report evidence gaps first and keep unsupported conditions indeterminate.
4. Permit `RECOMMENDED` only when all required tracked parameters have evidence-backed rules, the relevant farmer inputs are present and valid, and each required comparison was actually evaluated. Otherwise use the existing `INSUFFICIENT INFORMATION` or `RECOMMENDED WITH CAUTION` category as appropriate to the actual gap.
5. Keep irrigation/water-input records separate from rainfall. Preserve irrigated/rainfed system, soil/groundwater context, units, and whether a figure is an observed/typical input, acceptable limit, or optimum. Do not convert context-specific irrigation amounts to rainfall thresholds.
6. Pass publication title, institution/author, direct URL, source section, claim, context, and evidence/verification status through engine results and show them in the dashboard. Clearly label unknown evidence and distinguish ML prediction from agronomic assessment and recommendation category.
7. Add integration tests using a fixture derived from the 110-row research register. Cover unknown legacy-vs-register conflicts, supported rice irrigation vs unknown rice rainfall, non-promotion to recommended/rejected with unknowns, and provenance/status display/output.

## Files and functions reviewed

- `src/agronomic_rules.py`: `AgronomicSuitabilityEngine.__init__`, `_source_metadata`, `_preferred_range`, `evaluate_crop`.
- `src/recommendation_engine.py`: `RecommendationEngine.__init__`, `recommend`.
- `pages/1_Crop_Adviser.py`: result rendering for model prediction cards and ranked crop recommendation expanders.
- `tests/test_agronomic_rules.py`: core rule tests and added unavailable-rule, range, qualitative, and unverified-source tests.
- `tests/test_recommendation_engine.py`: category mapping and model input tests.
- `reports/agronomic_evidence_research.csv`: all 110 crop/parameter statuses; 1 `VERIFIED` (rice irrigation) and 109 `UNKNOWN`.
