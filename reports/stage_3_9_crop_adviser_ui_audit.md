# Stage 3.9 — Crop Adviser UI/UX Audit and Redesign Plan

**Audit date:** 2026-11-05  
**Scope:** Existing Streamlit Crop Adviser page, supporting recommendation/evidence data contracts, and the app landing page.  
**Status:** Audit and plan only. No application, test, model, or data files were changed.

## 1. Existing UI structure

The Crop Adviser is a single Streamlit page implemented in `pages/1_Crop_Adviser.py`.

1. **Page setup and theme** — wide layout, page title/icon, inline CSS, pale green background, dark green headings, white inputs, and green buttons (`pages/1_Crop_Adviser.py:14-89`).
2. **Engine startup** — cached `RecommendationEngine`, success state or error followed by `st.stop()` (`pages/1_Crop_Adviser.py:92-114`).
3. **Farm input form** — one `st.form` containing:
   - N, P, K in three columns (`pages/1_Crop_Adviser.py:123-165`).
   - Temperature and humidity in a two-column layout, paired with pH and rainfall (`pages/1_Crop_Adviser.py:167-207`).
   - Optional free-text soil texture, irrigation method, and location (`pages/1_Crop_Adviser.py:210-229`).
   - A full-width recommendation submit button (`pages/1_Crop_Adviser.py:231-234`).
4. **Submission and errors** — checks the seven ML inputs for `None`, builds `farmer_inputs`, optionally adds soil/irrigation/location, runs recommendations, stores successful output in session state, and clears stored results on an exception (`pages/1_Crop_Adviser.py:239-286`).
5. **Results**:
   - Top-level warnings (`pages/1_Crop_Adviser.py:301-306`).
   - Three model predictions in metric widgets (`pages/1_Crop_Adviser.py:308-324`).
   - Ranked recommendations in expandable cards, including recommendation category, agronomic evidence status, suitability, model agreement, reasoning, evidence table, missing inputs/rules, legacy notices, and validation warnings (`pages/1_Crop_Adviser.py:327-468`).
   - Weather context shown as raw JSON, or a no-weather message (`pages/1_Crop_Adviser.py:470-481`).
   - General decision-support disclaimer (`pages/1_Crop_Adviser.py:483-486`).

The root `app.py` is a separate welcome/overview page. It has a green hero, a dark green sidebar, feature cards, a model overview, project details, and its own inline CSS. Its styling is not shared as a reusable theme with the adviser page.

## 2. Problems identified

### Layout and visual hierarchy

- The adviser page is a vertically long form/results document, with limited grouping beyond headings and dividers. The engine-ready success notice takes prominent space even during normal use.
- Inline CSS in `pages/1_Crop_Adviser.py` styles basic elements but does not define a page-wide spacing/type scale, consistent card pattern, or responsive rules. It differs from the home-page styles in `app.py`.
- Most sections rely on default Streamlit spacing and component styles. Result areas do not have a unified visual container or summary hierarchy.

### Input form

- “All numeric limits below are based on the model training dataset” (`pages/1_Crop_Adviser.py:125-130`) is easy to read as agronomic safe/acceptable bounds. They are widget input bounds based on model data, not validated crop suitability limits.
- Seven required numeric inputs are collected together with optional information, but the form does not provide a compact explanation of which fields are required for ML versus optional for agronomic context.
- Exact dataset minima/maxima are shown in controls, sometimes as long decimal limits, which can distract users from measurement precision and be mistaken for agronomic thresholds.
- Inputs are arranged in fixed 3-column and 2-column groups; the page contains no explicit small-screen layout strategy.
- Soil texture, irrigation method, and location are free text, without examples or explanatory context on how they will be used. This is especially important because qualitative agronomic comparisons may remain unknown.
- Validation appears only after submit. The page checks missing fields, but the empty-field feedback is not associated with individual controls. Numeric fields also use feature bounds that can prevent entering values outside training distribution before the engine has a chance to explain them.

