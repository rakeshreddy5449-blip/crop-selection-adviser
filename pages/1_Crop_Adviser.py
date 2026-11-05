
from collections import Counter
from datetime import datetime
from html import escape
import math
import streamlit as st
import sys
import os
from pathlib import Path

# ---------------- PATH CONFIGURATION ----------------
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from recommendation_engine import RecommendationEngine

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Crop Adviser",
    page_icon="🌾",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""


<style>
.stApp {
    background-color: #F7FAF7;
}

/* Main headings */
h1, h2, h3, h4 {
    color: #123D2B !important;
}

/* General text */
.stMarkdown p,
.stMarkdown li {
    color: #183C28 !important;
}

/* Input field labels */
.stNumberInput label,
.stTextInput label,
[data-testid="stWidgetLabel"] p {
    color: #123D2B !important;
    font-weight: 700 !important;
    font-size: 0.94rem !important;
}

[data-testid="stForm"] {
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
}

[class*="st-key-cropwise-"][class*="-panel"] {
    padding: 1rem 1.1rem;
    border: 1px solid #DCE9DE;
    border-radius: 17px;
    background: linear-gradient(135deg, #FFFFFF 0%, #FBFDFC 100%);
    box-shadow: 0 6px 20px rgba(18, 61, 43, 0.055);
}

[class*="st-key-cropwise-"][class*="-panel"] [data-testid="stHorizontalBlock"] {
    flex-wrap: wrap;
    gap: 1rem;
}

[class*="st-key-cropwise-"][class*="-panel"] [data-testid="stColumn"] {
    flex: 1 1 220px !important;
    min-width: min(100%, 220px) !important;
}

.input-section-heading {
    color: #123D2B;
    font-size: 1.16rem;
    font-weight: 780;
    line-height: 1.3;
    margin: 0;
}

.input-section-caption {
    color: #5D7063;
    font-size: 0.9rem;
    line-height: 1.5;
    margin: 0;
}

/* Input boxes */
.stNumberInput input,
.stTextInput input {
    background-color: #ffffff !important;
    color: #183C28 !important;
    border: 1.5px solid #A8C9AE !important;
    border-radius: 11px !important;
    min-height: 2.8rem;
    font-size: 0.96rem !important;
}

.stNumberInput input::placeholder,
.stTextInput input::placeholder {
    color: #718176 !important;
    opacity: 1 !important;
}

/* Input box focus */
.stNumberInput input:focus,
.stTextInput input:focus {
    border: 2px solid #176B3A !important;
}

/* Number input controls */
.stNumberInput button {
    background-color: #EAF5EC !important;
    color: #123D2B !important;
}

/* Submit button */
.stFormSubmitButton > button {
    background-color: #176B3A !important;
    color: white !important;
    border: 1px solid #176B3A !important;
    border-radius: 13px !important;
    min-height: 3.2rem;
    font-size: 1rem !important;
    font-weight: 750 !important;
    padding: 12px 20px !important;
    box-shadow: 0 5px 14px rgba(23, 107, 58, 0.18);
    transition: background-color 160ms ease, box-shadow 160ms ease,
        transform 160ms ease;
}

.stFormSubmitButton > button:hover {
    background-color: #123D2B !important;
    border-color: #123D2B !important;
    box-shadow: 0 7px 18px rgba(18, 61, 43, 0.22);
    transform: translateY(-1px);
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 10px;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] li {
    color: #183C28 !important;
    line-height: 1.55;
}

[data-testid="stCaptionContainer"] p {
    color: #526456 !important;
    line-height: 1.5;
}

[data-testid="stExpander"] {
    border-color: #DCE8DE;
    border-radius: 12px;
    background: #ffffff;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p {
    color: #123D2B !important;
}

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    max-width: 100%;
}

.prediction-card {
    background: #ffffff;
    border: 1px solid #DCE8DE;
    border-top: 5px solid var(--model-accent);
    border-radius: 14px;
    padding: 20px;
    min-height: 150px;
    box-shadow: 0 4px 14px rgba(18, 61, 43, 0.07);
}

.prediction-card-label {
    color: #526456;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.prediction-card-crop {
    color: #123D2B;
    font-size: clamp(1.25rem, 2vw, 1.7rem);
    font-weight: 750;
    line-height: 1.25;
    margin-top: 14px;
    overflow-wrap: anywhere;
}

