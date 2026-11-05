import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath('src'))
from agronomic_rules import AgronomicSuitabilityEngine


PARAMETERS = ['pH', 'temperature', 'rainfall', 'soil_texture', 'irrigation']
RESEARCH_COLUMNS = [
    'crop', 'parameter', 'evidence_status', 'publication_title',
    'author_or_institution', 'direct_url', 'page_section_or_table',
    'claim_or_requirement', 'minimum', 'maximum', 'unit', 'range_type',
    'growing_conditions_context', 'verification_status', 'research_notes',
]


def _research_record(parameter, evidence_status='UNKNOWN', **updates):
    record = {
        'crop': 'rice',
        'parameter': parameter,
        'evidence_status': evidence_status,
        'publication_title': 'UNKNOWN',
        'author_or_institution': 'UNKNOWN',
        'direct_url': 'UNKNOWN',
        'page_section_or_table': 'UNKNOWN',
        'claim_or_requirement': 'UNKNOWN',
        'minimum': 'UNKNOWN',
        'maximum': 'UNKNOWN',
        'unit': 'UNKNOWN',
        'range_type': 'UNKNOWN',
        'growing_conditions_context': 'UNKNOWN',
        'verification_status': 'NOT_VERIFIED',
        'research_notes': 'UNKNOWN',
    }
    record.update(updates)
    return record


def _engine(tmp_path, records=None, legacy_records=None, malformed=False):
    research_path = tmp_path / 'research.csv'
    if malformed:
        pd.DataFrame([{'crop': 'rice', 'parameter': 'pH'}]).to_csv(
            research_path, index=False
        )
    else:
        if records is None:
            records = [_research_record(parameter) for parameter in PARAMETERS]
        pd.DataFrame(records, columns=RESEARCH_COLUMNS).to_csv(
            research_path, index=False
        )

    legacy_path = tmp_path / 'legacy.csv'
    legacy_columns = [
        'crop', 'parameter', 'minimum', 'maximum', 'unit',
        'preferred_value_or_description', 'source_name', 'source_url',
        'source_notes', 'confidence', 'last_checked',
    ]
    pd.DataFrame(
        legacy_records or [], columns=legacy_columns
    ).to_csv(legacy_path, index=False)
    return AgronomicSuitabilityEngine(
        csv_path=str(legacy_path),
        research_csv_path=str(research_path),
        crop_labels=['rice'],
    )


@pytest.mark.parametrize('parameter', PARAMETERS)
def test_unknown_evidence_is_insufficient_for_each_parameter(
    tmp_path, parameter
):
    engine = _engine(tmp_path)

    result = engine.evaluate_crop('rice', {parameter: 6.0})
    check = next(
        check for check in result['checks']
        if check['parameter'] == parameter
    )

    assert check['evidence_status'] == 'UNKNOWN'
    assert check['assessment'] == 'Insufficient Information'
    assert parameter in result['unknown_evidence']
    assert result['overall_status'] == 'Insufficient Information'
    assert result['suitability_status'] == 'Cannot Determine'


def test_ph_input_aliases_and_missing_farmer_inputs_are_consistent(tmp_path):
    engine = _engine(tmp_path)

    for key in ('pH', 'ph', 'PH'):
        result = engine.evaluate_crop('rice', {key: 6.0})
        check = next(c for c in result['checks'] if c['parameter'] == 'pH')
        assert check['evidence_status'] == 'UNKNOWN'
        assert 'pH' not in result['missing_information']
        assert check['assessment'] == 'Insufficient Information'

    missing_result = engine.evaluate_crop('rice', {})
    assert missing_result['missing_information'] == PARAMETERS
    assert missing_result['unknown_evidence'] == PARAMETERS


def test_legacy_values_are_preserved_but_cannot_override_unknown_research(
    tmp_path,
):
    legacy = [{
        'crop': 'rice',
        'parameter': 'pH',
        'minimum': '0',
        'maximum': '14',
        'unit': 'pH',
        'preferred_value_or_description': 'Legacy numeric range',
        'source_name': 'Legacy reference',
        'source_url': 'https://example.invalid/legacy',
        'source_notes': 'Historical row',
        'confidence': 'High',
        'last_checked': '2025-01-01',
    }]
    engine = _engine(tmp_path, legacy_records=legacy)

    result = engine.evaluate_crop('rice', {'pH': 6.0})
    check = next(c for c in result['checks'] if c['parameter'] == 'pH')

    assert check['assessment'] == 'Insufficient Information'
    assert check['evidence_status'] == 'UNKNOWN'
    assert check['legacy_reference']['minimum'] == '0'
    assert check['legacy_reference']['maximum'] == '14'
    assert check['legacy_data_status'] == 'NOT_VERIFIED'
    assert 'pH' in result['legacy_unverified']
    assert result['sources'] == []


