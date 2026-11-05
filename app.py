import json
from pathlib import Path

import altair as alt
import joblib
import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"

st.set_page_config(
    page_title="CropWise AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --cropwise-green: #176B3A;
        --cropwise-dark: #123D2B;
        --cropwise-light: #EAF5EC;
        --cropwise-background: #F7FAF7;
        --cropwise-border: #DCE9DE;
        --cropwise-muted: #5D7063;
    }

    .stApp {
        background: var(--cropwise-background);
        color: #183C28;
        font-family: "Segoe UI", Inter, Arial, sans-serif;
    }

    [data-testid="stAppViewContainer"] .main .block-container {
        max-width: 1440px;
        padding-top: clamp(1.25rem, 3vw, 2.5rem);
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid var(--cropwise-border);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: var(--cropwise-muted);
    }

    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: var(--cropwise-dark);
    }

    [data-testid="stSidebarNav"] {
        padding-top: 0.4rem;
    }

    [data-testid="stSidebarNav"] a {
        border-radius: 10px;
        margin: 3px 8px;
        transition: background-color 160ms ease, color 160ms ease;
    }

    [data-testid="stSidebarNav"] a:hover {
        background: var(--cropwise-light);
    }

    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: var(--cropwise-light);
        border-left: 4px solid var(--cropwise-green);
        color: var(--cropwise-dark);
        font-weight: 750;
    }

    [data-testid="stSidebarNav"] a[aria-current="page"] p,
    [data-testid="stSidebarNav"] a[aria-current="page"] span {
        color: var(--cropwise-dark);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        padding: 0 0.25rem;
    }

    h1, h2, h3 {
        color: var(--cropwise-dark) !important;
        letter-spacing: -0.02em;
    }

    h1 {
        font-size: clamp(1.75rem, 3vw, 2.4rem) !important;
        font-weight: 800 !important;
        line-height: 1.15 !important;
    }

    h2, h3 {
        font-weight: 720 !important;
    }

    .stMarkdown p,
    .stMarkdown li {
        color: #183C28;
        line-height: 1.65;
    }

    [data-testid="stCaptionContainer"] p {
        color: #526456;
        line-height: 1.5;
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] li {
        color: #183C28 !important;
        line-height: 1.55;
    }

    [data-testid="stExpander"] {
        border-color: var(--cropwise-border);
        border-radius: 12px;
        background: #ffffff;
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {
        color: var(--cropwise-dark) !important;
        font-weight: 650;
    }

    [data-testid="stButton"] button,
    [data-testid="stPageLink"] a {
        border-radius: 10px;
        transition: background-color 160ms ease, box-shadow 160ms ease,
            transform 160ms ease;
    }

    [data-testid="stButton"] button:hover,
    [data-testid="stPageLink"] a:hover {
        box-shadow: 0 5px 16px rgba(18, 61, 43, 0.12);
        transform: translateY(-1px);
    }

    .home-hero {
        padding: clamp(24px, 5vw, 46px);
        border: 1px solid var(--cropwise-border);
        border-radius: 20px;
        background: #ffffff;
        box-shadow: 0 8px 26px rgba(18, 61, 43, 0.06);
        margin-bottom: 24px;
    }

    .home-hero-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 20px;
    }

    .home-eyebrow {
        color: var(--cropwise-green);
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .home-hero h1 {
        color: var(--cropwise-dark);
        font-size: clamp(2rem, 4vw, 3rem);
        line-height: 1.12;
        margin: 10px 0;
    }

    .home-hero p {
        color: var(--cropwise-muted);
        font-size: 1.08rem;
        line-height: 1.65;
        max-width: 760px;
        margin-bottom: 0;
    }

    .overview-card {
        height: 100%;
        min-height: 148px;
        padding: 20px;
        border: 1px solid var(--cropwise-border);
        border-radius: 16px;
        background: #ffffff;
        box-shadow: 0 5px 18px rgba(18, 61, 43, 0.055);
    }

    .overview-card h3 {
        color: var(--cropwise-green);
        font-size: 1.03rem;
        margin: 0 0 9px;
    }

    .overview-card p {
        color: var(--cropwise-muted);
        line-height: 1.55;
        margin: 0;
    }

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--cropwise-border);
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 4px 16px rgba(18, 61, 43, 0.045);
    }

    [data-testid="stMetricLabel"] {
        color: var(--cropwise-muted);
    }

    [data-testid="stMetricLabel"] p {
        white-space: normal;
        overflow-wrap: anywhere;
    }

    [data-testid="stMetricValue"] {
        color: var(--cropwise-green);
        font-size: clamp(1.45rem, 2.8vw, 2.3rem);
    }

    .placeholder-panel {
        padding: clamp(22px, 4vw, 36px);
        border: 1px solid var(--cropwise-border);
        border-radius: 18px;
        background: #ffffff;
        box-shadow: 0 6px 22px rgba(18, 61, 43, 0.05);
    }

    .process-step {
        min-height: 190px;
        padding: 20px 18px;
        border: 1px solid #D6E6D9;
        border-top: 4px solid var(--cropwise-green);
        border-radius: 15px;
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FCF8 100%);
        box-shadow: 0 5px 18px rgba(18, 61, 43, 0.055);
    }

    .workflow-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
        align-items: stretch;
        gap: 14px;
    }

    .process-step strong {
        display: block;
        color: var(--cropwise-dark);
        font-size: 1.02rem;
        font-weight: 750;
        line-height: 1.35;
        margin: 8px 0;
    }

    .process-step .step-index {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 28px;
        border-radius: 8px;
        background: var(--cropwise-light);
        color: var(--cropwise-green);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.04em;
    }

    .process-step .step-description {
        display: block;
        color: #344D3A !important;
        font-size: 0.91rem;
        font-weight: 450;
        line-height: 1.58;
    }

    .model-card {
        height: 100%;
        min-height: 130px;
        padding: 18px;
        border: 1px solid var(--cropwise-border);
        border-radius: 14px;
        background: #ffffff;
    }

    .model-card h3 {
        font-size: 1.05rem;
        margin: 0 0 8px;
    }

    .model-card p {
        color: var(--cropwise-muted);
        line-height: 1.5;
        margin: 0;
    }

    .overview-card,
    .model-card,
    .process-step {
        transition: box-shadow 160ms ease, transform 160ms ease;
    }

    .overview-card:hover,
    .model-card:hover,
    .process-step:hover {
        box-shadow: 0 8px 22px rgba(18, 61, 43, 0.09);
        transform: translateY(-2px);
    }

    .sidebar-footer {
        margin-top: 1.5rem;
        padding: 12px;
        border-top: 1px solid var(--cropwise-border);
        color: var(--cropwise-muted);
        font-size: 0.78rem;
        line-height: 1.5;
    }

    .chart-note {
        padding: 14px 16px;
        border: 1px solid var(--cropwise-border);
        border-radius: 12px;
        background: #ffffff;
        color: #183C28;
    }

    @media (max-width: 640px) {
        .overview-card {
            min-height: auto;
        }

        [data-testid="stAppViewContainer"] .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def home_dashboard():
    st.markdown(
        """
        <section class="home-hero">
            <div class="home-eyebrow">AI-powered agricultural decision support</div>
            <h1>Welcome to CropWise AI</h1>
            <p>
                Explore machine-learning crop predictions and available
                agronomic evidence to support informed farm planning.
                Recommendations are decision-support information, not a
                guarantee of real-world crop success.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    action_columns = st.columns([1, 1, 3])
    with action_columns[0]:
        st.page_link(
            crop_adviser_page,
            label="Open Crop Adviser",
            icon="🌾",
        )
    with action_columns[1]:
        st.page_link(
            model_performance_nav_page,
            label="View Model Performance",
            icon="📈",
        )

    st.subheader("Project overview")
    st.write(
        "CropWise AI combines three trained machine-learning models—Artificial "
        "Neural Network (ANN), Random Forest, and Support Vector Machine "
        "(SVM)—to predict crops from soil and environmental measurements. "
        "The Crop Adviser presents those predictions separately from "
        "source-backed agronomic evidence."
    )

    metric_columns = st.columns(4)
    metric_columns[0].metric("Samples", "2,200")
    metric_columns[1].metric("Crop classes", "22")
    metric_columns[2].metric("ML models", "3")
    metric_columns[3].metric("Input features", "7")
    st.caption("Model input features: 7, as listed in the saved model metadata.")

    st.subheader("About the system")
    system_columns = st.columns(2)
    with system_columns[0]:
        st.markdown(
            """
            <div class="overview-card">
                <h3>🧠 Machine-learning predictions</h3>
                <p>
                    Artificial Neural Network, Random Forest and Support
                    Vector Machine models produce crop predictions from
                    the saved seven-feature input set.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with system_columns[1]:
        st.markdown(
            """
            <div class="overview-card">
                <h3>🌿 Agronomic evidence and weather context</h3>
                <p>
                    The adviser presents available source-backed agronomic
                    evidence separately from predictions and may show
                    external weather context when it is available.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("How it works")
    steps = [
        ("01 · Enter conditions", "Provide the soil and environmental measurements used by the models."),
        ("02 · Generate predictions", "ANN, Random Forest and SVM return their crop predictions."),
        ("03 · Compare model outputs", "The recommendation engine ranks candidate crops using existing model outputs."),
        ("04 · Review evidence", "Agronomic evidence is assessed independently; unknowns remain unknown."),
        ("05 · Read the result", "Review ranked recommendations, evidence limitations and available context."),
    ]
    _render_workflow_steps(steps)

    st.subheader("Model overview")
    model_columns = st.columns(3)
    model_overview = [
        ("🌳 Random Forest", "Ensemble classifier included in the existing model set."),
        ("🧭 Support Vector Machine", "SVM classifier included in the existing model set."),
        ("🧠 Artificial Neural Network", "ANN classifier included in the existing model set."),
    ]
    for column, (name, description) in zip(model_columns, model_overview):
        with column:
            st.markdown(
                f'<div class="model-card"><h3>{name}</h3>'
                f'<p>{description}</p></div>',
                unsafe_allow_html=True,
            )

    st.subheader("Explore CropWise AI")
    quick_links = st.columns(3)
    quick_link_pages = [
        (crop_adviser_page, "🌾 Crop Adviser", "Enter farm conditions and review recommendations."),
        (model_performance_nav_page, "📈 Model Performance", "Review saved aggregate evaluation metrics."),
        (detailed_analysis_nav_page, "🔎 Detailed Model Analysis", "Inspect available detailed evaluation data."),
    ]
    for column, (page, label, description) in zip(quick_links, quick_link_pages):
        with column:
            st.markdown(
                f'<div class="overview-card"><h3>{label}</h3>'
                f'<p>{description}</p></div>',
                unsafe_allow_html=True,
            )
            st.page_link(page, label=f"Open {label.split(' ', 1)[1]}")


@st.cache_data
def load_saved_evaluation():
    with (MODELS_DIR / "evaluation_results.json").open(
        "r", encoding="utf-8"
    ) as file:
        return json.load(file)


@st.cache_data
def load_model_metadata():
    with (MODELS_DIR / "metadata.json").open("r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_resource
def load_random_forest_for_analysis():
    return joblib.load(MODELS_DIR / "random_forest_model.joblib")


def _readable_model_name(model_key):
    return {
        "random_forest": "Random Forest",
        "svm": "SVM",
        "ann": "ANN",
    }.get(model_key, model_key.replace("_", " ").title())


def _format_percentage(value):
    return f"{float(value) * 100:.2f}%"


def _render_workflow_steps(steps):
    cards = "".join(
        f'<div class="process-step"><span class="step-index">{index:02d}</span>'
        f'<strong>{title}</strong>'
        f'<span class="step-description">{description}</span></div>'
        for index, (title, description) in enumerate(steps, start=1)
    )
    st.markdown(
        f'<div class="workflow-grid">{cards}</div>',
        unsafe_allow_html=True,
    )


def model_performance_dashboard():
    st.title("📈 Model Performance")
    st.caption(
        "Metrics below are read from the project's saved evaluation_results.json. "
        "They are historical evaluation results, not live performance estimates."
    )
    try:
        results = load_saved_evaluation()
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        st.error(f"Saved evaluation results could not be loaded: {error}")
        return

    required_models = ("random_forest", "svm", "ann")
    if not isinstance(results, dict) or any(
        not isinstance(results.get(key), dict) for key in required_models
    ):
        st.error("Saved evaluation results are missing one or more model records.")
        return
    if any("accuracy" not in results[key] for key in required_models):
        st.error("Saved evaluation results do not contain accuracy for every model.")
        return

    best_model = max(required_models, key=lambda key: float(results[key]["accuracy"]))
    st.subheader("Test accuracy")
    first_metrics_row = st.columns(2)
    for column, model_key in zip(first_metrics_row, required_models[:2]):
        with column:
            column.metric(
                _readable_model_name(model_key),
                _format_percentage(results[model_key]["accuracy"]),
                "Saved test accuracy",
            )
    second_metrics_row = st.columns(2)
    second_metrics_row[0].metric(
        _readable_model_name(required_models[2]),
        _format_percentage(results[required_models[2]]["accuracy"]),
        "Saved test accuracy",
    )
    with second_metrics_row[1]:
        second_metrics_row[1].metric(
            "Best recorded accuracy",
            _readable_model_name(best_model),
            _format_percentage(results[best_model]["accuracy"]),
        )

    metric_data = []
    for model_key in required_models:
        record = results[model_key]
        row = {"Model": _readable_model_name(model_key)}
        if "accuracy" in record:
            row["Test accuracy"] = float(record["accuracy"]) * 100
        if "macro_f1" in record:
            row["Macro F1"] = float(record["macro_f1"]) * 100
        metric_data.append(row)

    st.subheader("Saved test accuracy and macro F1")
    metric_long = pd.DataFrame(
        [
            {"Model": row["Model"], "Metric": metric, "Score": row[metric]}
            for row in metric_data
            for metric in ("Test accuracy", "Macro F1")
            if metric in row
        ]
    )
    performance_bars = (
        alt.Chart(metric_long)
        .mark_bar(cornerRadiusEnd=5)
        .encode(
            x=alt.X("Model:N", title=None, axis=alt.Axis(labelAngle=0)),
            xOffset=alt.XOffset("Metric:N"),
            y=alt.Y(
                "Score:Q",
                title="Score (%)",
                scale=alt.Scale(domain=[0, 100]),
            ),
            color=alt.Color(
                "Metric:N",
                title=None,
                scale=alt.Scale(
                    domain=["Test accuracy", "Macro F1"],
                    range=["#176B3A", "#72A982"],
                ),
            ),
            tooltip=[
                alt.Tooltip("Model:N"),
                alt.Tooltip("Metric:N"),
                alt.Tooltip("Score:Q", format=".2f"),
            ],
        )
        .properties(height=340, background="#F7FAF7")
        .configure_view(stroke=None)
        .configure_axis(
            labelColor="#344D3A",
            titleColor="#123D2B",
            gridColor="#DCE9DE",
            domainColor="#B8CDBD",
        )
        .configure_legend(labelColor="#344D3A")
    )
    st.altair_chart(performance_bars, width="stretch")
    st.caption(
        "Accuracy and macro F1 are separate recorded metrics. Neither is "
        "a probability that a crop will succeed on a particular farm."
    )

    st.subheader("Test accuracy comparison")
    accuracy_data = pd.DataFrame(
        [
            {
                "Model": _readable_model_name(model_key),
                "Test accuracy": float(results[model_key]["accuracy"]) * 100,
            }
            for model_key in required_models
        ]
    )
    accuracy_line = (
        alt.Chart(accuracy_data)
        .mark_line(
            point=alt.OverlayMarkDef(filled=True, size=110),
            color="#176B3A",
            strokeWidth=3,
        )
        .encode(
            x=alt.X(
                "Model:N",
                sort=[_readable_model_name(key) for key in required_models],
                title=None,
                axis=alt.Axis(labelAngle=0),
            ),
            y=alt.Y(
                "Test accuracy:Q",
                title="Saved test accuracy (%)",
                scale=alt.Scale(domain=[95, 100]),
            ),
            tooltip=[
                alt.Tooltip("Model:N"),
                alt.Tooltip("Test accuracy:Q", format=".2f"),
            ],
        )
        .properties(height=300, background="#F7FAF7")
        .configure_view(stroke=None)
        .configure_axis(
            labelColor="#344D3A",
            titleColor="#123D2B",
            gridColor="#DCE9DE",
            domainColor="#B8CDBD",
        )
    )
    st.altair_chart(accuracy_line, width="stretch")
    st.caption(
        "The axis is focused on 95–100% to show small differences. This is a "
        "category comparison, not a time series or a measure of real-world "
        "crop success."
    )

    st.subheader("Recorded validation or stability results")
    cv_records = []
    for model_key in required_models:
        record = results[model_key]
        mean_key = (
            "seed_stability_acc_mean"
            if model_key == "ann"
            else "cv_accuracy_mean"
        )
        std_key = (
            "seed_stability_acc_std"
            if model_key == "ann"
            else "cv_accuracy_std"
        )
        if mean_key in record and std_key in record:
            cv_records.append({
                "Model": _readable_model_name(model_key),
                "Evaluation type": (
                    "Multi-seed stability"
                    if model_key == "ann"
                    else "Cross-validation"
                ),
                "Mean accuracy": _format_percentage(record[mean_key]),
                "Standard deviation": _format_percentage(record[std_key]),
            })
    if cv_records:
        st.dataframe(
            cv_records,
            hide_index=True,
            width="stretch",
        )
    else:
        st.info("No cross-validation or stability results are recorded.")

    st.subheader("Evaluation details")
    detail_columns = st.columns(2)
    with detail_columns[0]:
        st.markdown(
            """
            <div class="overview-card">
                <h3>Best recorded test accuracy</h3>
                <p>
                    The model shown above is selected by comparing only the
                    saved test accuracy values in the evaluation file.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with detail_columns[1]:
        st.markdown(
            """
            <div class="overview-card">
                <h3>Unavailable saved measurements</h3>
                <p>
                    Training time, prediction latency, per-fold values,
                    and prediction counts are not present in the saved
                    evaluation records.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.info(
        "Precision and recall are not recorded in evaluation_results.json; "
        "a precision/recall comparison is therefore unavailable."
    )
    st.subheader("Evaluation methodology and available data")
    st.write(
        "This dashboard displays aggregate test accuracy, macro F1, and the "
        "saved validation or stability summaries. The saved evaluation file "
        "does not include per-sample labels, predictions, test-split details, "
        "or individual fold values, so no additional metrics are reconstructed."
    )
    st.caption(
        "The evaluation split details and per-sample predictions are not "
        "included with these aggregate records; no additional metrics are "
        "inferred here."
    )


def detailed_model_analysis_dashboard():
    st.title("🔎 Detailed Model Analysis")
    st.caption(
        "Detailed reports use only saved evaluation values and saved model "
        "artifacts. Models are not retrained on this page."
    )
    model_keys = ("random_forest", "svm", "ann")
    model_key = st.selectbox(
        "Select model",
        model_keys,
        format_func=_readable_model_name,
    )

    try:
        results = load_saved_evaluation()
        metadata = load_model_metadata()
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        st.error(f"Saved model analysis data could not be loaded: {error}")
        return

    record = results.get(model_key, {})
    summary_columns = st.columns(3)
    if "accuracy" in record:
        summary_columns[0].metric(
            "Test accuracy", _format_percentage(record["accuracy"])
        )
    if "macro_f1" in record:
        summary_columns[1].metric(
            "Macro F1", _format_percentage(record["macro_f1"])
        )
    mean_key = (
        "seed_stability_acc_mean"
        if model_key == "ann"
        else "cv_accuracy_mean"
    )
    std_key = (
        "seed_stability_acc_std"
        if model_key == "ann"
        else "cv_accuracy_std"
    )
    if mean_key in record and std_key in record:
        summary_columns[2].metric(
            "Recorded mean ± std",
            f"{_format_percentage(record[mean_key])} ± "
            f"{_format_percentage(record[std_key])}",
        )

    st.subheader("Per-class evaluation")
    st.info(
        "A confusion matrix, per-crop precision/recall/F1, and a classification "
        "report are unavailable because the project does not include saved "
        "test labels and per-sample predictions. These values cannot be "
        "reconstructed reliably from the aggregate metrics alone."
    )

    st.subheader("Feature importance")
    if model_key != "random_forest":
        st.info(
            "Feature importance is shown only when supported by the saved "
            "model artifact. No comparable feature-importance values are "
            "provided for this selected model."
        )
    else:
        try:
            model = load_random_forest_for_analysis()
            importances = getattr(model, "feature_importances_", None)
            features = metadata.get("features", [])
            if importances is None or len(importances) != len(features):
                st.info(
                    "The saved Random Forest artifact does not expose "
                    "feature importances aligned with the saved feature list."
                )
            else:
                importance_data = pd.DataFrame(
                    {
                        "Feature": features,
                        "Importance": importances,
                    }
                )
                feature_order = (
                    importance_data.sort_values("Importance", ascending=False)[
                        "Feature"
                    ].tolist()
                )
                importance_line = (
                    alt.Chart(importance_data)
                    .mark_line(
                        point=alt.OverlayMarkDef(filled=True, size=110),
                        color="#176B3A",
                        strokeWidth=3,
                    )
                    .encode(
                        x=alt.X(
                            "Feature:N",
                            sort=feature_order,
                            title="Model input feature",
                            axis=alt.Axis(labelAngle=-25),
                        ),
                        y=alt.Y(
                            "Importance:Q",
                            title="Relative feature importance",
                            scale=alt.Scale(zero=True),
                        ),
                        tooltip=[
                            alt.Tooltip("Feature:N"),
                            alt.Tooltip("Importance:Q", format=".4f"),
                        ],
                    )
                    .properties(height=360, background="#F7FAF7")
                    .configure_view(stroke=None)
                    .configure_axis(
                        labelColor="#344D3A",
                        titleColor="#123D2B",
                        gridColor="#DCE9DE",
                        domainColor="#B8CDBD",
                    )
                )
                st.altair_chart(importance_line, width="stretch")
                st.caption(
                    "Importances come directly from the saved Random Forest "
                    "artifact. The line connects ranked input features for "
                    "visual comparison; it is not a time trend or causal "
                    "agricultural relationship."
                )
        except (OSError, ValueError, AttributeError) as error:
            st.error(f"Saved Random Forest importances could not be read: {error}")

    st.subheader("Recorded results and interpretation")
    st.write(
        f"Saved test accuracy: "
        f"{_format_percentage(record['accuracy']) if 'accuracy' in record else 'Not recorded'}."
    )
    st.write(
        f"Saved macro F1: "
        f"{_format_percentage(record['macro_f1']) if 'macro_f1' in record else 'Not recorded'}."
    )
    if model_key == "ann" and mean_key in record:
        st.write(
            "The saved ANN stability fields are multi-seed mean and standard "
            "deviation; they are not reported as cross-validation folds."
        )
    elif mean_key in record:
        st.write(
            "The saved validation fields are cross-validation mean and "
            "standard deviation. Individual fold results are not available."
        )
    accuracy_order = sorted(
        (
            (key, float(value["accuracy"]))
            for key, value in results.items()
            if isinstance(value, dict) and "accuracy" in value
        ),
        key=lambda item: item[1],
        reverse=True,
    )
    if accuracy_order:
        rank = next(
            (index for index, (key, _) in enumerate(accuracy_order, 1)
             if key == model_key),
            None,
        )
        if rank is not None:
            st.write(
                f"Among the saved test-accuracy values, this model ranks "
                f"{rank} of {len(accuracy_order)}. This comparison does not "
                "establish real-world crop success."
            )
    strength_columns = st.columns(2)
    with strength_columns[0]:
        st.markdown(
            f"""
            <div class="overview-card">
                <h3>Recorded result</h3>
                <p>
                    {_readable_model_name(model_key)} ranks
                    {rank if accuracy_order else 'unavailable'} by saved
                    test accuracy among models with recorded accuracy.
                    This describes historical evaluation results only.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with strength_columns[1]:
        st.markdown(
            """
            <div class="overview-card">
                <h3>Evaluation limitation</h3>
                <p>
                    Per-class strengths and error patterns cannot be assessed
                    without saved test labels and per-sample predictions.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def about_project_dashboard():
    st.title("ℹ️ About CropWise AI")
    st.markdown(
        """
        <div class="home-hero">
            <div class="home-eyebrow">Intelligent Crop Selection Adviser</div>
            <h1>Supporting informed crop planning</h1>
            <p>
                CropWise AI is an academic crop selection adviser that
                presents trained machine-learning predictions alongside
                separately assessed agronomic evidence and optional
                external weather context.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Problem statement")
    st.write(
        "Selecting a crop from soil and environmental conditions involves "
        "multiple factors. This project provides model predictions and "
        "evidence-aware context while keeping the distinction between "
        "statistical prediction and agronomic suitability visible."
    )

    st.subheader("Project objectives")
    objectives = [
        "Generate crop predictions from the saved seven-feature model input.",
        "Compare ANN, Random Forest and SVM predictions.",
        "Present ranked recommendations without treating model agreement as success probability.",
        "Show source-backed agronomic evidence, unknowns and limitations separately.",
        "Provide external weather context when available without blocking recommendations.",
    ]
    st.markdown("\n".join(f"- {objective}" for objective in objectives))

    st.subheader("Proposed solution and recommendation methodology")
    st.write(
        "Farmer-provided measurements are passed through the existing trained "
        "models. Their predictions are combined by the recommendation engine "
        "to produce candidate rankings. The agronomic evidence engine reports "
        "verified claims or insufficient evidence; weather information is "
        "displayed as a separate context source."
    )

    st.subheader("System architecture and workflow")
    workflow = [
        ("Inputs", "N, P, K, temperature, humidity, pH and rainfall."),
        ("Predictions", "ANN, Random Forest and SVM use saved model artifacts."),
        ("Recommendation", "Existing engine ranks candidate crop predictions."),
        ("Evidence", "Research register statuses and limitations remain visible."),
        ("Context", "Weather values are shown only when returned by the service."),
    ]
    _render_workflow_steps(workflow)

    st.subheader("Dataset")
    st.write(
        "The project documentation records 2,200 samples, 22 crop classes, "
        "eight columns (seven model features and the crop label), and no "
        "missing or duplicate rows in the curated dataset."
    )
    try:
        metadata = load_model_metadata()
        st.write("**Saved model features:**", ", ".join(metadata.get("features", [])))
        st.write("**Saved model crop classes:**", len(metadata.get("classes", [])))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        st.warning(f"Saved model metadata could not be loaded: {error}")

    st.subheader("Machine-learning algorithms")
    algorithm_columns = st.columns(3)
    for column, (name, description) in zip(
        algorithm_columns,
        [
            ("Random Forest", "A tree-ensemble classifier in the saved model set."),
            ("Support Vector Machine", "A support-vector classifier in the saved model set."),
            ("Artificial Neural Network", "A neural-network classifier in the saved model set."),
        ],
    ):
        with column:
            st.markdown(
                f'<div class="model-card"><h3>{name}</h3>'
                f'<p>{description}</p></div>',
                unsafe_allow_html=True,
            )

    st.subheader("Agronomic evidence and weather")
    st.write(
        "The research register tracks pH, temperature, rainfall, soil texture "
        "and irrigation. UNKNOWN indicates that adequate evidence was not "
        "confirmed; it is not evidence that a crop has no requirement or is "
        "unsuitable. External weather data can provide temperature and "
        "humidity when returned; rainfall is not estimated when unavailable."
    )

    st.subheader("Technology stack")
    st.write(
        "Python, Streamlit, NumPy, pandas, scikit-learn, TensorFlow/Keras, "
        "Joblib and Requests, as listed in the project requirements and source."
    )

    st.subheader("Limitations")
    limitations = [
        "Model predictions reflect the trained dataset and do not guarantee field outcomes.",
        "Agronomic evidence coverage is incomplete; unknown evidence must not be interpreted as unsuitable.",
        "Weather retrieval depends on the external service and may be unavailable.",
        "Aggregate saved metrics do not include test predictions, per-crop metrics, training time or prediction latency.",
    ]
    st.markdown("\n".join(f"- {limitation}" for limitation in limitations))

    st.subheader("Potential future enhancements")
    st.write(
        "Possible future work includes expanding verified crop-specific "
        "evidence, making per-class evaluation outputs available, and "
        "improving decision-support explanations. These are future directions, "
        "not features claimed as complete."
    )


st.logo(str(ROOT / "assets" / "cropwise_brand.svg"), size="large")

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-footer">
            Intelligent Crop Selection Adviser<br>
            Predictions and evidence for decision support.
        </div>
        """,
        unsafe_allow_html=True,
    )

home_page = st.Page(
    home_dashboard,
    title="Home Dashboard",
    icon="🏠",
    default=True,
)
crop_adviser_page = st.Page(
    "pages/1_Crop_Adviser.py",
    title="Crop Adviser",
    icon="🌾",
)
model_performance_nav_page = st.Page(
    model_performance_dashboard,
    title="Model Performance",
    icon="📈",
)
detailed_analysis_nav_page = st.Page(
    detailed_model_analysis_dashboard,
    title="Detailed Model Analysis",
    icon="🔎",
)
about_project_nav_page = st.Page(
    about_project_dashboard,
    title="About Project",
    icon="ℹ️",
)

navigation = st.navigation(
    [
        home_page,
        crop_adviser_page,
        model_performance_nav_page,
        detailed_analysis_nav_page,
        about_project_nav_page,
    ],
    position="sidebar",
)
navigation.run()
