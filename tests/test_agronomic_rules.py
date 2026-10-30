import pytest
import sys
import os

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
    assert check['assessment'] == 'Highly Suitable'

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
    assert res['overall_status'] == 'Highly Suitable'

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
    assert res['overall_status'] == 'Unsuitable'

    # 20. Conflict-related behavior mapping
    res = engine.evaluate_crop('rice', {'pH': 5.2})
    check = next(c for c in res['checks'] if c['parameter'] == 'pH')
    # Assert it maps to Suitable (marginal) rather than Unsuitable or Highly Suitable
    assert check['assessment'] == 'Suitable'
