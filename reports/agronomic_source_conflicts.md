# Agronomic Source Conflicts & Discrepancies Report

This file documents discrepancies observed between major agricultural authorities. We do not synthesize these values artificially, but track them as variety-specific or region-specific configurations.

## 1. Crop: Rice
- **Parameter**: pH Optimal Bounds
- **Authority A**: International Rice Research Institute (IRRI) — recommends pH 5.5 to 6.5 for maximum nutrient availability.
- **Authority B**: FAO Crop Manual — documents acceptable performance across a wider margin of 5.0 to 8.0 in heavy alluvial clay soils.
- **Resolution**: The suitability engine will treat [5.5, 6.5] as 'Highly Suitable (Optimal)' and [5.0, 5.5) or [6.5, 8.0] as 'Moderately Suitable (Marginal)' with range-based advice.

## 2. Crop: Banana
- **Parameter**: Minimal temperature threshold
- **Authority A**: ICAR-NRCB (India) — warns that vegetative growth halts below 13°C.
- **Authority B**: FAO Horticultural database — recommends a safety margin threshold of 15°C for sensitive commercial cultivars.
- **Resolution**: Under 15°C will trigger a caution notice; temperatures below 13°C will trigger an active hazard warning.

## 3. Crop: Maize
- **Parameter**: Optimal Water/Rainfall Requirement
- **Authority A**: ICAR-IIMR — notes 500-800 mm distributed evenly is standard.
- **Authority B**: USDA Extension — highlights that under intensive high-yield hybrid management, 600-1000 mm is typical.
- **Resolution**: Highlight variation under dryland vs high-yield hybrid production systems.