### Predictions, agreement, and recommendations

- ANN, Random Forest, and SVM predictions are visually separated into three metrics, which is a useful starting separation. Crop names rendered in metric values may be long and do not have a dedicated crop label/visual treatment.
- The same information is repeated in recommendation expanders through “Model Agreement”. The page does not lead with a compact agreement summary that tells the user whether predictions agree or differ.
- “Ranked Crop Recommendations” does not explain that the candidate list is formed from ANN top candidates plus RF/SVM predictions; it is not necessarily a ranking of all 22 crops.
- No probability/confidence value is displayed, appropriately avoiding fabricated certainty. The redesign should keep this restraint.
- Category labels and “Agronomic Suitability” are both shown, but the page could make the relationship clearer: ML prediction is a model output; evidence status describes source coverage; suitability can remain “Cannot Determine”; the recommendation category is the combined decision-support outcome.

### Agronomic evidence and UNKNOWN handling

- The evidence table contains many provenance/context columns. It is valuable for auditability but can become very wide, particularly on mobile.
- For each record, the dashboard displays only the verified claim when `source_verified` is true; for unknown/unverified evidence, it displays a generic unknown notice. Historical legacy information is rendered using Python `str(...)`, which is not an easily scannable presentation.
- Unknown evidence is explained in a general info callout repeated within every recommendation expander; repeated callouts add clutter. Parameter-level unknowns also appear in “Insufficient Agronomic Evidence”.
- The page shows missing farmer inputs separately from unavailable rules/evidence, a useful distinction that should be retained.
- Source limitations and growing context are displayed as separate columns, but the current broad table makes those caveats hard to scan and may be truncated visually on small screens.
- Reference URLs and full claims need controlled wrapping/clickable links and clear verification labels. A URL alone must not visually imply a verified source.

### Weather

- Weather data is rendered as raw `st.json`, exposing implementation-oriented fields and nested payload structure rather than a concise farmer-facing summary.
- Context is not grouped into status, location, retrieval time, available observations, and warnings. Missing values may appear as JSON nulls without a clear explanation.
- Weather is external context and should not visually imply that it was used to replace farmer-entered measurements; the engine retains user values and emits conflict warnings.

### Responsive behaviour and consistency

- Streamlit columns generally stack in narrow viewports, but three model metrics, three NPK inputs, fixed two-column input groupings, and the multi-column evidence table are not explicitly optimized for mobile.
- CSS selectors target widget labels and metrics globally but do not include narrow-screen adjustments, reduced-motion considerations, or robust component-specific layout rules.
- Emoji use is not consistently paired with a text hierarchy; color is the primary way to signal success/warnings in some places.
- The page and landing page have separate style implementations, so typography, sidebar, background, and card treatment can feel like separate products.
- No visual/browser or viewport tests were found during this audit; responsive quality has not been verified by screenshot or device-size checks.

## 3. Proposed improved layout

Keep the existing single-page workflow and Streamlit architecture. Reorganize the same data into a responsive dashboard with progressive disclosure:

1. **Compact page header**
   - Product title, short decision-support description, and a concise note that model predictions are not guarantees.
   - Remove routine “engine ready” success noise; keep actionable load errors visible.
2. **Farm conditions form in a clear panel**
   - Divide into “Soil nutrients”, “Climate measurements”, and “Optional farm context”.
   - Mark required ML fields and optional context explicitly.
   - Explain that displayed input bounds reflect the model input domain, not agronomic suitability thresholds.
   - Keep all seven model inputs and current optional fields; do not change prediction inputs or logic.
3. **Prediction summary**
   - Three responsive model cards, one for each existing prediction.
   - A separate model-agreement summary derived only from existing prediction values/votes, without probabilities or invented confidence metrics.
