import pytest
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath('src'))
from agronomic_rules import AgronomicSuitabilityEngine

def test_suite_agronomic_rules():
    engine = AgronomicSuitabilityEngine('reports/agronomic_requirements_sources.csv')

    # 1. Preferred pH range
    res = engine.evaluate_crop('rice', {'pH': 6.0})
    check = next(c for c in res['checks'] if c['parameter'] == 'pH')
    assert check['assessment'] == 'Highly Suitable'

    # 2. Tolerable pH range
    res = engine.evaluate_crop('rice', {'pH': 5.2})
    check = next(c for c in res['checks'] if c['parameter'] == 'pH')
    assert check['assessment'] == 'Suitable'

    # 3. pH outside documented range
    res = engine.evaluate_crop('rice', {'pH': 3.5})
    assert res['overall_status'] == 'Unsuitable'

    # 4. Preferred temperature range
    res = engine.evaluate_crop('rice', {'temperature': 25.0})
    check = next(c for c in res['checks'] if c['parameter'] == 'temperature')
    assert check['assessment'] == 'Highly Suitable'

    # 5. Temperature outside documented range
    res = engine.evaluate_crop('rice', {'temperature': 12.0})
    assert res['overall_status'] == 'Unsuitable'

    # 6. Rainfall evaluation
    res = engine.evaluate_crop('rice', {'rainfall': 1500.0})
    check = next(c for c in res['checks'] if c['parameter'] == 'rainfall')
    assert check['assessment'] == 'Suitable'

    # 7. Missing pH
    res = engine.evaluate_crop('rice', {'temperature': 25.0})
    assert 'pH' in res['missing_information']

    # 8. Missing temperature
    res = engine.evaluate_crop('rice', {'pH': 6.0})
    assert 'temperature' in res['missing_information']

    # 9. Missing rainfall
    res = engine.evaluate_crop('rice', {'pH': 6.0})
    assert 'rainfall' in res['missing_information']

    # 10. Missing soil texture
    res = engine.evaluate_crop('rice', {'pH': 6.0})
    assert 'soil_texture' in res['missing_information']

    # 11. Missing irrigation
    res = engine.evaluate_crop('rice', {'pH': 6.0})
    assert 'irrigation' in res['missing_information']

    # 12. Multiple simultaneous conditions
    res = engine.evaluate_crop('rice', {'pH': 6.0, 'temperature': 25.0, 'rainfall': 1500.0})
    assert res['overall_status'] == 'Suitable'

    # 13. Unknown crop
    res = engine.evaluate_crop('unknown_crop_type', {'pH': 6.0})
    assert res['overall_status'] == 'Insufficient Information'

    # 14. Insufficient information
    res = engine.evaluate_crop('rice', {})
    assert res['overall_status'] == 'Insufficient Information'

    # 15. Source traceability
    res = engine.evaluate_crop('rice', {'pH': 6.0})
    check = next(c for c in res['checks'] if c['parameter'] == 'pH')
    assert check['source_name'] == 'FAO Crop Water Information'
    assert check['reference_available'] is True
    assert check['source_verified'] is False

    # 16. Grapes evaluation
    res_grapes = engine.evaluate_crop('grapes', {'pH': 6.5, 'temperature': 28.0, 'rainfall': 600.0})
    assert res_grapes['overall_status'] == 'Highly Suitable'

    # 17. Explanation generation
    res = engine.evaluate_crop('rice', {'pH': 6.0})
    assert len(res['supporting_reasons']) > 0

    # 18. Rejection reason
    res = engine.evaluate_crop('rice', {'pH': 9.5})
    assert any("unsuitable" in w.lower() for w in res['warnings'])

    # 19. Invalid input handling
    res = engine.evaluate_crop('rice', {'pH': 'invalid_string'})
    assert res['overall_status'] == 'Insufficient Information'

    check = next(c for c in res['checks'] if c['parameter'] == 'pH')
    assert check['assessment'] == 'Invalid Input'
    assert 'pH' in res['invalid_information']

    # 20. Conflict-related behavior mapping
    res = engine.evaluate_crop('rice', {'pH': 5.2})
    check = next(c for c in res['checks'] if c['parameter'] == 'pH')
    # Assert it maps to Suitable (marginal) rather than Unsuitable or Highly Suitable
    assert check['assessment'] == 'Suitable'


