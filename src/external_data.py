import requests
import time

class WeatherClient:
    """
    A modular weather client utilizing wttr.in to fetch current weather data
    using a free, keyless JSON endpoint.
    """
    def __init__(self, timeout=5):
        self.timeout = timeout
        self.base_url = "https://wttr.in"

    def get_current_weather(self, location):
        """
        Retrieves current weather details for a user-specified location.
        """
        if not location or not isinstance(location, str) or not location.strip():
            return {
                "status": "FAILURE",
                "location": "Unknown",
                "weather_source": "wttr.in",
                "retrieved_at": str(time.time()),
                "warnings": ["Invalid location string provided."]
            }

        location_clean = location.strip()
        url = f"{self.base_url}/{location_clean}?format=j1"

        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 403:
                return {
                    "status": "AUTH_FAILURE",
                    "location": location_clean,
                    "weather_source": "wttr.in",
                    "retrieved_at": str(time.time()),
                    "warnings": ["API returned 403 Forbidden. Access blocked."]
                }
            if response.status_code != 200:
                return {
                    "status": "API_FAILURE",
                    "location": location_clean,
                    "weather_source": "wttr.in",
                    "retrieved_at": str(time.time()),
                    "warnings": [f"Weather API returned status code {response.status_code}"]
                }

            data = response.json()
            current_condition = data.get("current_condition", [{}])[0]

            # Extract temperature and humidity safely
            temp_c = current_condition.get("temp_C")
            humidity = current_condition.get("humidity")

            temp_val = float(temp_c) if temp_c is not None else None
            hum_val = float(humidity) if humidity is not None else None

            # Rainfall is often not directly given as a single accumulation field
            # in wttr.in current_condition, so we preserve it as unknown.
            # Real unknown must remain unknown.
            rainfall_val = None

            return {
                "status": "SUCCESS",
                "location": location_clean,
                "temperature": temp_val,
                "humidity": hum_val,
                "rainfall": rainfall_val,
                "weather_source": "wttr.in",
                "retrieved_at": str(time.time()),
                "warnings": ["Rainfall data was unknown from live conditions."]
            }

        except requests.exceptions.Timeout:
            return {
                "status": "TIMEOUT",
                "location": location_clean,
                "weather_source": "wttr.in",
                "retrieved_at": str(time.time()),
                "warnings": ["Weather API connection timed out."]
            }
        except (requests.exceptions.RequestException, ValueError) as e:
            return {
                "status": "FAILURE",
                "location": location_clean,
                "weather_source": "wttr.in",
                "retrieved_at": str(time.time()),
                "warnings": [f"Weather client failed with exception: {str(e)}"]
            }
