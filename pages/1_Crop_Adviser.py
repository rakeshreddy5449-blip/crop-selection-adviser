
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
    background-color: #f5f9f3;
}

/* Main headings */
h1, h2, h3, h4 {
    color: #174b30 !important;
}

/* General text */
.stMarkdown p,
.stMarkdown li {
    color: #344b3b !important;
}

/* Input field labels */
.stNumberInput label,
.stTextInput label,
[data-testid="stWidgetLabel"] p {
    color: #174b30 !important;
    font-weight: 700 !important;
    font-size: 16px !important;
}

/* Input boxes */
.stNumberInput input,
.stTextInput input {
    background-color: #ffffff !important;
    color: #173d29 !important;
    border: 1.5px solid #a8c9ae !important;
    border-radius: 9px !important;
    font-size: 16px !important;
}

/* Input box focus */
.stNumberInput input:focus,
.stTextInput input:focus {
    border: 2px solid #21864b !important;
}

/* Number input controls */
.stNumberInput button {
    background-color: #e5f2e7 !important;
    color: #174b30 !important;
}

/* Submit button */
.stButton > button,
.stFormSubmitButton > button {
    background-color: #187a43 !important;
    color: white !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
    padding: 12px !important;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 10px;
}
</style>


""", unsafe_allow_html=True)

# ---------------- LOAD ENGINE ----------------
@st.cache_resource
def load_engine():
    return RecommendationEngine(
        models_dir=str(ROOT / "models"),
        csv_path=str(ROOT / "reports" / "agronomic_requirements_sources.csv")
    )

st.title("🌾 AI Crop Adviser")
st.write(
    "Enter your farm's soil and environmental measurements "
    "to receive AI-powered crop recommendations."
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

    st.markdown("### Soil Nutrients")
    st.caption("Enter the NPK values from your soil test report.")

    c1, c2, c3 = st.columns(3)

    with c1:
        nitrogen = st.number_input(
            "Nitrogen (N)",
            min_value=0.0,
            max_value=140.0,
            value=None,
            step=1.0,
            format="%.2f"
        )

    with c2:
        phosphorus = st.number_input(
            "Phosphorus (P)",
            min_value=5.0,
            max_value=145.0,
            value=None,
            step=1.0,
            format="%.2f"
        )

    with c3:
        potassium = st.number_input(
            "Potassium (K)",
            min_value=5.0,
            max_value=205.0,
            value=None,
            step=1.0,
            format="%.2f"
        )

    st.markdown("### Environmental Conditions")
    st.caption("Enter the measured temperature, moisture and rainfall conditions.")

    c4, c5 = st.columns(2)

    with c4:
        temperature = st.number_input(
            "Temperature (°C)",
            min_value=8.825674745,
            max_value=43.67549305,
            value=None,
            step=0.5,
            format="%.2f"
        )

        humidity = st.number_input(
            "Humidity (%)",
            min_value=14.25803981,
            max_value=99.98187601,
            value=None,
            step=1.0,
            format="%.2f"
        )

    with c5:
        ph = st.number_input(
            "Soil pH",
            min_value=3.510404312,
            max_value=9.93509073,
            value=None,
            step=0.1,
            format="%.2f"
        )

        rainfall = st.number_input(
            "Rainfall (mm)",
            min_value=20.21126747,
            max_value=298.5601175,
            value=None,
            step=1.0,
            format="%.2f"
        )

    st.markdown("### Additional Farm Information")
    st.caption("These details are optional and help the agronomic suitability assessment.")

    c6, c7 = st.columns(2)

    with c6:
        soil_texture = st.text_input(
            "Soil Texture (Optional)",
            placeholder="Example: Loamy soil"
        )

    with c7:
        irrigation = st.text_input(
            "Irrigation Method (Optional)",
            placeholder="Example: Drip irrigation"
        )

    location = st.text_input(
        "Farm Location (Optional)",
        placeholder="Example: Warangal, Telangana"
    )

    submitted = st.form_submit_button(
        "🌾 Generate Crop Recommendations",
        use_container_width=True
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

            except Exception as e:
                st.error(f"Recommendation failed: {e}")
                st.session_state.pop("crop_result", None)


# ---------------- DISPLAY RESULTS ----------------
if "crop_result" in st.session_state:

    result = st.session_state["crop_result"]

    st.divider()
    st.header("📊 Crop Recommendation Results")

    if result["input_status"] != "VALID":
        st.error("The supplied inputs are insufficient for prediction.")

    else:

        # Warnings
        if result["warnings"]:
            st.warning("Important Information")
            for warning in result["warnings"]:
                st.write("•", warning)

        # Model Predictions
        st.subheader("🤖 Machine Learning Predictions")

        predictions = result["model_predictions"]

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "Random Forest",
            str(predictions["random_forest"]).title()
        )

        m2.metric(
            "SVM",
            str(predictions["svm"]).title()
        )

        m3.metric(
            "ANN",
            str(predictions["ann"]).title()
        )

        # Ranked recommendations
        st.subheader("🌾 Ranked Crop Recommendations")

        recommendations = result["ranked_recommendations"]

        if not recommendations:
            st.info("No crop recommendations are available.")
        else:

            for index, item in enumerate(recommendations, start=1):

                category = item["recommendation_category"]

                with st.expander(
                    f"{index}. {item['crop'].title()} — {category}",
                    expanded=(index == 1)
                ):

                    st.write(
                        "**Agronomic Status:**",
                        item["agronomic_status"]
                    )

                    st.write(
                        "**Model Agreement:**",
                        item["model_agreement"]
                    )

                    st.write(
                        "**Reasoning:**",
                        item["reasoning"]
                    )

                    if item.get("checks"):
                        st.write("**Agronomic Evidence:**")
                        evidence_rows = []
                        for check in item["checks"]:
                            if check.get("reference_available"):
                                reference = (
                                    f"{check['source_name']}: "
                                    f"{check['source_url']}"
                                )
                                reference_status = (
                                    "Not independently verified"
                                )
                            else:
                                reference = "No usable source reference"
                                reference_status = "Unavailable"
                            evidence_rows.append({
                                "Parameter": check["parameter"],
                                "Farmer input": check["input"],
                                "Assessment": check["assessment"],
                                "Explanation": check["reason"],
                                "Reference metadata": reference,
                                "Reference status": reference_status,
                            })
                        st.dataframe(
                            evidence_rows,
                            hide_index=True,
                            use_container_width=True
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

                    if item["sources"]:
                        st.write(
                            "**Reference metadata "
                            "(not independently verified):**"
                        )
                        for source in item["sources"]:
                            st.write(
                                f"• {source['source_name']}: "
                                f"{source['source_url']}"
                            )

        # Weather Information
        st.subheader("🌦️ Weather Context")

        weather = result.get("weather_context")

        if weather:
            st.json(weather)
        else:
            st.info(
                "No external weather information was requested. "
                "Recommendations use the farmer-provided measurements."
            )

        st.caption(
            "Recommendations are decision-support outputs, "
            "not guarantees of crop yield or harvest success."
        )
