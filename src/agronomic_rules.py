import math
import re
from numbers import Number
from urllib.parse import urlparse

import pandas as pd


class AgronomicSuitabilityEngine:
    NUMERICAL_PARAMETERS = ("ph", "temperature", "rainfall")
    QUALITATIVE_PARAMETERS = ("soil_texture", "irrigation")
    TRACKED_PARAMETERS = NUMERICAL_PARAMETERS + QUALITATIVE_PARAMETERS

    @staticmethod
    def _normalize_name(value):
        return re.sub(r"[\s-]+", "_", str(value).strip().lower())

    @staticmethod
    def _is_missing(value):
        if value is None:
            return True
        try:
            if bool(pd.isna(value)):
                return True
        except (TypeError, ValueError):
            pass
        return isinstance(value, str) and not value.strip()

    @staticmethod
    def _is_missing_input(value):
        if value is None:
            return True
        if isinstance(value, str):
            return not value.strip()
        if isinstance(value, Number):
            return False
        return AgronomicSuitabilityEngine._is_missing(value)

    @staticmethod
    def _clean_metadata(value):
        if AgronomicSuitabilityEngine._is_missing(value):
            return None
        text = str(value).strip()
        return text or None

    @classmethod
    def _source_metadata(cls, rule):
        source_name = cls._clean_metadata(rule.get("source_name"))
        source_url = cls._clean_metadata(rule.get("source_url"))

        invalid_names = {"unverified", "unknown", "unknown source"}
        parsed_url = urlparse(source_url or "")
        reference_available = (
            source_name is not None
            and source_name.lower() not in invalid_names
            and parsed_url.scheme.lower() in {"http", "https"}
            and bool(parsed_url.netloc)
            and "#" not in source_url
        )

        return {
            "source_name": source_name,
            "source_url": source_url,
            "source_notes": cls._clean_metadata(rule.get("source_notes")),
            "confidence": cls._clean_metadata(rule.get("confidence")),
            "last_checked": cls._clean_metadata(rule.get("last_checked")),
            "reference_available": reference_available,
            # The CSV contains no evidence that any reference was independently verified.
            "source_verified": False,
        }

    @staticmethod
    def _preferred_range(description, minimum, maximum):
        match = re.search(
            r"\boptimal\b[^.;]*?(-?\d+(?:\.\d+)?)\s*(?:-|to)\s*"
            r"(-?\d+(?:\.\d+)?)",
            description,
            flags=re.IGNORECASE,
        )
        if not match:
            return None

        preferred_minimum, preferred_maximum = map(float, match.groups())
        if (
            preferred_minimum <= preferred_maximum
            and minimum <= preferred_minimum
            and preferred_maximum <= maximum
        ):
            return preferred_minimum, preferred_maximum
        return None

    def __init__(self, csv_path="reports/agronomic_requirements_sources.csv"):
        self.csv_path = csv_path
        try:
            self.df = pd.read_csv(csv_path)
            self.df.columns = [
                self._normalize_name(column) for column in self.df.columns
            ]
            if "crop" in self.df.columns:
                self.df["crop"] = self.df["crop"].map(self._normalize_name)
            if "parameter" in self.df.columns:
                self.df["parameter"] = self.df["parameter"].map(
                    self._normalize_name
                )
        except (OSError, pd.errors.ParserError, UnicodeError) as error:
            self.df = pd.DataFrame()
            print(f"Warning: Could not load {csv_path}: {error}")

    def evaluate_crop(self, crop, inputs):
        normalized_inputs = {
            self._normalize_name(key): value for key, value in inputs.items()
        }
        normalized_crop = self._normalize_name(crop)
        crop_rules = (
            self.df[self.df["crop"] == normalized_crop]
            if not self.df.empty and "crop" in self.df.columns
            else pd.DataFrame()
        )

        checks = []
        supporting_reasons = []
        warnings = []
        missing_information = []
        unavailable_rules = []
        insufficient_evidence = []
        invalid_information = []
        sources = {}
        lowest_rating = 4
        has_unsuitable = False
        has_evaluations = False

        def append_unique(items, value):
            if value not in items:
                items.append(value)

        for parameter in self.TRACKED_PARAMETERS:
            display_parameter = "pH" if parameter == "ph" else parameter
            user_value = normalized_inputs.get(parameter)
            has_input = not self._is_missing_input(user_value)

            rules = (
                crop_rules[crop_rules["parameter"] == parameter]
                if not crop_rules.empty and "parameter" in crop_rules.columns
                else pd.DataFrame()
            )

            if rules.empty:
                append_unique(unavailable_rules, display_parameter)
                if not has_input:
                    append_unique(missing_information, display_parameter)
                else:
                    append_unique(insufficient_evidence, display_parameter)
                checks.append({
                    "parameter": display_parameter,
                    "input": str(user_value) if has_input else "Unknown",
                    "assessment": "Insufficient Information",
                    "reason": (
                        f"No crop-specific rule is available for "
                        f"{display_parameter}."
                    ),
                    **self._source_metadata({}),
                })
                continue

            rule = rules.iloc[0]
            metadata = self._source_metadata(rule)
            if metadata["reference_available"]:
                source_key = (metadata["source_name"], metadata["source_url"])
                sources[source_key] = metadata.copy()

            if not metadata["reference_available"]:
                append_unique(insufficient_evidence, display_parameter)
                checks.append({
                    "parameter": display_parameter,
                    "input": str(user_value) if has_input else "Unknown",
                    "assessment": "Insufficient Information",
                    "reason": (
                        "The crop rule has no usable source reference, so it "
                        "cannot be relied on for a suitability assessment."
                    ),
                    **metadata,
                })
                if not has_input:
                    append_unique(missing_information, display_parameter)
                continue

            if not has_input:
                append_unique(missing_information, display_parameter)
                checks.append({
                    "parameter": display_parameter,
                    "input": "Unknown",
                    "assessment": "Insufficient Information",
                    "reason": "No input provided by the farmer.",
                    **metadata,
                })
                continue

            if parameter in self.QUALITATIVE_PARAMETERS:
                append_unique(insufficient_evidence, display_parameter)
                checks.append({
                    "parameter": display_parameter,
                    "input": str(user_value),
                    "assessment": "Insufficient Information",
                    "reason": (
                        "The farmer supplied this information, but the "
                        "available crop description is not a validated "
                        "comparison rule."
                    ),
                    **metadata,
                })
                continue

            try:
                value = float(user_value)
                if not math.isfinite(value):
                    raise ValueError("The value must be finite.")
            except (TypeError, ValueError, OverflowError):
                append_unique(invalid_information, display_parameter)
                append_unique(insufficient_evidence, display_parameter)
                warnings.append(
                    f"{display_parameter} value {user_value!r} is not a valid "
                    "finite number."
                )
                checks.append({
                    "parameter": display_parameter,
                    "input": str(user_value),
                    "assessment": "Invalid Input",
                    "reason": "The supplied value must be a finite number.",
                    **metadata,
                })
                continue

            unit = self._clean_metadata(rule.get("unit")) or ""
            try:
                minimum = float(rule.get("minimum"))
                maximum = float(rule.get("maximum"))
                range_is_valid = (
                    math.isfinite(minimum)
                    and math.isfinite(maximum)
                    and minimum <= maximum
                )
            except (TypeError, ValueError, OverflowError):
                range_is_valid = False
                minimum = maximum = None

            if not range_is_valid:
                append_unique(insufficient_evidence, display_parameter)
                checks.append({
                    "parameter": display_parameter,
                    "input": f"{value}{unit}",
                    "assessment": "Insufficient Information",
                    "reason": (
                        "A complete, valid numerical range is unavailable "
                        "for this parameter."
                    ),
                    **metadata,
                })
                continue

            description = (
                self._clean_metadata(
                    rule.get("preferred_value_or_description")
                )
                or ""
            )
            preferred_range = self._preferred_range(
                description, minimum, maximum
            )

            if value < minimum or value > maximum:
                assessment = "Unsuitable"
                reason = (
                    f"Input value {value}{unit} is outside the documented "
                    f"acceptable range of {minimum} to {maximum}{unit}."
                )
                warnings.append(
                    f"{display_parameter} value {value}{unit} is unsuitable."
                )
                has_unsuitable = True
            elif preferred_range and preferred_range[0] <= value <= preferred_range[1]:
                assessment = "Highly Suitable"
                reason = (
                    f"Input value {value}{unit} falls within the explicitly "
                    f"documented preferred range of {preferred_range[0]} to "
                    f"{preferred_range[1]}{unit}."
                )
                supporting_reasons.append(
                    f"{display_parameter} is in the documented preferred range."
                )
                lowest_rating = min(lowest_rating, 4)
            else:
                assessment = "Suitable"
                if preferred_range:
                    reason = (
                        f"Input value {value}{unit} is within the acceptable "
                        "range but outside the documented preferred range."
                    )
                else:
                    reason = (
                        f"Input value {value}{unit} is within the documented "
                        "acceptable range; no preferred numerical range is "
                        "provided."
                    )
                supporting_reasons.append(
                    f"{display_parameter} is within the acceptable range."
                )
                lowest_rating = min(lowest_rating, 3)

            has_evaluations = True
            checks.append({
                "parameter": display_parameter,
                "input": f"{value}{unit}",
                "assessment": assessment,
                "reason": reason,
                **metadata,
            })

        if has_unsuitable:
            overall_status = "Unsuitable"
        elif unavailable_rules or insufficient_evidence or not has_evaluations:
            overall_status = "Insufficient Information"
        else:
            overall_status = (
                "Highly Suitable" if lowest_rating == 4 else "Suitable"
            )

        return {
            "crop": crop,
            "overall_status": overall_status,
            "checks": checks,
            "supporting_reasons": supporting_reasons,
            "warnings": warnings,
            "missing_information": missing_information,
            "unavailable_rules": unavailable_rules,
            "insufficient_evidence": insufficient_evidence,
            "invalid_information": invalid_information,
            "sources": list(sources.values()),
        }