def test_ph_aliases_have_consistent_display_and_missing_information():
    engine = AgronomicSuitabilityEngine('reports/agronomic_requirements_sources.csv')

    for key in ('pH', 'ph', 'PH'):
        result = engine.evaluate_crop('rice', {key: 6.0})
        check = next(c for c in result['checks'] if c['parameter'] == 'pH')
        assert check['assessment'] == 'Highly Suitable'
        assert 'pH' not in result['missing_information']
        assert 'ph' not in result['missing_information']


def test_missing_farmer_inputs_use_consistent_display_names():
    engine = AgronomicSuitabilityEngine('reports/agronomic_requirements_sources.csv')

    result = engine.evaluate_crop('rice', {'temperature': 25.0})

    assert result['missing_information'] == [
        'pH', 'rainfall', 'soil_texture', 'irrigation'
    ]


def test_provided_value_without_crop_rule_is_not_reported_missing():
    engine = AgronomicSuitabilityEngine('reports/agronomic_requirements_sources.csv')

    result = engine.evaluate_crop('unknown_crop_type', {'pH': 6.0})

    assert 'pH' not in result['missing_information']
    assert 'pH' in result['unavailable_rules']
    assert 'pH' in result['insufficient_evidence']
    assert result['overall_status'] == 'Insufficient Information'


@pytest.mark.parametrize('value', ['not-a-number', float('nan'), float('inf')])
def test_invalid_numerical_inputs_are_not_suitable(value):
    engine = AgronomicSuitabilityEngine('reports/agronomic_requirements_sources.csv')

    result = engine.evaluate_crop('rice', {'pH': value})
    check = next(c for c in result['checks'] if c['parameter'] == 'pH')

    assert check['assessment'] == 'Invalid Input'
    assert 'pH' in result['invalid_information']
    assert result['overall_status'] == 'Insufficient Information'


def test_missing_numerical_range_is_insufficient_evidence(tmp_path):
    csv_path = tmp_path / 'requirements.csv'
    pd.DataFrame([{
        'crop': 'test crop',
        'parameter': 'pH',
        'minimum': None,
        'maximum': 8.0,
        'unit': 'pH',
        'preferred_value_or_description': 'Optimal 6.0-7.0.',
        'source_name': 'Agronomy reference',
        'source_url': 'https://example.org/crop',
        'source_notes': 'Test data',
        'confidence': 'High',
        'last_checked': '2025-05-15',
    }]).to_csv(csv_path, index=False)
    engine = AgronomicSuitabilityEngine(str(csv_path))

    result = engine.evaluate_crop('test crop', {'pH': 6.5})
    check = next(c for c in result['checks'] if c['parameter'] == 'pH')

    assert check['assessment'] == 'Insufficient Information'
    assert 'pH' not in result['missing_information']
    assert 'pH' in result['insufficient_evidence']


def test_qualitative_inputs_are_not_assumed_suitable():
    engine = AgronomicSuitabilityEngine('reports/agronomic_requirements_sources.csv')

    result = engine.evaluate_crop(
        'rice',
        {'soil_texture': 'Heavy clay', 'irrigation': 'Basin flooding'},
    )
    checks = {
        check['parameter']: check
        for check in result['checks']
    }

    assert checks['soil_texture']['assessment'] == 'Insufficient Information'
    assert checks['irrigation']['assessment'] == 'Insufficient Information'
    assert 'soil_texture' not in result['missing_information']
    assert 'irrigation' not in result['missing_information']
    assert {'soil_texture', 'irrigation'} <= set(result['insufficient_evidence'])


def test_unverified_source_is_not_returned_as_reference():
    engine = AgronomicSuitabilityEngine('reports/agronomic_requirements_sources.csv')

    result = engine.evaluate_crop('chickpea', {'pH': 6.0})
    check = next(c for c in result['checks'] if c['parameter'] == 'pH')

    assert check['source_name'] == 'UNVERIFIED'
    assert check['source_url'] == '#'
    assert check['source_verified'] is False
    assert check['reference_available'] is False
    assert result['sources'] == []
    assert check['assessment'] == 'Insufficient Information'