.prediction-card-footnote {
    color: #526456;
    font-size: 0.88rem;
    margin-top: 8px;
}

.agreement-card {
    background: #ffffff;
    border: 1px solid #DCE8DE;
    border-radius: 12px;
    padding: 15px 17px;
    min-height: 95px;
}

.agreement-crop {
    color: #123D2B;
    font-size: 1.05rem;
    font-weight: 700;
}

.agreement-count {
    color: #526456;
    font-size: 0.9rem;
    margin-top: 5px;
}

.recommendation-card {
    background: #ffffff;
    border: 1px solid #DCE8DE;
    border-left: 6px solid var(--recommendation-accent);
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(18, 61, 43, 0.07);
}

.recommendation-card-heading {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
}

.recommendation-rank {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 42px;
    height: 42px;
    border-radius: 12px;
    background: #EAF5EC;
    color: #123D2B;
    font-weight: 800;
}

.recommendation-crop {
    color: #123D2B;
    font-size: clamp(1.2rem, 2vw, 1.55rem);
    font-weight: 750;
    overflow-wrap: anywhere;
}

.recommendation-category {
    margin-left: auto;
    padding: 6px 10px;
    border-radius: 999px;
    color: #123D2B;
    background: #EAF5EC;
    font-size: 0.78rem;
    font-weight: 750;
    text-align: center;
}

.recommendation-category-caution {
    color: #654400;
    background: #FFF4D6;
}

.recommendation-category-insufficient {
    color: #24465F;
    background: #E8F1FC;
}

.recommendation-category-not-recommended {
    color: #7A2525;
    background: #FDE8E7;
}

.recommendation-summary-label {
    color: #526456;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.weather-card {
    background: #ffffff;
    border: 1px solid #DCE8DE;
    border-top: 4px solid #176B3A;
    border-radius: 12px;
    padding: 14px 16px;
    box-shadow: 0 4px 14px rgba(18, 61, 43, 0.06);
}

.weather-card-label {
    color: #526456;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

@media (max-width: 640px) {
    .prediction-card {
        min-height: auto;
        padding: 16px;
    }

    .agreement-card {
        min-height: auto;
    }

    .recommendation-card {
        padding: 15px;
    }

    .recommendation-category {
        margin-left: 0;
    }

    .weather-card {
        padding: 12px;
    }

    .recommendation-summary-label {
        margin-top: 8px;
    }

    [class*="st-key-cropwise-"][class*="-panel"] {
        border-radius: 14px !important;
        padding: 0.85rem;
    }

    .input-section-heading {
        font-size: 1.05rem;
    }
}

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        transition-duration: 0.01ms !important;
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
    }
}
</style>


