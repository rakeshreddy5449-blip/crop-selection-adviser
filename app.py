
import streamlit as st

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Crop Selection Adviser",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.stApp {
    background-color: #f5f9f3;
}

[data-testid="stSidebar"] {
    background-color: #153d2b;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.hero {
    background: linear-gradient(120deg, #123c2a, #26834c);
    padding: 55px 40px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    font-size: 42px;
}

.hero p {
    color: #e2f4e8;
    font-size: 18px;
}

.section-title {
    color: #174b30;
    font-size: 25px;
    font-weight: bold;
    margin-top: 25px;
}

.feature-card {
    background: white;
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #e0ebdf;
    min-height: 165px;
}

.feature-card h3 {
    color: #21633b;
}

.feature-card p {
    color: #526456;
}

.footer {
    text-align: center;
    color: #718176;
    padding: 30px;
}
/* Improve main content readability */
.stApp [data-testid="stAppViewContainer"] .stMarkdown p,
.stApp [data-testid="stAppViewContainer"] .stMarkdown li {
    color: #344b3b !important;
}

/* Improve model metric visibility */
[data-testid="stMetricLabel"] {
    color: #526456 !important;
}

[data-testid="stMetricValue"] {
    color: #174b30 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
   

    st.divider()
    st.caption("Project Version 1.0")

# ---------------- HERO SECTION ----------------
st.markdown("""
<div class="hero">
    <h1>🌱 AI-Powered Crop Selection Adviser</h1>
    <p>
        Intelligent crop recommendations using Artificial Intelligence,
        Machine Learning and Agronomic Knowledge.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------- INTRODUCTION ----------------
st.markdown(
    '<div class="section-title">Welcome to Smart Farming</div>',
    unsafe_allow_html=True
)

st.write("""
Choosing the right crop is an important decision in agriculture.
Our Crop Selection Adviser analyses soil nutrients, environmental
conditions and agronomic requirements to help farmers identify
suitable crops.
""")

# ---------------- FEATURE CARDS ----------------
st.markdown(
    '<div class="section-title">Our Key Features</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>🤖 AI Crop Prediction</h3>
        <p>Uses ANN, Random Forest and SVM models to identify suitable crops.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>🌿 Agronomic Analysis</h3>
        <p>Evaluates crop suitability using source-backed agricultural rules.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>🌦️ Weather Integration</h3>
        <p>Uses available weather information to provide additional context.</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------- MODEL OVERVIEW ----------------
st.markdown(
    '<div class="section-title">Machine Learning Models</div>',
    unsafe_allow_html=True
)

m1, m2, m3 = st.columns(3)

m1.metric("Model 1", "ANN")
m2.metric("Model 2", "Random Forest")
m3.metric("Model 3", "SVM")

# ---------------- PROJECT DETAILS ----------------
st.markdown(
    '<div class="section-title">Project Overview</div>',
    unsafe_allow_html=True
)

left, right = st.columns(2)

with left:
    st.info("""
    **Dataset Information**

    - 2,200 agricultural samples
    - 22 crop categories
    - 7 input features
    - No missing values in the curated dataset
    """)

with right:
    st.success("""
    **Recommendation Approach**

    - Machine Learning predictions
    - Model agreement analysis
    - Agronomic suitability evaluation
    - Weather context when available
    """)

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
    AI-Powered Crop Selection Adviser |
    Smart Agriculture Project
</div>
""", unsafe_allow_html=True)
