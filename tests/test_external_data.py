import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import requests

sys.path.insert(0, os.path.abspath('src'))
from external_data import WeatherClient
from recommendation_engine import RecommendationEngine

@patch('requests.get')
def test_successful_weather_response(mock_get):
    # Mock successful response matching wttr.in schema
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "current_condition": [
            {
                "temp_C": "28",
                "humidity": "82"
            }
        ]
    }
    mock_get.return_value = mock_response

    client = WeatherClient()
    res = client.get_current_weather("Nairobi")
    assert res["status"] == "SUCCESS"
    assert res["location"] == "Nairobi"
    assert res["temperature"] == 28.0
    assert res["humidity"] == 82.0
    assert res["rainfall"] is None  # Unknown remains unknown
    assert "wttr.in" in res["weather_source"]

@patch('requests.get')
def test_weather_invalid_location(mock_get):
    client = WeatherClient()
    res = client.get_current_weather("   ")
    assert res["status"] == "FAILURE"
    assert any("Invalid location" in w for w in res["warnings"])

@patch('requests.get')
def test_weather_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout()
    client = WeatherClient()
    res = client.get_current_weather("Nairobi")
    assert res["status"] == "TIMEOUT"
    assert any("timed out" in w for w in res["warnings"])

@patch('requests.get')
def test_weather_connection_error(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Connection lost")
    client = WeatherClient()
    res = client.get_current_weather("Nairobi")
    assert res["status"] == "FAILURE"
    assert any("exception" in w for w in res["warnings"])

@patch('requests.get')
def test_weather_missing_fields(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "current_condition": [{}]
    }
    mock_get.return_value = mock_response

    client = WeatherClient()
    res = client.get_current_weather("Nairobi")
    assert res["status"] == "SUCCESS"
    assert res["temperature"] is None
    assert res["humidity"] is None

@patch('requests.get')
def test_weather_malformed_response(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    # Throwing decoding error
    mock_response.json.side_effect = ValueError("Decoding error")
    mock_get.return_value = mock_response

    client = WeatherClient()
    res = client.get_current_weather("Nairobi")
    assert res["status"] == "FAILURE"
    assert any("exception" in w for w in res["warnings"])

@patch('requests.get')
def test_weather_forbidden_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_get.return_value = mock_response

    client = WeatherClient()
    res = client.get_current_weather("Nairobi")
    assert res["status"] == "AUTH_FAILURE"
    assert any("Forbidden" in w for w in res["warnings"])

@patch('requests.get')
def test_weather_and_user_input_precedence(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "current_condition": [
            {
                "temp_C": "31",
                "humidity": "82"
            }
        ]
    }
    mock_get.return_value = mock_response

    engine = RecommendationEngine(models_dir='models', csv_path='reports/agronomic_requirements_sources.csv')
    inputs = {
        'N': 80, 'P': 40, 'K': 40,
        'temperature': 25.0, 'humidity': 80.0, 'ph': 6.2,
        'rainfall': 1500.0
    }
    # Run recommendation with location trigger
    res = engine.recommend(inputs, location="Nairobi")
    assert res["input_status"] == "VALID"
    # Ensure weather was attached but user's 25C was preserved
    assert res["weather_context"]["temperature"] == 31.0
    assert any("Difference detected" in w for w in res["warnings"])

@patch('requests.get')
def test_weather_failure_fallback_recommendation(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout()
    engine = RecommendationEngine(models_dir='models', csv_path='reports/agronomic_requirements_sources.csv')
    inputs = {
        'N': 80, 'P': 40, 'K': 40,
        'temperature': 25.0, 'humidity': 80.0, 'ph': 6.2,
        'rainfall': 1500.0
    }
    res = engine.recommend(inputs, location="Nairobi")
    assert res["input_status"] == "VALID"
    assert res["weather_context"]["status"] == "TIMEOUT"
    assert any("Current weather data unavailable" in w for w in res["warnings"])
