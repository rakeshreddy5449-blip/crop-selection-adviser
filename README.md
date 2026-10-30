# AI-Powered Crop Selection Adviser

An AI-based crop recommendation system that combines machine learning models with a source-backed agronomic suitability engine.

The system uses **Artificial Neural Network (ANN)** as the primary machine-learning model and compares it with **Random Forest (RF)** and **Support Vector Machine (SVM)** models.

## Project Status

**Current development stage: Stage 3.4 — External Weather Data Integration**

Stage 3.4 functionality has been implemented and tested.

The Streamlit dashboard (Stage 3.5) has **not yet been started**.

---

## 1. Project Objectives

The system is designed to:

- Recommend suitable crops from available farm conditions.
- Rank candidate crops using machine-learning predictions and agronomic rules.
- Explain why a crop is recommended or rejected.
- Identify insufficient or missing information.
- Compare ANN, Random Forest, and SVM models.
- Integrate external weather information when available.
- Keep agronomic suitability rules separate from the machine-learning model.
- Avoid presenting machine-learning scores as guaranteed harvest probabilities.

---

## 2. Dataset

The primary dataset is the Crop Recommendation dataset.

Dataset characteristics verified during the project:

- **Samples:** 2,200
- **Columns:** 8
- **Crop classes:** 22
- **Missing values:** 0
- **Duplicate rows:** 0

The machine-learning features are:

```text
N
P
K
temperature
humidity
ph
rainfall
```