def test_comparable_legacy_range_conflict_is_reported_but_not_applied(
    tmp_path,
):
    pH_record = _research_record(
        'pH',
        evidence_status='VERIFIED',
        publication_title='Verified soil guide',
        author_or_institution='Agriculture institute',
        direct_url='https://example.org/soil-guide',
        claim_or_requirement='Verified range is from 5 to 8 pH.',
        minimum='5',
        maximum='8',
        unit='pH',
        verification_status='SOURCE_CONTENT_VERIFIED',
    )
    records = [
        pH_record if parameter == 'pH'
        else _research_record(parameter)
        for parameter in PARAMETERS
    ]
    legacy = [{
        'crop': 'rice',
        'parameter': 'pH',
        'minimum': '6',
        'maximum': '7',
        'unit': 'pH',
        'preferred_value_or_description': 'Legacy range',
        'source_name': 'Legacy source',
        'source_url': 'https://example.org/legacy',
        'source_notes': 'Historical range',
        'confidence': 'Medium',
        'last_checked': '2025-01-01',
    }]
    engine = _engine(tmp_path, records=records, legacy_records=legacy)

    result = engine.evaluate_crop('rice', {'pH': 6.5})
    check = next(c for c in result['checks'] if c['parameter'] == 'pH')

    assert check['evidence_status'] == 'VERIFIED'
    assert check['effective_evidence_status'] == 'CONFLICTING'
    assert check['legacy_conflict'] is True
    assert check['legacy_data_status'] == 'RANGE_CONFLICT'
    assert 'pH' in result['legacy_conflicts']
    assert check['assessment'] == (
        'Evidence Available - No Suitability Assessment'
    )
    assert result['overall_status'] == 'Insufficient Information'


def test_missing_research_record_fails_safely(tmp_path):
    records = [
        _research_record(parameter)
        for parameter in PARAMETERS
        if parameter != 'rainfall'
    ]
    engine = _engine(tmp_path, records=records)

    result = engine.evaluate_crop('rice', {'rainfall': 1000.0})
    check = next(c for c in result['checks'] if c['parameter'] == 'rainfall')

    assert check['evidence_status'] == 'UNKNOWN'
    assert check['assessment'] == 'Insufficient Information'
    assert 'rainfall' in result['unavailable_rules']
    assert not result['research_register_valid']
    assert any('Missing research record' in w for w in result['warnings'])


def test_duplicate_research_records_are_detected_and_not_used(tmp_path):
    record = _research_record('pH')
    records = [record, record] + [
        _research_record(parameter)
        for parameter in PARAMETERS
        if parameter != 'pH'
    ]
    engine = _engine(tmp_path, records=records)

    result = engine.evaluate_crop('rice', {'pH': 6.0})
    check = next(c for c in result['checks'] if c['parameter'] == 'pH')

    assert check['evidence_status'] == 'UNKNOWN'
    assert check['assessment'] == 'Insufficient Information'
    assert any('Duplicate research record' in error
               for error in result['research_validation_errors'])
    assert any('duplicate crop/parameter' in warning
               for warning in result['warnings'])


def test_malformed_research_schema_fails_safely(tmp_path):
    engine = _engine(tmp_path, malformed=True)

    result = engine.evaluate_crop('rice', {'pH': 6.0})

    assert result['overall_status'] == 'Insufficient Information'
    assert result['unknown_evidence'] == PARAMETERS
    assert not result['research_register_valid']
    assert any('missing required columns' in warning.lower()
               for warning in result['warnings'])


def test_unreadable_research_csv_fails_safely(tmp_path):
    research_path = tmp_path / 'broken.csv'
    research_path.write_text('crop,parameter\n"unterminated', encoding='utf-8')
    engine = AgronomicSuitabilityEngine(
        csv_path=str(tmp_path / 'missing-legacy.csv'),
        research_csv_path=str(research_path),
        crop_labels=['rice'],
    )

    result = engine.evaluate_crop('rice', {'pH': 6.0})

    assert result['overall_status'] == 'Insufficient Information'
    assert result['unknown_evidence'] == PARAMETERS
    assert not result['research_register_valid']
    assert any('could not be read' in warning.lower()
               for warning in result['warnings'])


def test_verified_register_entry_requires_complete_source_metadata(tmp_path):
    incomplete = _research_record(
        'pH',
        evidence_status='VERIFIED',
        publication_title='A title',
        author_or_institution='An institute',
        direct_url='https://example.org',
        claim_or_requirement='UNKNOWN',
        verification_status='SOURCE_CONTENT_VERIFIED',
    )
    records = [
        incomplete if parameter == 'pH'
        else _research_record(parameter)
        for parameter in PARAMETERS
    ]
    engine = _engine(tmp_path, records=records)

    result = engine.evaluate_crop('rice', {'pH': 6.0})
    check = next(c for c in result['checks'] if c['parameter'] == 'pH')

    assert check['evidence_status'] == 'UNKNOWN'
    assert check['assessment'] == 'Insufficient Information'
    assert any('treated as UNKNOWN' in error
               for error in result['research_validation_errors'])


