import pandas as pd
import numpy as np

class AgronomicSuitabilityEngine:
    def __init__(self, csv_path='reports/agronomic_requirements_sources.csv'):
        self.csv_path = csv_path
        try:
            self.df = pd.read_csv(csv_path)
        except Exception as e:
            self.df = pd.DataFrame()
            print(f"Warning: Could not load {csv_path}: {e}")

    def evaluate_crop(self, crop, inputs):
        crop_rules = self.df[self.df['crop'] == crop.lower()]
        checks = []
        supporting_reasons = []
        warnings = []
        missing_information = []

        rating_hierarchy = {
            "Unsuitable": 0,
            "Caution": 1,
            "Moderately Suitable": 2,
            "Suitable": 3,
            "Highly Suitable": 4,
            "Insufficient Information": -1
        }

        lowest_rating_numeric = 4
        has_unsuitable = False
        has_evaluations = False

        core_numerical = ['pH', 'temperature', 'rainfall']
        core_qualitative = ['soil_texture', 'irrigation']
        all_tracked = set(core_numerical) | set(core_qualitative)

        normalized_inputs = {str(k).lower(): v for k, v in inputs.items()}

        for param in all_tracked:
            user_val = normalized_inputs.get(param.lower(), None)
            # Perform case-insensitive parameter matching against the rule database
            rules_subset = crop_rules[crop_rules['parameter'].str.lower() == param.lower()]

            if rules_subset.empty:
                missing_information.append(param)
                continue

            rule = rules_subset.iloc[0]
            source_name = rule.get('source_name', 'Unknown Source')
            source_url = rule.get('source_url', '#')

            if user_val is None:
                missing_information.append(param)
                checks.append({
                    "parameter": param,
                    "input": "Unknown",
                    "assessment": "Insufficient Information",
                    "reason": "No input provided by the user for evaluation.",
                    "source_name": source_name,
                    "source_url": source_url
                })
                continue

            has_evaluations = True
            unit = rule.get('unit', '')

            if unit in ['pH', 'C', 'mm']:
                try:
                    val = float(user_val)
                except (ValueError, TypeError):
                    checks.append({
                        "parameter": param,
                        "input": str(user_val),
                        "assessment": "Unsuitable",
                        "reason": f"Input value could not be converted to a numerical value.",
                        "source_name": source_name,
                        "source_url": source_url
                    })
                    lowest_rating_numeric = 0
                    has_unsuitable = True
                    continue

                min_val = rule['minimum']
                max_val = rule['maximum']
                desc = rule.get('preferred_value_or_description', '')

                min_val = None if pd.isna(min_val) else float(min_val)
                max_val = None if pd.isna(max_val) else float(max_val)

                if min_val is not None and max_val is not None:
                    midpoint = (min_val + max_val) / 2.0
                    optimal_span = (max_val - min_val) * 0.25
                    pref_min = midpoint - optimal_span
                    pref_max = midpoint + optimal_span

                    if "Optimal 5.5-6.5" in desc:
                        pref_min, pref_max = 5.5, 6.5
                    elif "Optimal range 22-32C" in desc:
                        pref_min, pref_max = 22.0, 32.0
                    elif "optimal pH is 6.0 to 7.0" in desc:
                        pref_min, pref_max = 6.0, 7.0
                    elif "optimal pH is 6.0 to 7.5" in desc:
                        pref_min, pref_max = 6.0, 7.5

                    if val < min_val or val > max_val:
                        assessment = "Unsuitable"
                        reason = f"Input value {val}{unit} is outside the documented acceptable range of {min_val} to {max_val}{unit}."
                        warnings.append(f"{param} value {val}{unit} is unsuitable.")
                        has_unsuitable = True
                    elif pref_min <= val <= pref_max:
                        assessment = "Highly Suitable"
                        reason = f"Input value {val}{unit} falls within the documented preferred range of {pref_min} to {pref_max}{unit}."
                        supporting_reasons.append(f"{param} is in preferred range.")
                    else:
                        assessment = "Suitable"
                        reason = f"Input value {val}{unit} is within the acceptable range ({min_val} to {max_val}{unit}) but outside the optimal preferred sub-range."
                        supporting_reasons.append(f"{param} is within acceptable range.")
                else:
                    assessment = "Suitable"
                    reason = f"Input value is compatible: {desc}"
                    supporting_reasons.append(f"{param} evaluation: {desc}")

                checks.append({
                    "parameter": param,
                    "input": f"{val}{unit}",
                    "assessment": assessment,
                    "reason": reason,
                    "source_name": source_name,
                    "source_url": source_url
                })

                rating_val = rating_hierarchy.get(assessment, 4)
                if rating_val < lowest_rating_numeric:
                    lowest_rating_numeric = rating_val

            else:
                desc = rule.get('preferred_value_or_description', '')
                assessment = "Suitable"
                reason = f"Qualitative match evaluated: {desc}"
                supporting_reasons.append(f"{param}: {desc}")

                checks.append({
                    "parameter": param,
                    "input": str(user_val),
                    "assessment": assessment,
                    "reason": reason,
                    "source_name": source_name,
                    "source_url": source_url
                })

        if not has_evaluations:
            overall_status = "Insufficient Information"
        elif has_unsuitable:
            overall_status = "Unsuitable"
        else:
            status_map = {0: "Unsuitable", 1: "Caution", 2: "Moderately Suitable", 3: "Suitable", 4: "Highly Suitable"}
            overall_status = status_map.get(lowest_rating_numeric, "Suitable")

        return {
            "crop": crop,
            "overall_status": overall_status,
            "checks": checks,
            "supporting_reasons": supporting_reasons,
            "warnings": warnings,
            "missing_information": missing_information,
            "sources": list({x['source_name']: x for x in checks}.values())
        }
