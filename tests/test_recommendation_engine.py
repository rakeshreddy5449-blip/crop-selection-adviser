import pytest
import sys
import os

sys.path.insert(0, os.path.abspath('src'))
from recommendation_engine import RecommendationEngine

def test_suite_recommendation_engine():
    engine = RecommendationEngine(models_dir='models', csv_path='reports/agronomic_requirements_sources.csv')

    # 1. Valid complete input (Rice baseline)
    inputs_rice = {
        'N': 80, 'P': 40, 'K': 40,
        'temperature': 25.0, 'humidity': 80.0, 'ph': 6.2,
        'rainfall': 1500.0, 'soil_texture': 'Heavy clay', 'irrigation': 'Basin flooding'
    }
    res = engine.recommend(inputs_rice)
    assert res['input_status'] == 'VALID'
    assert len(res['ranked_recommendations']) > 0

    # 2. Missing required ML feature
    inputs_missing_ml = {
        'P': 40, 'K': 40, 'temperature': 25.0
    }
    res_missing = engine.recommend(inputs_missing_ml)
    assert res_missing['input_status'] == 'INVALID'
    assert len(res_missing['ranked_recommendations']) == 0

    # 3. Missing optional agronomic information
    inputs_no_opt = {
        'N': 80, 'P': 40, 'K': 40,
        'temperature': 25.0, 'humidity': 80.0, 'ph': 6.2,
        'rainfall': 1500.0
    }
    res_no_opt = engine.recommend(inputs_no_opt)
    assert res_no_opt['input_status'] == 'VALID'
    # Since optionals are missing, top recommendations should map to caution
    rec = res_no_opt['ranked_recommendations'][0]
    assert rec['recommendation_category'] == 'RECOMMENDED WITH CAUTION'

    # 4. Agronomically unsuitable candidate
    inputs_extreme = {
        'N': 80, 'P': 40, 'K': 40,
        'temperature': 25.0, 'humidity': 80.0, 'ph': 11.5,
        'rainfall': 1500.0
    }
    res_extreme = engine.recommend(inputs_extreme)
    assert any(rec['recommendation_category'] == 'NOT RECOMMENDED' for rec in res_extreme['ranked_recommendations'])


def test_recommendation_surfaces_unavailable_and_insufficient_agronomic_rules(
    monkeypatch,
):
    engine = RecommendationEngine(
        models_dir='models',
        csv_path='reports/agronomic_requirements_sources.csv',
    )
    agronomic_result = {
        'overall_status': 'Insufficient Information',
        'warnings': [],
        'missing_information': [],
        'unavailable_rules': ['pH'],
        'insufficient_evidence': ['pH'],
        'invalid_information': [],
        'checks': [{
            'parameter': 'pH',
            'assessment': 'Insufficient Information',
            'reason': 'No verified rule is available.',
        }],
        'supporting_reasons': [],
        'sources': [],
    }
    monkeypatch.setattr(
        engine.agronomic_engine,
        'evaluate_crop',
        lambda crop, inputs: agronomic_result,
    )
    inputs = {
        'N': 80, 'P': 40, 'K': 40,
        'temperature': 25.0, 'humidity': 80.0, 'ph': 6.2,
        'rainfall': 1500.0,
    }

    result = engine.recommend(inputs)

    assert result['input_status'] == 'VALID'
    assert set(result['model_predictions']) == {
        'random_forest', 'svm', 'ann'
    }
    assert result['ranked_recommendations']
    for recommendation in result['ranked_recommendations']:
        assert recommendation['recommendation_category'] == (
            'INSUFFICIENT INFORMATION'
        )
        assert recommendation['unavailable_rules'] == ['pH']
        assert recommendation['insufficient_evidence'] == ['pH']
        assert recommendation['checks'][0]['parameter'] == 'pH'


def test_recommendation_rejects_non_finite_model_inputs():
    engine = RecommendationEngine(
        models_dir='models',
        csv_path='reports/agronomic_requirements_sources.csv',
    )
    inputs = {
        'N': 80, 'P': 40, 'K': 40,
        'temperature': 25.0, 'humidity': 80.0, 'ph': float('nan'),
        'rainfall': 1500.0,
    }

    result = engine.recommend(inputs)

    assert result['input_status'] == 'INVALID'
    assert result['invalid_inputs'] == ['ph']
    assert result['ranked_recommendations'] == []