4. **Recommendation list**
   - A concise card per existing ranked candidate.
   - Show crop, existing category, and a clearly worded evidence/suitability status.
   - Show “Model agreement” as prediction context, not as suitability evidence.
   - Expand details for parameter-level evidence, source claims, limitations, and historical legacy data.
5. **Evidence coverage and suitability panel**
   - Keep farmer-input omissions separate from unavailable or UNKNOWN evidence.
   - Display “Cannot determine suitability” distinctly from “Unsuitable”.
   - Show source verification status, crop/context, claim, units, and limitations; no suitability gauge or numeric score unless the engine supplies a validated value.
6. **Weather context panel**
   - Present status and location first, then available temperature/humidity/rainfall observations, retrieval time, and warnings.
   - Explain unavailable/unknown fields and that current external weather is contextual and does not silently replace farmer measurements.
7. **Consistent footer/disclaimer**
   - Preserve decision-support limitation and source/evidence caveats.

## 4. Component-by-component redesign plan and available data

| Component | Current data available | Proposed presentation |
|---|---|---|
| Page header | Static title/description and decision-support caveat | Compact title and concise subtitle; no new analytics |
| Form: NPK | `N`, `P`, `K` inputs; widget limits; values passed as model features | Grouped inputs with units/context and clear required label; explain feature bounds |
| Form: climate | `temperature`, `humidity`, `ph`, `rainfall`; widget limits | Grouped climate/soil pH controls with readable precision; label required ML fields |
| Optional farm details | `soil_texture`, `irrigation`, `location` strings | Optional context group with examples and explicit note that unverified qualitative comparisons may remain unknown |
| Input validation | Missing required names from form and `input_status`/`warnings` from engine | Inline/summary error state; no change to feature validation logic |
| Prediction cards | `model_predictions.random_forest`, `.svm`, `.ann` | Responsive, consistent model cards with crop labels; do not infer probability |
| Agreement summary | Per recommendation `ml_votes`, `model_agreement`; three `model_predictions` | Show agreement/difference using only the existing votes/text; ensure accessible text labels accompany color |
| Candidate/recommendation card | `crop`, `recommendation_category`, `reasoning`, `ml_votes`, `model_agreement` | Compact scan-first card; preserve category priority and candidate scope |
| Evidence/suitability | `agronomic_status`, `suitability_status`, `checks`, `unknown_evidence`, `insufficient_evidence`, `unavailable_rules`, `missing_information`, `invalid_information` | Separate status badges/labels; unknown means insufficient evidence, not a negative result |
| Per-parameter evidence | `parameter`, `input`, `assessment`, `evidence_status`, `effective_evidence_status`, claim, source, `unit`, `range_type`, context, limitations, verification status | Responsive detail rows/expanders rather than one extremely wide table; keep UNKNOWN values and limitations visible |
| Legacy history | `legacy_data_status`, `legacy_reference`, `legacy_unverified`, `legacy_conflicts` | Collapsible “Historical reference — not used for suitability” section; show conflicts explicitly without letting legacy data dominate the card |
| Verified source detail | `publication_title`, `author_or_institution`, `source_url`, `page_section_or_table`, `claim_or_requirement`, `growing_conditions_context`, `limitations`, `source_verified` | Clickable source with a text verification label, claim excerpt/description, context, units, and limits |
| Validation warnings | top-level `warnings`, `research_validation_errors`, `agronomic_warnings` | One consolidated, persistent warning area with distinct input/weather/evidence labels |
| Weather | `weather_context` from `WeatherClient`: status, location, values when available, source, retrieval timestamp, warnings | Human-readable status/observation panel; preserve missing values, source, and warnings; avoid raw JSON by default |
| No-data states | `input_status`, empty recommendations, missing weather, missing fields | Purposeful empty/error states explaining next action without framing UNKNOWN as crop failure |

## 5. Required files for the next implementation step

**Expected direct changes**

- `pages/1_Crop_Adviser.py` — layout, reusable rendering helpers if kept local, responsive styling, result/evidence/weather presentation.