""", unsafe_allow_html=True)

# ---------------- LOAD ENGINE ----------------
@st.cache_resource
def load_engine():
    return RecommendationEngine(
        models_dir=str(ROOT / "models"),
        csv_path=str(ROOT / "reports" / "agronomic_requirements_sources.csv"),
        research_csv_path=str(
            ROOT / "reports" / "agronomic_evidence_research.csv"
        )
    )

st.title("🌾 Crop Adviser")
st.write(
    "Enter soil and environmental measurements to review model predictions, "
    "ranked crop recommendations, agronomic evidence, and optional weather context."
)

try:
    engine = load_engine()
    st.success("Recommendation Engine is ready.")
except Exception as e:
    st.error(f"Could not load recommendation engine: {e}")
    st.stop()

st.divider()

# ---------------- FARMER INPUT FORM ----------------
st.subheader("🌱 Farm Information")

with st.form("crop_adviser_main_form"):

    st.info(
        "Enter actual measurements from your soil test "
        "and farm conditions. All numeric limits below "
        "are based on the model training dataset."
    )

    with st.container(border=True, key="cropwise-npk-panel"):
        st.markdown(
            '<p class="input-section-heading">🌱 Soil Nutrients (NPK)</p>'
            '<p class="input-section-caption">'
            "Enter the nutrient values from your soil test report."
            "</p>",
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            nitrogen = st.number_input(
                "Nitrogen (N)",
                min_value=0.0,
                max_value=140.0,
                value=None,
                step=1.0,
                format="%.2f",
                placeholder="Enter nitrogen value",
                help="Enter the nitrogen value from your soil test report.",
            )

        with c2:
            phosphorus = st.number_input(
                "Phosphorus (P)",
                min_value=5.0,
                max_value=145.0,
                value=None,
                step=1.0,
                format="%.2f",
                placeholder="Enter phosphorus value",
                help="Enter the phosphorus value from your soil test report.",
            )

        with c3:
            potassium = st.number_input(
                "Potassium (K)",
                min_value=5.0,
                max_value=205.0,
                value=None,
                step=1.0,
                format="%.2f",
                placeholder="Enter potassium value",
                help="Enter the potassium value from your soil test report.",
            )

    with st.container(border=True, key="cropwise-environment-panel"):
        st.markdown(
            '<p class="input-section-heading">🌡️ Environmental Conditions</p>'
            '<p class="input-section-caption">'
            "Enter measured temperature, humidity, soil pH and rainfall."
            "</p>",
            unsafe_allow_html=True,
        )

        c4, c5 = st.columns(2)

        with c4:
            temperature = st.number_input(
                "Temperature (°C)",
                min_value=8.825674745,
                max_value=43.67549305,
                value=None,
                step=0.5,
                format="%.2f",
                placeholder="e.g., 28.5",
                help="Enter the measured temperature in degrees Celsius.",
            )

            humidity = st.number_input(
                "Humidity (%)",
                min_value=14.25803981,
                max_value=99.98187601,
                value=None,
                step=1.0,
                format="%.2f",
                placeholder="e.g., 75",
                help="Enter the measured relative humidity percentage.",
            )

        with c5:
            ph = st.number_input(
                "Soil pH",
                min_value=3.510404312,
                max_value=9.93509073,
                value=None,
                step=0.1,
                format="%.2f",
                placeholder="e.g., 6.5",
                help="Enter the measured soil pH value.",
            )

            rainfall = st.number_input(
                "Rainfall (mm)",
                min_value=20.21126747,
                max_value=298.5601175,
                value=None,
                step=1.0,
                format="%.2f",
                placeholder="e.g., 120",
                help="Enter the rainfall value used for the model input.",
            )

    with st.container(border=True, key="cropwise-additional-panel"):
        st.markdown(
            '<p class="input-section-heading">🚜 Additional Farm Information</p>'
            '<p class="input-section-caption">'
            "Optional details support the evidence-aware agronomic assessment."
            "</p>",
            unsafe_allow_html=True,
        )

        c6, c7 = st.columns(2)

        with c6:
            soil_texture = st.text_input(
                "Soil Texture (Optional)",
                placeholder="Example: Loamy soil",
                help="Describe your soil texture if known.",
            )

        with c7:
            irrigation = st.text_input(
                "Irrigation Method (Optional)",
                placeholder="Example: Drip irrigation",
                help="Describe the irrigation method used on the farm.",
            )

        location = st.text_input(
            "Farm Location (Optional)",
            placeholder="Example: Warangal, Telangana",
            help="A location can be used to request optional weather context.",
        )

    submitted = st.form_submit_button(
        "🌱  Generate Crop Recommendations  →",
        width="stretch"
    )

# ---------------- RECOMMENDATION PROCESS ----------------

if submitted:

    required_inputs = {
        "N": nitrogen,
        "P": phosphorus,
        "K": potassium,
        "temperature": temperature,
        "humidity": humidity,
        "ph": ph,
        "rainfall": rainfall
    }

    missing = [
        name for name, value in required_inputs.items()
        if value is None
    ]

    if missing:
        st.error(
            "Please enter all required measurements: "
            + ", ".join(missing)
        )

    else:
        farmer_inputs = {
            **required_inputs
        }

        if soil_texture.strip():
            farmer_inputs["soil_texture"] = soil_texture.strip()

        if irrigation.strip():
            farmer_inputs["irrigation"] = irrigation.strip()

        with st.spinner(
            "Analyzing farm conditions and predicting crops..."
        ):
            try:
                result = engine.recommend(
                    farmer_inputs,
                    location=location.strip() or None
                )

                st.session_state["crop_result"] = result
                st.session_state["crop_farmer_inputs"] = dict(farmer_inputs)

            except Exception as e:
                st.error(f"Recommendation failed: {e}")
                st.session_state.pop("crop_result", None)
                st.session_state.pop("crop_farmer_inputs", None)


# ---------------- DISPLAY RESULTS ----------------
if "crop_result" in st.session_state:

    result = st.session_state["crop_result"]

    st.divider()
    st.header("📊 Crop Recommendation Results")

    if result.get("warnings"):
        st.warning("Important Information")
        for warning in result["warnings"]:
            st.write("•", warning)

    if result["input_status"] != "VALID":
        st.error("The supplied inputs are insufficient for prediction.")
        if result.get("missing_inputs"):
            st.write(
                "**Missing required inputs:** "
                + ", ".join(result["missing_inputs"])
            )
        if result.get("invalid_inputs"):
            st.write(
                "**Invalid inputs:** "
                + ", ".join(result["invalid_inputs"])
            )

    else:
        # Model Predictions
        st.subheader("🤖 Machine Learning Predictions")

        predictions = result["model_predictions"]
        model_cards = [
            ("random_forest", "Random Forest", "#21864b"),
            ("svm", "Support Vector Machine (SVM)", "#167c80"),
            ("ann", "Artificial Neural Network (ANN)", "#b77b18"),
        ]
        model_columns = st.columns(3)

        for column, (key, model_name, accent) in zip(
            model_columns, model_cards
        ):
            predicted_crop = escape(str(predictions[key]).title())
            with column:
                st.markdown(
                    f"""
                    <div class="prediction-card"
                         style="--model-accent: {accent};">
                        <div class="prediction-card-label">{model_name}</div>
                        <div class="prediction-card-crop">{predicted_crop}</div>
                        <div class="prediction-card-footnote">
                            Predicted crop
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        prediction_counts = Counter(
            str(predictions[key])
            for key, _, _ in model_cards
        )
        agreement_crops = sorted(
            prediction_counts,
            key=lambda crop: (-prediction_counts[crop], crop.lower()),
        )
        st.markdown("#### Model agreement")
        st.caption(
            "Counts show how many of the three models predicted each crop. "
            "Agreement is not a probability of crop success."
        )

        agreement_columns = st.columns(max(1, len(agreement_crops)))
        for column, crop in zip(agreement_columns, agreement_crops):
            supporting_models = [
                name
                for key, name, _ in model_cards
                if str(predictions[key]) == crop
            ]
            with column:
                st.markdown(
                    f"""
                    <div class="agreement-card">
                        <div class="agreement-crop">
                            {escape(crop.title())}
                        </div>
                        <div class="agreement-count">
                            {len(supporting_models)} of 3 models
                        </div>
                        <div class="agreement-count">
                            {escape(", ".join(supporting_models))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        if len(agreement_crops) > 1:
            disagreement = " · ".join(
                f"{prediction_counts[crop]}/3: {crop.title()}"
                for crop in agreement_crops
            )
            st.info(
                "The models disagree: "
                f"{disagreement}. These counts describe model predictions "
                "only; they do not establish agronomic suitability."
            )
        else:
            st.success(
                "All three models predict the same crop. This is model "
                "agreement, not a probability or guarantee of crop success."
            )

        # Ranked recommendations
        st.subheader("🌾 Ranked Crop Recommendations")
        st.subheader("🌿 Agronomic Evidence & Suitability")
        st.caption(
            "ML predictions are learned from the training dataset. Agronomic "
            "evidence is source-backed information about crop requirements; "
            "it is assessed separately and does not change the ML prediction."
        )
        st.caption(
            "These predictions do not guarantee real-world crop success."
        )

        recommendations = result["ranked_recommendations"]

        if not recommendations:
            st.info("No crop recommendations are available.")
        else:

            for index, item in enumerate(recommendations, start=1):
                category = item["recommendation_category"]
                normalized_category = category.upper()
                category_class = {
                    "RECOMMENDED WITH CAUTION":
                        "recommendation-category-caution",
                    "INSUFFICIENT INFORMATION":
                        "recommendation-category-insufficient",
                    "NOT RECOMMENDED":
                        "recommendation-category-not-recommended",
                }.get(normalized_category, "")
                category_class_attribute = (
                    f" {category_class}" if category_class else ""
                )
                category_accent = {
                    "RECOMMENDED WITH CAUTION": "#b77b18",
                    "INSUFFICIENT INFORMATION": "#47728f",
                    "NOT RECOMMENDED": "#b34c4c",
                }.get(normalized_category, "#21864b")
                crop_name = str(item["crop"])
                crop_key = crop_name.casefold()
                model_support = sum(
                    1
                    for prediction in predictions.values()
                    if str(prediction).casefold() == crop_key
                )
                suitability = item.get(
                    "suitability_status", "Cannot Determine"
                )
                unknown_evidence = item.get(
                    "unknown_evidence",
                    item.get("insufficient_evidence", [])
                )

                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div class="recommendation-card"
                             style="--recommendation-accent: {category_accent};">
                            <div class="recommendation-card-heading">
                                <span class="recommendation-rank">
                                    #{index}
                                </span>
                                <span class="recommendation-crop">
                                    {escape(crop_name.title())}
                                </span>
                                <span class="recommendation-category{category_class_attribute}">
                                    {escape(category)}
                                </span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    summary_columns = st.columns(3)
                    with summary_columns[0]:
                        st.markdown(
                            '<div class="recommendation-summary-label">'
                            'ML model support</div>',
                            unsafe_allow_html=True,
                        )
                        st.write(f"**{model_support} of 3 models**")
                        st.caption(
                            "Agreement among model predictions only."
                        )
                    with summary_columns[1]:
                        st.markdown(
                            '<div class="recommendation-summary-label">'
                            'Agronomic evidence</div>',
                            unsafe_allow_html=True,
                        )
                        st.write(item["agronomic_status"])
                    with summary_columns[2]:
                        st.markdown(
                            '<div class="recommendation-summary-label">'
                            'Agronomic suitability</div>',
                            unsafe_allow_html=True,
                        )
                        st.write(suitability)

                    if unknown_evidence:
                        st.info(
                            "Evidence is unknown for: "
                            f"{', '.join(unknown_evidence)}. UNKNOWN means "
                            "evidence was not verified; it does not mean "
                            "the crop is unsuitable."
                        )

                    if item.get("legacy_conflicts"):
                        st.warning(
                            "Legacy values conflict with the research "
                            "register for: "
                            f"{', '.join(item['legacy_conflicts'])}. "
                            "Historical values are retained but are not "
                            "used to determine suitability."
                        )

                    if item.get("research_validation_errors"):
                        st.warning(
                            "Research register validation issues were "
                            "found; affected parameters are treated as "
                            "UNKNOWN."
                        )

                    with st.expander(
                        "View agronomic evidence details and reasoning",
                        expanded=(index == 1),
                    ):
                        st.markdown("#### Evidence status by parameter")
                        st.caption(
                            "UNKNOWN means evidence has not been adequately "
                            "confirmed. It does not mean the crop is "
                            "unsuitable. A CONFLICTING effective status means "
                            "historical values conflict with the research "
                            "register; those values do not establish "
                            "suitability."
                        )

                        checks = item.get("checks", [])
                        verified_parameters = [
                            check["parameter"]
                            for check in checks
                            if check.get("evidence_status") == "VERIFIED"
                        ]
                        unknown_parameters = [
                            check["parameter"]
                            for check in checks
                            if check.get("evidence_status") == "UNKNOWN"
                        ]
                        conflicting_parameters = [
                            check["parameter"]
                            for check in checks
                            if check.get("effective_evidence_status")
                            == "CONFLICTING"
                        ]
                        status_columns = st.columns(3)
                        with status_columns[0]:
                            st.markdown("**VERIFIED source evidence**")
                            st.write(
                                ", ".join(verified_parameters)
                                if verified_parameters
                                else "None"
                            )
                        with status_columns[1]:
                            st.markdown("**UNKNOWN evidence**")
                            st.write(
                                ", ".join(unknown_parameters)
                                if unknown_parameters
                                else "None"
                            )
                        with status_columns[2]:
                            st.markdown("**CONFLICTING effective status**")
                            st.write(
                                ", ".join(conflicting_parameters)
                                if conflicting_parameters
                                else "None"
                            )

                        if (
                            str(item["crop"]).casefold() == "rice"
                            and any(
                                check.get("parameter") == "irrigation"
                                and check.get("evidence_status") == "VERIFIED"
                                for check in checks
                            )
                        ):
                            st.info(
                                "Rice irrigation evidence is specific to "
                                "irrigated lowland rice and reports "
                                "context-dependent seasonal field water input. "
                                "It is not a universal irrigation threshold "
                                "and must not be interpreted as a rainfall "
                                "requirement."
                            )

                        st.write(
                            "**Model Agreement (prediction only):**",
                            item["model_agreement"],
                        )
                        st.write("**Reasoning:**", item["reasoning"])

                        if checks:
                            st.info(
                                "UNKNOWN means evidence was not verified. "
                                "It is not a finding that the crop is "
                                "unsuitable."
                            )
                            st.write("**Evidence by Parameter:**")
                            evidence_rows = []
                            for check in checks:
                                if check.get("source_verified"):
                                    reference = (
                                        f"{check.get('author_or_institution')}: "
                                        f"{check.get('publication_title')} — "
                                        f"{check.get('source_url')} "
                                        f"({check.get('page_section_or_table')})"
                                    )
                                    claim = check.get(
                                        "claim_or_requirement"
                                    )
                                    claim_status = "Verified source claim"
                                else:
                                    reference = (
                                        f"Unverified reference: "
                                        f"{check.get('source_name') or 'Unknown'} "
                                        f"{check.get('source_url') or ''}"
                                    )
                                    claim = (
                                        f"Unverified: "
                                        f"{check.get('claim_or_requirement')}"
                                        if check.get("claim_or_requirement")
                                        else "UNKNOWN — evidence not verified"
                                    )
                                    claim_status = "Not verified"
                                evidence_rows.append({
                                    "Parameter": check["parameter"],
                                    "Farmer input": check["input"],
                                    "Research register status": check.get(
                                        "evidence_status", "UNKNOWN"
                                    ),
                                    "Effective evidence status": check.get(
                                        "effective_evidence_status", "UNKNOWN"
                                    ),
                                    "Source content status": claim_status,
                                    "Suitability assessment": check["assessment"],
                                    "Verified claim": claim,
                                    "Source": reference,
                                    "Growing context": (
                                        check.get(
                                            "growing_conditions_context"
                                        )
                                        or "No verified claim available."
                                    ),
                                    "Source limitations": (
                                        check.get("limitations")
                                        or "None recorded."
                                    ),
                                    "Legacy data status": check.get(
                                        "legacy_data_status"
                                    ),
                                    "Historical legacy data (not used)": (
                                        str(check.get("legacy_reference"))
                                        if check.get("legacy_reference")
                                        else "None"
                                    ),
                                })
                            st.dataframe(
                                evidence_rows,
                                hide_index=True,
                                width="stretch",
                            )

                        if item["missing_information"]:
                            st.write("**Missing Farmer Inputs:**")
                            for missing in item["missing_information"]:
                                st.write("•", missing)

                        if item.get("unavailable_rules"):
                            st.write("**Unavailable Crop-Specific Rules:**")
                            for parameter in item["unavailable_rules"]:
                                st.write("•", parameter)

                        if item.get("insufficient_evidence"):
                            st.write("**Insufficient Agronomic Evidence:**")
                            for parameter in item["insufficient_evidence"]:
                                st.write("•", parameter)

                        if item.get("invalid_information"):
                            st.warning(
                                "Some farmer-provided information could not "
                                "be assessed: "
                                f"{', '.join(item['invalid_information'])}."
                            )

                        if item.get("legacy_unverified"):
                            st.caption(
                                "Legacy requirements exist for "
                                f"{', '.join(item['legacy_unverified'])}, "
                                "but they are retained as historical "
                                "reference only and do not determine "
                                "suitability."
                            )

                        if item.get("legacy_conflicts"):
                            st.warning(
                                "Legacy numerical values conflict with the "
                                "research register for: "
                                f"{', '.join(item['legacy_conflicts'])}. "
                                "They are retained for history and not used."
                            )

                        if item.get("research_validation_errors"):
                            st.warning(
                                "Research register validation issues were "
                                "found; affected parameters are treated as "
                                "UNKNOWN."
                            )

                        if item.get("agronomic_warnings"):
                            for warning in item["agronomic_warnings"]:
                                st.warning(warning)

        # Weather Information
        st.subheader("🌦️ Weather Context")
        st.caption(
            "External weather is contextual information only. It is shown "
            "separately from your submitted farm measurements, ML predictions, "
            "and agronomic suitability."
        )

        weather = result.get("weather_context")

        if isinstance(weather, dict):
            weather_status = str(weather.get("status") or "UNKNOWN").upper()
            status_messages = {
                "SUCCESS": "Weather data retrieved successfully.",
                "TIMEOUT": "The weather service did not respond in time.",
                "AUTH_FAILURE": "The weather service denied the request.",
                "API_FAILURE": "The weather service could not provide data.",
                "FAILURE": "Weather data could not be retrieved.",
            }
            if weather_status == "SUCCESS":
                st.success(status_messages["SUCCESS"])
            else:
                st.info(
                    status_messages.get(
                        weather_status,
                        "Weather retrieval status is unavailable; external "
                        "measurements are not shown.",
                    )
                )

            source_details = []
            if weather.get("weather_source"):
                source_details.append(
                    f"Source: {weather['weather_source']}"
                )
            if weather.get("location"):
                source_details.append(f"Location: {weather['location']}")
            retrieved_at = weather.get("retrieved_at")
            if retrieved_at:
                try:
                    retrieved_time = datetime.fromtimestamp(
                        float(retrieved_at)
                    ).astimezone()
                    retrieved_label = retrieved_time.strftime(
                        "%Y-%m-%d %H:%M %Z"
                    )
                except (TypeError, ValueError, OverflowError, OSError):
                    retrieved_label = str(retrieved_at)
                source_details.append(f"Retrieved: {retrieved_label}")
            if source_details:
                st.caption(" · ".join(source_details))

            submitted_measurements = st.session_state.get(
                "crop_farmer_inputs", {}
            )
            external_measurements = {}
            if weather_status == "SUCCESS":
                for field in ("temperature", "humidity", "rainfall"):
                    raw_value = weather.get(field)
                    if raw_value is None:
                        external_measurements[field] = None
                        continue
                    try:
                        numeric_value = float(raw_value)
                    except (TypeError, ValueError, OverflowError):
                        numeric_value = None
                    external_measurements[field] = (
                        numeric_value
                        if numeric_value is not None
                        and math.isfinite(numeric_value)
                        else None
                    )

            weather_columns = st.columns(3)
            weather_fields = (
                ("temperature", "Temperature", "°C"),
                ("humidity", "Humidity", "%"),
                ("rainfall", "Rainfall", "mm"),
            )
            for column, (field, label, unit) in zip(
                weather_columns, weather_fields
            ):
                external_value = external_measurements.get(field)
                with column:
                    st.markdown(
                        f'<div class="weather-card">'
                        f'<div class="weather-card-label">'
                        f'External {label}</div></div>',
                        unsafe_allow_html=True,
                    )
                    if external_value is not None:
                        st.metric(label, f"{external_value:g} {unit}")
                    elif weather_status == "SUCCESS":
                        st.write("Not reported by the weather source")
                    else:
                        st.write("Unavailable")

            if weather_status == "SUCCESS" and external_measurements.get(
                "rainfall"
            ) is None:
                st.caption(
                    "No reliable external rainfall measurement was provided; "
                    "rainfall is not estimated."
                )

            if submitted_measurements:
                st.markdown("**Your submitted farm measurements**")
                submitted_columns = st.columns(3)
                for column, (field, label, unit) in zip(
                    submitted_columns, weather_fields
                ):
                    submitted_value = submitted_measurements.get(field)
                    with column:
                        if submitted_value is not None:
                            st.caption(
                                f"Farmer-entered {label}: "
                                f"{submitted_value} {unit}"
                            )

            weather_warnings = weather.get("warnings") or []
            if isinstance(weather_warnings, str):
                weather_warnings = [weather_warnings]
            for warning in weather_warnings:
                st.warning(str(warning))
        else:
            st.info(
                "External weather data is unavailable or was not requested. "
                "Crop recommendations remain based on your submitted farm "
                "measurements and are not blocked by this."
            )

        st.caption(
            "Recommendations are decision-support outputs, "
            "not guarantees of crop yield or harvest success."
        )
