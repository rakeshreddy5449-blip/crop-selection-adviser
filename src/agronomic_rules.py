import json
import math
import re
from urllib.parse import urlparse

import pandas as pd


class AgronomicSuitabilityEngine:
    PARAMETERS = ("pH", "temperature", "rainfall", "soil_texture", "irrigation")
    RESEARCH_COLUMNS = {
        "crop",
        "parameter",
        "evidence_status",
        "publication_title",
        "author_or_institution",
        "direct_url",
        "page_section_or_table",
        "claim_or_requirement",
        "minimum",
        "maximum",
        "unit",
        "range_type",
        "growing_conditions_context",
        "verification_status",
        "research_notes",
    }
    VERIFIED_METADATA_COLUMNS = (
        "publication_title",
        "author_or_institution",
        "direct_url",
        "claim_or_requirement",
    )
    DEFAULT_LEGACY_PATH = "reports/agronomic_requirements_sources.csv"
    DEFAULT_RESEARCH_PATH = "reports/agronomic_evidence_research.csv"
    DEFAULT_METADATA_PATH = "models/metadata.json"

    @staticmethod
    def _normalize_parameter(value):
        normalized = re.sub(r"[\s-]+", "_", str(value).strip().lower())
        aliases = {
            "ph": "pH",
            "temperature": "temperature",
            "rainfall": "rainfall",
            "soil_texture": "soil_texture",
            "irrigation": "irrigation",
        }
        return aliases.get(normalized)

    @staticmethod
    def _is_missing(value):
        if value is None:
            return True
        if isinstance(value, str):
            return not value.strip() or value.strip().upper() == "UNKNOWN"
        try:
            return bool(pd.isna(value))
        except (TypeError, ValueError):
            return False

    @classmethod
    def _value(cls, row, name):
        if row is None:
            return None
        value = row.get(name)
        if cls._is_missing(value):
            return None
        return str(value).strip()

    @staticmethod
    def _canonical_columns(columns):
        return [str(column).strip().lower() for column in columns]

    def __init__(
        self,
        csv_path=DEFAULT_LEGACY_PATH,
        research_csv_path=DEFAULT_RESEARCH_PATH,
        metadata_path=DEFAULT_METADATA_PATH,
        crop_labels=None,
    ):
        self.csv_path = csv_path
        self.research_csv_path = research_csv_path
        self.metadata_path = metadata_path
        self.validation_warnings = []
        self.research_validation_errors = []
        self.crop_labels, labels_error = self._load_crop_labels(crop_labels)
        if labels_error:
            self.research_validation_errors.append(labels_error)

        self.legacy_df = self._load_legacy()
        self._research_records = {}
        self._duplicate_records = set()
        self._research_unavailable = False
        self._load_research_register()

    def _load_crop_labels(self, crop_labels):
        if crop_labels is not None:
            labels = [str(label).strip() for label in crop_labels]
            if not labels or len(labels) != len(set(labels)):
                return [], "Crop labels are empty or duplicated."
            return labels, None

        try:
            with open(self.metadata_path, "r", encoding="utf-8") as file:
                metadata = json.load(file)
            labels = metadata.get("classes")
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            return [], f"Could not load exact crop labels: {error}"

        if not isinstance(labels, list) or not labels:
            return [], "Model metadata does not contain a non-empty classes list."
        labels = [str(label).strip() for label in labels]
        if any(not label for label in labels) or len(labels) != len(set(labels)):
            return [], "Model crop labels are empty or duplicated."
        return labels, None

    def _load_legacy(self):
        try:
            legacy = pd.read_csv(self.csv_path, dtype=str, keep_default_na=False)
            legacy.columns = self._canonical_columns(legacy.columns)
            if {"crop", "parameter"} - set(legacy.columns):
                self.validation_warnings.append(
                    "Legacy requirements file is missing crop or parameter "
                    "columns; historical rows are unavailable."
                )
                return pd.DataFrame()
            legacy["crop"] = legacy["crop"].astype(str).str.strip()
            legacy["parameter"] = legacy["parameter"].map(
                self._normalize_parameter
            )
            return legacy
        except (
            OSError,
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
            UnicodeError,
        ) as error:
            self.validation_warnings.append(
                f"Legacy requirements could not be loaded and will not be "
                f"available as historical metadata: {error}"
            )
            return pd.DataFrame()

    def _load_research_register(self):
        try:
            research = pd.read_csv(
                self.research_csv_path,
                dtype=str,
                keep_default_na=False,
            )
        except (
            OSError,
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
            UnicodeError,
        ) as error:
            self._research_unavailable = True
            self.research_validation_errors.append(
                f"Research register could not be read: {error}"
            )
            return

        research.columns = self._canonical_columns(research.columns)
        if len(research.columns) != len(set(research.columns)):
            self._research_unavailable = True
            self.research_validation_errors.append(
                "Research register has duplicate column names after "
                "normalization."
            )
            return

        missing_columns = self.RESEARCH_COLUMNS - set(research.columns)
        if missing_columns:
            self._research_unavailable = True
            self.research_validation_errors.append(
                "Research register is missing required columns: "
                + ", ".join(sorted(missing_columns))
            )
            return

        if not self.crop_labels:
            self._research_unavailable = True
            return

        for index, row in research.iterrows():
            crop = str(row["crop"]).strip()
            parameter = self._normalize_parameter(row["parameter"])
            if crop not in self.crop_labels:
                self.research_validation_errors.append(
                    f"Research row {index + 2} uses crop label {crop!r}, "
                    "which is not an exact model crop label."
                )
                continue
            if parameter not in self.PARAMETERS:
                self.research_validation_errors.append(
                    f"Research row {index + 2} uses unsupported parameter "
                    f"{row['parameter']!r}."
                )
                continue

            key = (crop, parameter)
            if key in self._research_records:
                self._duplicate_records.add(key)
                self.research_validation_errors.append(
                    f"Duplicate research record for {crop}/{parameter}."
                )
                continue

            record = row.to_dict()
            status = str(record["evidence_status"]).strip().upper()
            if status not in {"VERIFIED", "UNKNOWN"}:
                self.research_validation_errors.append(
                    f"Research record for {crop}/{parameter} has invalid "
                    f"evidence_status {record['evidence_status']!r}; treated "
                    "as UNKNOWN."
                )
                status = "UNKNOWN"
            if status == "VERIFIED":
                missing_metadata = [
                    column for column in self.VERIFIED_METADATA_COLUMNS
                    if self._is_missing(record.get(column))
                ]
                verified_marker = str(
                    record.get("verification_status", "")
                ).strip().upper()
                direct_url = str(record.get("direct_url", "")).strip()
                parsed_url = urlparse(direct_url)
                if (
                    missing_metadata
                    or verified_marker != "SOURCE_CONTENT_VERIFIED"
                    or parsed_url.scheme.lower() not in {"http", "https"}
                    or not parsed_url.netloc
                ):
                    self.research_validation_errors.append(
                        f"Research record for {crop}/{parameter} is marked "
                        "VERIFIED without complete source-content metadata; "
                        "treated as UNKNOWN."
                    )
                    status = "UNKNOWN"
            record["_effective_status"] = status
            self._research_records[key] = record

        expected = {
            (crop, parameter)
            for crop in self.crop_labels
            for parameter in self.PARAMETERS
        }
        for crop, parameter in sorted(expected - set(self._research_records)):
            self.research_validation_errors.append(
                f"Missing research record for {crop}/{parameter}; treated as "
                "UNKNOWN."
            )

        if self._duplicate_records:
            self.validation_warnings.append(
                f"{len(self._duplicate_records)} duplicate crop/parameter "
                "record(s) found; duplicate combinations are treated as "
                "UNKNOWN."
            )
        if self.research_validation_errors:
            self.validation_warnings.append(
                "Research register validation found issues; affected "
                "evidence is treated as UNKNOWN."
            )

    def _legacy_record(self, crop, parameter):
        if self.legacy_df.empty:
            return None
        matches = self.legacy_df[
            (self.legacy_df["crop"] == crop)
            & (self.legacy_df["parameter"] == parameter)
        ]
        if matches.empty:
            return None
        return matches.iloc[0].to_dict()

    @staticmethod
    def _range_conflict(evidence, legacy):
        if evidence is None or legacy is None:
            return False, "NOT_COMPARABLE"
        research_unit = str(evidence.get("unit", "")).strip().lower()
        legacy_unit = str(legacy.get("unit", "")).strip().lower()
        if not research_unit or research_unit != legacy_unit:
            return False, "NOT_COMPARABLE"
        try:
            research_range = (
                float(evidence.get("minimum")),
                float(evidence.get("maximum")),
            )
            legacy_range = (
                float(legacy.get("minimum")),
                float(legacy.get("maximum")),
            )
        except (TypeError, ValueError, OverflowError):
            return False, "NOT_COMPARABLE"
        if not all(map(math.isfinite, research_range + legacy_range)):
            return False, "NOT_COMPARABLE"
        if research_range != legacy_range:
            return True, "RANGE_CONFLICT"
        return False, "RANGE_MATCH_ONLY"

    def _research_evidence(self, crop, parameter):
        key = (crop, parameter)
        record = self._research_records.get(key)
        if self._research_unavailable or key in self._duplicate_records:
            return None, "UNKNOWN"
        if record is None:
            return None, "UNKNOWN"
        return record, record["_effective_status"]

    def evaluate_crop(self, crop, inputs):
        crop_label = str(crop).strip()
        normalized_inputs = {
            re.sub(r"[\s-]+", "_", str(key).strip().lower()): value
            for key, value in inputs.items()
        }
        checks = []
        missing_information = []
        unknown_evidence = []
        insufficient_evidence = []
        unavailable_rules = []
        legacy_unverified = []
        legacy_conflicts = []
        sources = {}
        warnings = list(self.validation_warnings)
        if self.research_validation_errors:
            first_issue = self.research_validation_errors[0]
            remaining = len(self.research_validation_errors) - 1
            suffix = f" ({remaining} additional issue(s))." if remaining else ""
            warnings.append(
                f"Research register validation issue: {first_issue}{suffix}"
            )

        crop_is_supported = crop_label in self.crop_labels
        if not crop_is_supported:
            warnings.append(
                f"Crop {crop_label!r} is not an exact model crop label."
            )

        for parameter in self.PARAMETERS:
            input_key = parameter.lower()
            user_value = normalized_inputs.get(input_key)
            has_input = not self._is_missing(user_value)
            if not has_input:
                missing_information.append(parameter)

            if not crop_is_supported:
                evidence, evidence_status = None, "UNKNOWN"
            else:
                evidence, evidence_status = self._research_evidence(
                    crop_label, parameter
                )

            legacy = self._legacy_record(crop_label, parameter)
            if legacy is not None:
                legacy_minimum = self._value(legacy, "minimum")
                legacy_maximum = self._value(legacy, "maximum")
                legacy_value = {
                    "minimum": legacy_minimum,
                    "maximum": legacy_maximum,
                    "unit": self._value(legacy, "unit"),
                    "preferred_value_or_description": self._value(
                        legacy, "preferred_value_or_description"
                    ),
                    "source_name": self._value(legacy, "source_name"),
                    "source_url": self._value(legacy, "source_url"),
                    "source_notes": self._value(legacy, "source_notes"),
                }
                legacy_state = (
                    "NOT_VERIFIED"
                    if evidence_status == "UNKNOWN"
                    else "NOT_USED_FOR_SUITABILITY"
                )
            else:
                legacy_value = None
                legacy_state = "NO_LEGACY_RECORD"

            if evidence_status == "VERIFIED":
                legacy_conflict, comparable_legacy_state = (
                    self._range_conflict(evidence, legacy)
                )
            else:
                legacy_conflict, comparable_legacy_state = (
                    False,
                    "NOT_VERIFIED",
                )
            if evidence_status == "VERIFIED" and legacy is not None:
                legacy_state = comparable_legacy_state
            effective_evidence_status = (
                "CONFLICTING" if legacy_conflict else evidence_status
            )
            if legacy_conflict:
                legacy_conflicts.append(parameter)

            if evidence_status != "VERIFIED":
                unknown_evidence.append(parameter)
                insufficient_evidence.append(parameter)
                if legacy is None:
                    unavailable_rules.append(parameter)
                else:
                    legacy_unverified.append(parameter)
                check = {
                    "parameter": parameter,
                    "input": str(user_value) if has_input else "Unknown",
                    "assessment": "Insufficient Information",
                    "evidence_status": evidence_status,
                    "effective_evidence_status": effective_evidence_status,
                    "source_verified": False,
                    "reference_available": bool(
                        self._value(evidence, "direct_url")
                    ),
                    "publication_title": self._value(
                        evidence, "publication_title"
                    ),
                    "author_or_institution": self._value(
                        evidence, "author_or_institution"
                    ),
                    "source_name": self._value(
                        evidence, "author_or_institution"
                    ),
                    "source_url": self._value(evidence, "direct_url"),
                    "page_section_or_table": self._value(
                        evidence, "page_section_or_table"
                    ),
                    "claim_or_requirement": self._value(
                        evidence, "claim_or_requirement"
                    ),
                    "minimum": self._value(evidence, "minimum"),
                    "maximum": self._value(evidence, "maximum"),
                    "unit": self._value(evidence, "unit"),
                    "range_type": self._value(evidence, "range_type"),
                    "growing_conditions_context": self._value(
                        evidence, "growing_conditions_context"
                    ),
                    "limitations": self._value(evidence, "research_notes"),
                    "verification_status": self._value(
                        evidence, "verification_status"
                    ) or "NOT_VERIFIED",
                    "legacy_data_status": legacy_state,
                    "legacy_conflict": legacy_conflict,
                    "legacy_reference": legacy_value,
                    "reason": (
                        "Adequate crop-specific evidence is unknown or "
                        "unavailable. Legacy values are preserved as "
                        "historical metadata and are not used to assess "
                        "suitability."
                    ),
                }
            else:
                source_url = self._value(evidence, "direct_url")
                source_name = self._value(
                    evidence, "author_or_institution"
                )
                source_key = (source_name, source_url)
                source_data = {
                    "source_name": source_name,
                    "source_url": source_url,
                    "publication_title": self._value(
                        evidence, "publication_title"
                    ),
                    "page_section_or_table": self._value(
                        evidence, "page_section_or_table"
                    ),
                    "claim_or_requirement": self._value(
                        evidence, "claim_or_requirement"
                    ),
                    "unit": self._value(evidence, "unit"),
                    "growing_conditions_context": self._value(
                        evidence, "growing_conditions_context"
                    ),
                    "limitations": self._value(evidence, "research_notes"),
                    "verification_status": self._value(
                        evidence, "verification_status"
                    ),
                    "source_verified": True,
                }
                sources[source_key] = source_data
                check = {
                    "parameter": parameter,
                    "input": str(user_value) if has_input else "Unknown",
                    "assessment": "Evidence Available - No Suitability Assessment",
                    "evidence_status": "VERIFIED",
                    "effective_evidence_status": effective_evidence_status,
                    "source_verified": True,
                    "reference_available": bool(source_url),
                    "publication_title": source_data["publication_title"],
                    "author_or_institution": source_name,
                    "source_name": source_name,
                    "source_url": source_url,
                    "page_section_or_table": source_data[
                        "page_section_or_table"
                    ],
                    "claim_or_requirement": source_data[
                        "claim_or_requirement"
                    ],
                    "minimum": self._value(evidence, "minimum"),
                    "maximum": self._value(evidence, "maximum"),
                    "unit": source_data["unit"],
                    "range_type": self._value(evidence, "range_type"),
                    "growing_conditions_context": source_data[
                        "growing_conditions_context"
                    ],
                    "limitations": source_data["limitations"],
                    "verification_status": source_data[
                        "verification_status"
                    ],
                    "legacy_data_status": legacy_state,
                    "legacy_conflict": legacy_conflict,
                    "legacy_reference": legacy_value,
                    "reason": (
                        "The source supports this context-specific claim, "
                        "but does not provide a validated comparison rule "
                        "for the farmer's input."
                    ),
                }

            if legacy is not None:
                warnings.append(
                    f"{crop_label} {parameter}: legacy values are retained "
                    "for reference only and do not authorize a suitability "
                    "assessment."
                )
            checks.append(check)

        if self._research_unavailable:
            overall_status = "Insufficient Information"
        else:
            overall_status = "Insufficient Information"

        return {
            "crop": crop_label,
            "overall_status": overall_status,
            "suitability_status": "Cannot Determine",
            "checks": checks,
            "supporting_reasons": [],
            "warnings": list(dict.fromkeys(warnings)),
            "missing_information": missing_information,
            "unavailable_rules": unavailable_rules,
            "insufficient_evidence": insufficient_evidence,
            "unknown_evidence": unknown_evidence,
            "legacy_unverified": legacy_unverified,
            "legacy_conflicts": legacy_conflicts,
            "invalid_information": [],
            "sources": list(sources.values()),
            "research_register_valid": (
                not self._research_unavailable
                and not self.research_validation_errors
            ),
            "research_validation_errors": list(
                self.research_validation_errors
            ),
        }
