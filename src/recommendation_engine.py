import os
import joblib
import json
import numpy as np
import pandas as pd
import tensorflow as tf
from agronomic_rules import AgronomicSuitabilityEngine
from external_data import WeatherClient

class RecommendationEngine:
    def __init__(self, models_dir='models', csv_path='reports/agronomic_requirements_sources.csv'):
        self.models_dir = models_dir
        self.agronomic_engine = AgronomicSuitabilityEngine(csv_path)
        self.weather_client = WeatherClient()

        # Load saved artifacts
        self.rf_model = joblib.load(os.path.join(models_dir, 'random_forest_model.joblib'))
        self.svm_pipeline = joblib.load(os.path.join(models_dir, 'svm_model.joblib'))
        self.ann_model = tf.keras.models.load_model(os.path.join(models_dir, 'ann_crop_model.keras'))
        self.scaler = joblib.load(os.path.join(models_dir, 'ann_scaler.joblib'))
        self.label_encoder = joblib.load(os.path.join(models_dir, 'label_encoder.joblib'))

        with open(os.path.join(models_dir, 'metadata.json'), 'r') as f:
            self.metadata = json.load(f)
        self.feature_names = self.metadata['features']
        self.classes = self.metadata['classes']

    def recommend(self, farmer_inputs, location=None):
        warnings = []
        weather_info = None

        # If location is provided, fetch weather as contextual data
        if location:
            weather_info = self.weather_client.get_current_weather(location)
            if weather_info.get("status") != "SUCCESS":
                warnings.append(f"Current weather data unavailable; recommendation is based on supplied farm inputs and agronomic rules. (Details: {weather_info.get('warnings')})")
            else:
                # Check for conflicts between user inputs and retrieved weather data
                for field in ["temperature", "humidity"]:
                    user_val = farmer_inputs.get(field)
                    api_val = weather_info.get(field)
                    if user_val is not None and api_val is not None:
                        if abs(float(user_val) - float(api_val)) > 0.01:
                            warnings.append(f"User-provided {field}: {user_val} | Current external weather {field}: {api_val}. Difference detected; user-provided farm measurement was retained.")

        # Check for missing required features
        missing_required = [f for f in self.feature_names if f not in farmer_inputs or farmer_inputs[f] is None]
        if missing_required:
            return {
                "input_status": "INVALID",
                "warnings": warnings + [f"Missing required inputs: {missing_required}. Cannot run predictions."],
                "ranked_recommendations": [],
                "weather_context": weather_info
            }

        # Prepare inputs
        input_vals = [float(farmer_inputs[f]) for f in self.feature_names]
        input_arr = np.array([input_vals])

        # Standard preprocess scaling for ANN
        scaled_arr = self.scaler.transform(input_arr)

        # 1. Run Machine Learning Predictions
        rf_pred = self.rf_model.predict(input_arr)[0]
        svm_pred = self.svm_pipeline.predict(input_arr)[0]

        ann_probs = self.ann_model.predict(scaled_arr, verbose=0)[0]
        ann_idx = np.argmax(ann_probs)
        ann_pred = self.label_encoder.inverse_transform([ann_idx])[0]

        # 2. Extract Top Candidate Set using ANN probability distribution
        top_k = 5
        top_k_idx = np.argsort(ann_probs)[::-1][:top_k]
        candidate_crops = list(self.label_encoder.inverse_transform(top_k_idx))

        # Force inclusions from other baseline predictions to be thorough
        for p in [rf_pred, svm_pred]:
            if p not in candidate_crops:
                candidate_crops.append(p)

        # 3. Model Agreement Calculation
        predictions_set = [rf_pred, svm_pred, ann_pred]

        ranked_recommendations = []

        for crop in candidate_crops:
            votes = sum(1 for p in predictions_set if p == crop)
            agreement_text = f"{(votes)}/3 models predict {crop}"

            # Agronomic rule-based check
            ag_res = self.agronomic_engine.evaluate_crop(crop, farmer_inputs)

            # Resolve category mapping based on evidence integrity
            if ag_res['overall_status'] == 'Unsuitable':
                category = 'NOT RECOMMENDED'
                why = f"Agronomic mismatch: {', '.join(ag_res['warnings'] or ['Input values do not meet acceptable limits.'])}"
            elif ag_res['overall_status'] == 'Insufficient Information':
                category = 'INSUFFICIENT INFORMATION'
                why = "Model supports candidate, but insufficient localized data available to make an agronomic recommendation."
            elif len(ag_res['missing_information']) > 0:
                category = 'RECOMMENDED WITH CAUTION'
                why = f"Agronomic check is baseline {ag_res['overall_status']}; missing key elements: {ag_res['missing_information']}"
            else:
                category = 'RECOMMENDED'
                why = f"All agronomic constraints satisfied successfully: {', '.join(ag_res['supporting_reasons'])}"

            ranked_recommendations.append({
                "crop": crop,
                "ml_votes": votes,
                "model_agreement": agreement_text,
                "agronomic_status": ag_res['overall_status'],
                "recommendation_category": category,
                "reasoning": why,
                "missing_information": ag_res['missing_information'],
                "sources": ag_res['sources']
            })

        # Sort recommendations
        category_priority = {
            'RECOMMENDED': 0,
            'RECOMMENDED WITH CAUTION': 1,
            'INSUFFICIENT INFORMATION': 2,
            'NOT RECOMMENDED': 3
        }

        ranked_recommendations.sort(key=lambda x: (category_priority[x['recommendation_category']], -x['ml_votes']))

        return {
            "input_status": "VALID",
            "warnings": warnings,
            "model_predictions": {
                "random_forest": rf_pred,
                "svm": svm_pred,
                "ann": ann_pred
            },
            "ranked_recommendations": ranked_recommendations,
            "weather_context": weather_info
        }
