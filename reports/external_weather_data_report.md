# External Weather Data Report (Stage 3.4)

## 1. Purpose
Enable safe contextual enrichment of user soil records with live localized climatic conditions without modifying model weights.

## 2. API/Provider
- **API**: wttr.in
- **Access**: Free, keyless GET requests.
- **Endpoint**: `https://wttr.in/<location>?format=j1`
- **Fields retrieved**: `temp_C` (converted to temperature float), `humidity` (converted to float).
- **Rainfall**: Returned as `None` (Unknown remains unknown).
- **Timeout**: 5 seconds limit.

## 3. Error & Missing Value Handling
- Connection limits or timeout errors do not block recommendation logic. Falls back gracefully with a warning reporting: `"Current weather data unavailable; recommendation is based on supplied farm inputs and agronomic rules."`
- Unknown values are never fabricated or backfilled with mock means/medians.

## 4. User-Input Precedence Policy
- User measured parameters are **never** silently overridden. Differences triggers a logged warning in the recommendation response context.

## 5. Live vs Mocked Examples
- Live checks require a clean JSON dictionary response.
- **Mocked response verification** is enforced across the entire unit test suite to support offline CI execution limits.