**Inspect before deciding whether a change is needed**

- `app.py` — align the adviser styling with the existing green/white home-page theme without requiring a broad redesign.
- `src/recommendation_engine.py` — use its current response contract as the source for rendered values. Any desired field not currently returned must be treated as a data-contract change requiring explicit approval; do not fabricate it in the UI.
- `src/agronomic_rules.py` — preserve evidence and unknown semantics; UI implementation should not alter them.
- `tests/` — add or update focused page/helper tests only if an existing test harness covers Streamlit rendering; otherwise manually validate desktop and narrow viewport behaviour.

**Do not change as part of the UI implementation**

- ML artifacts, feature set, prediction logic, evidence rules, recommendation categories, or weather API logic.
- Existing source records or agronomic thresholds.

## 6. Risks to existing functionality

1. Refactoring result rendering can accidentally hide errors, warnings, unknown evidence, or source limitations. Keep all current warnings and status distinctions observable.
2. A visual “green/suitable” badge could imply a verified positive result when the engine returns `Cannot Determine`. Status must use explicit text and not color alone.
3. Showing only prediction cards without explaining candidate scope may imply all 22 crops were ranked. State the actual generated recommendation list’s scope.
4. Changing form widget keys, defaults, `value=None`, or numeric bounds can affect Streamlit session state and input validation.
5. Moving submission or result state can cause stale recommendations to remain after invalid submissions. Preserve or deliberately test current session-state behavior.
6. Responsive evidence rendering must not drop provenance, units, context, limitations, or historical conflict details.
7. Raw weather JSON currently exposes all payload fields; replacing it must retain status, source, timestamps, warnings, and missing-data meaning while avoiding accidental loss.
8. Shared styling changes in `app.py` can alter the landing page. Prefer page-scoped visual updates unless a shared theme is explicitly desired.
9. Streamlit DOM/CSS selectors using `data-testid` can be brittle across framework versions. Prefer native components and narrowly scoped styling.
10. Accessibility risks include small low-contrast labels, icon-only meaning, color-only status, keyboard/focus visibility, and table overflow.

## 7. Recommended implementation order

1. **Confirm response-contract inventory** — map each current UI field to the existing `RecommendationEngine.recommend` response; do not add or infer metrics.
2. **Set visual tokens and page header** — establish green/white palette, typography hierarchy, spacing, and card treatment scoped to the adviser page.
3. **Reorganize the input form** — group fields, clarify required vs optional, and explain model-domain bounds; retain exact input names, limits, and submission behavior.
4. **Build responsive prediction summary** — display ANN/RF/SVM outputs and agreement separately, without probability or confidence fabrication.
5. **Redesign recommendation cards** — make candidate, category, model agreement, evidence state, and suitability state independently scannable.
6. **Present agronomic evidence progressively** — compact parameter summaries with expandable source claim/context/limitations and a clearly labeled historical legacy section.
7. **Replace default raw weather JSON view** — human-readable fields and explicit status/unknown messaging, retaining all warnings and data provenance.
8. **Review validation and empty states** — test missing values, failed engine load, recommendation errors, no external weather, unavailable evidence, and unknown suitability.
9. **Validate desktop and mobile layouts** — use browser/screenshot checks at wide desktop and narrow phone widths; test table wrapping, stacked cards, focus, contrast, and keyboard navigation.
10. **Regression-check behaviour** — confirm form payload, ML prediction result structure, recommendation categories, warnings, source metadata, and session-state transitions are unchanged.

## Audit conclusion

The page already exposes the essential prediction, recommendation, evidence, and weather information and has the right semantic distinctions in several labels. The redesign should improve hierarchy, reduce dense presentation, clarify model-domain input limits, and make weather/evidence details easier to scan—while preserving the existing response values and prominent UNKNOWN/source limitations. No unsupported chart, suitability score, probability, or threshold is warranted by the current data.