def test_rice_irrigation_evidence_does_not_become_rainfall_evidence(tmp_path):
    irrigation = _research_record(
        'irrigation',
        evidence_status='VERIFIED',
        publication_title='How to manage water',
        author_or_institution='International Rice Research Institute (IRRI)',
        direct_url=(
            'http://knowledgebank.irri.org/step-by-step-production/'
            'growth/water-management'
        ),
        page_section_or_table='Overview; continuous flooding',
        claim_or_requirement=(
            'Seasonal field water input varies by texture and groundwater; '
            '1300-1500 mm is typical for irrigated rice in Asia.'
        ),
        unit='mm',
        range_type='Context-specific seasonal water input',
        growing_conditions_context=(
            'Lowland irrigated rice; not rainfall or a universal threshold.'
        ),
        verification_status='SOURCE_CONTENT_VERIFIED',
        research_notes='Do not apply to all rice systems.',
    )
    records = [
        irrigation if parameter == 'irrigation'
        else _research_record(parameter)
        for parameter in PARAMETERS
    ]
    engine = _engine(tmp_path, records=records)

    result = engine.evaluate_crop(
        'rice',
        {'rainfall': 1400.0, 'irrigation': 'Basin flooding'},
    )
    rainfall_check = next(
        c for c in result['checks'] if c['parameter'] == 'rainfall'
    )
    irrigation_check = next(
        c for c in result['checks'] if c['parameter'] == 'irrigation'
    )

    assert rainfall_check['evidence_status'] == 'UNKNOWN'
    assert rainfall_check['assessment'] == 'Insufficient Information'
    assert irrigation_check['evidence_status'] == 'VERIFIED'
    assert irrigation_check['assessment'] == (
        'Evidence Available - No Suitability Assessment'
    )
    assert 'rainfall' in result['unknown_evidence']
    assert 'irrigation' not in result['unknown_evidence']


def test_real_research_register_authorizes_only_rice_irrigation_evidence():
    engine = AgronomicSuitabilityEngine()

    result = engine.evaluate_crop(
        'rice',
        {'pH': 6.0, 'temperature': 25.0, 'rainfall': 1400.0,
         'soil_texture': 'Heavy clay', 'irrigation': 'Basin flooding'},
    )

    assert result['research_register_valid']
    assert result['unknown_evidence'] == [
        'pH', 'temperature', 'rainfall', 'soil_texture'
    ]
    assert 'irrigation' not in result['unknown_evidence']
    assert result['overall_status'] == 'Insufficient Information'
    assert result['sources'][0]['publication_title'] == 'How to manage water'


@pytest.mark.parametrize(
    'method',
    ['Basin flooding', 'Drip irrigation', 'No irrigation'],
)
def test_rice_irrigation_claim_is_not_a_universal_numeric_threshold(
    tmp_path, method
):
    irrigation = _research_record(
        'irrigation',
        evidence_status='VERIFIED',
        publication_title='How to manage water',
        author_or_institution='IRRI',
        direct_url='https://example.org/irri-water-page',
        claim_or_requirement='Contextual seasonal water-input figures.',
        unit='mm',
        growing_conditions_context='Irrigated lowland rice only.',
        verification_status='SOURCE_CONTENT_VERIFIED',
    )
    records = [
        irrigation if parameter == 'irrigation'
        else _research_record(parameter)
        for parameter in PARAMETERS
    ]
    engine = _engine(tmp_path, records=records)

    result = engine.evaluate_crop('rice', {'irrigation': method})
    check = next(c for c in result['checks'] if c['parameter'] == 'irrigation')

    assert check['assessment'] == (
        'Evidence Available - No Suitability Assessment'
    )
    assert result['overall_status'] == 'Insufficient Information'
    assert result['suitability_status'] == 'Cannot Determine'


def test_verified_source_claim_and_limitations_are_preserved(tmp_path):
    claim = 'Contextual seasonal field water input, not a crop threshold.'
    limitations = 'Applies to irrigated lowland context only.'
    irrigation = _research_record(
        'irrigation',
        evidence_status='VERIFIED',
        publication_title='How to manage water',
        author_or_institution='International Rice Research Institute (IRRI)',
        direct_url='https://example.org/irri-water-page',
        page_section_or_table='Water management',
        claim_or_requirement=claim,
        unit='mm',
        range_type='Context-specific',
        growing_conditions_context='Irrigated lowland rice.',
        verification_status='SOURCE_CONTENT_VERIFIED',
        research_notes=limitations,
    )
    records = [
        irrigation if parameter == 'irrigation'
        else _research_record(parameter)
        for parameter in PARAMETERS
    ]
    engine = _engine(tmp_path, records=records)

    result = engine.evaluate_crop('rice', {'irrigation': 'Basin flooding'})
    check = next(c for c in result['checks'] if c['parameter'] == 'irrigation')

    assert check['source_verified'] is True
    assert check['publication_title'] == 'How to manage water'
    assert check['source_url'] == 'https://example.org/irri-water-page'
    assert check['claim_or_requirement'] == claim
    assert check['unit'] == 'mm'
    assert check['growing_conditions_context'] == 'Irrigated lowland rice.'
    assert check['limitations'] == limitations
    assert result['sources'][0]['claim_or_requirement'] == claim
