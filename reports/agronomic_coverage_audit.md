# Agronomic Evidence Coverage Audit

**Dataset inspected:** `agronomic_requirements_sources.csv`  
**Audit date:** 2026-11-05  
**Scope:** Jute, Papaya, Coffee, Pigeonpeas, and Rice; parameters pH, temperature, rainfall, soil_texture, and irrigation.

## Coverage summary

| Crop | Rules documented in CSV | Rules missing from CSV | Numeric rule with missing minimum or maximum |
|---|---|---|---|
| Jute | pH | temperature, rainfall, soil_texture, irrigation | None. The pH row has minimum 5.5 and maximum 7.5. |
| Papaya | pH | temperature, rainfall, soil_texture, irrigation | None. The pH row has minimum 5.5 and maximum 7.5. |
| Coffee | pH | temperature, rainfall, soil_texture, irrigation | None. The pH row has minimum 5.5 and maximum 7.5. |
| Pigeonpeas | pH | temperature, rainfall, soil_texture, irrigation | None. The pH row has minimum 5.5 and maximum 7.5. |
| Rice | pH, temperature, rainfall, soil_texture, irrigation | None | None. pH, temperature, and rainfall have both minimum and maximum values. Soil texture and irrigation are qualitative rows and have no numeric range. |

“Documented” here means that a crop/parameter row exists in the CSV. It does not imply that its evidence is verified or adequate. Missing rules are absent crop/parameter rows; this audit does not assess whether any farmer supplied or omitted an input.

## Source and URL audit

The four placeholder crop rows (Jute, Papaya, Coffee, and Pigeonpeas) each have the same source metadata: source name `UNVERIFIED`, source URL `#`, and a generic “general loam baseline” note. The name is explicitly unverified and the URL is a placeholder, so the source cannot be independently verified from the recorded details. Their numerical pH fields are populated, but those values should not be treated as verified crop-specific evidence.

Rice has five rows. All five rows contain a non-empty source name and URL, but URL presence alone does not establish a source or verify the associated rule.

| Rice parameter | Recorded source name | Recorded URL | Missing/placeholder metadata? | Independent verification from recorded details |
|---|---|---|---|---|
| pH | FAO Crop Water Information | `https://www.fao.org/land-water/databases-chemical-properties/crop-information/en/` | Neither field is blank or a placeholder. | **Not verified.** A fetch of the recorded URL returned HTTP 404 on the audit date. The CSV does not provide a publication title, author, or pinpoint citation. |
| temperature | International Rice Research Institute (IRRI) | `https://www.irri.org` | Neither field is blank or a placeholder. | **Not verified.** The URL loads the IRRI homepage, which identifies the institution but is not a specific citation for the recorded temperature rule. |
| rainfall | IRRI Rice Knowledge Bank | `http://www.knowledgebank.irri.org` | Neither field is blank or a placeholder. | **Not verified.** The recorded HTTP URL could not be fetched successfully (HTTP 500 during this check). The CSV gives no specific page or publication title. |
| soil_texture | ICAR - National Rice Research Institute | `https://nrri.icar.gov.in` | Neither field is blank or a placeholder. | **Not verified.** The recorded host could not be resolved during this check. No specific publication or page is identified in the CSV. |
| irrigation | FAO Land & Water | `https://www.fao.org` | Neither field is blank or a placeholder. | **Not verified.** The URL redirects to the general FAO homepage. The CSV does not identify a specific page or publication that substantiates the irrigation rule. |

The fetch results are an access check performed on 2026-11-05, not proof that a source or claim is invalid. The CSV’s `source_notes`, `confidence`, and `last_checked` fields do not provide enough bibliographic detail to independently reproduce or confirm the cited rules. No sources in these five crops can be labeled independently verified based on the recorded details alone.

## Audit conclusions

- Jute, Papaya, Coffee, and Pigeonpeas each have only one pH rule row; their other four requested parameter rules are absent. Their pH row has placeholder source metadata and is not independently verifiable.
- Rice has rows for all five requested parameters. Its three numerical rules have both bounds; its two qualitative rules appropriately have no numeric minimum/maximum fields.
- None of the rice source references is independently confirmed as supporting its associated rule by the metadata recorded in the CSV. Some URLs resolve only to institutional homepages, and three checks failed to retrieve/resolve the recorded URL.
- No thresholds were inferred, transferred between crops, or changed as part of this audit. The CSV, recommendation logic, and model artifacts were not modified.
