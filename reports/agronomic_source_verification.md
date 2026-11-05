# Agronomic Source Verification Log

**Checked:** 2026-11-05  
**Verification rule:** A reference is verified for a claim only if the cited publication/page was accessed and its content directly supports that crop/parameter statement. An institutional homepage, a URL that merely responds, or a search-result excerpt does not meet this rule.

## Source supporting a research-register entry

| Source | Access result | What the source directly supports | What it does not support |
|---|---|---|---|
| International Rice Research Institute (IRRI), Rice Knowledge Bank, “How to manage water,” <http://knowledgebank.irri.org/step-by-step-production/growth/water-management> | Page content accessed successfully on 2026-11-05. | Rice is typically grown in bunded fields with continuous flooding until 7–10 days before harvest. The page reports seasonal field water input of 400 mm in heavy clay soils with shallow groundwater to >2,000 mm in coarse-textured soils with deep groundwater, and 1,300–1,500 mm as typical for irrigated rice in Asia. These statements support a context-specific rice irrigation/water-input entry. | Does not state a universal acceptable or optimal numerical range. These values are not rainfall requirements. Texture is discussed as a factor affecting water input and puddling, not as a preferred rice soil-texture classification. The page does not substantiate rice pH or temperature values. |

The CSV row records the source institution as author because no individual author was identified in the accessed page content. The numeric values are preserved in the claim/context text; the register uses `UNKNOWN` for universal minimum and maximum because the source describes different site conditions rather than one interchangeable range.

## Existing project references not promoted to verified evidence

The older project files contain claims and URLs, but their presence is not independent confirmation. The listed sources below were checked or reviewed as follows:

| Existing reference or lead | Check result | Evidence decision |
|---|---|---|
| FAO Crop Water Information URL recorded in the existing CSV: <https://www.fao.org/land-water/databases-chemical-properties/crop-information/en/> | Fetch returned HTTP 404 in the earlier coverage audit. No page content supporting the recorded rice pH claim was available in this check. | Not verified; do not use to substantiate the rice pH assertion. |
| IRRI homepage: <https://www.irri.org> | The homepage loads and establishes the institution identity, but is not a pinpoint crop-management citation for the existing rice temperature assertion. | Not verified for that claim. |
| IRRI Rice Knowledge Bank homepage: <http://www.knowledgebank.irri.org> | The recorded root URL failed with HTTP 500 in the earlier audit. The specific “How to manage water” page above is separately accessible and verified only for its own water-management statements. | Homepage is not evidence; the specific page supports only the qualified rice irrigation/water-input entry. |
| ICAR-National Rice Research Institute host: <https://nrri.icar.gov.in> | Host could not be resolved during the earlier audit. No specific publication/page supporting the existing soil-texture assertion was identified. | Not verified. |
| FAO homepage: <https://www.fao.org> | Resolves/redirects to general FAO homepage; it does not pinpoint the existing rice irrigation assertion. | Not verified for that claim. |
| Existing project records for maize, grapes, chickpea, and other crops | Existing reports/CSV include broad or placeholder references, including `UNVERIFIED` and `#`; no source content supporting claims was verified in this research pass. | Not counted as evidence. |
| Chickpea PDF discovered during research | Direct URL could not be accessed; search-result text alone was insufficient. | Not verified. |

Access failure does not prove a claim false; it means that this audit cannot verify the claim from the available source content. No project data was silently treated as corroboration.

## Verification totals

- **Verified source-content support:** one crop/parameter entry — rice irrigation/water input, with explicit production-context caveats.
- **Not verified / UNKNOWN:** 109 crop/parameter combinations.
- No source in this register is marked verified solely because it uses HTTP/HTTPS.

See [agronomic_evidence_research.csv](./agronomic_evidence_research.csv) for row-level status and [agronomic_evidence_gaps.md](./agronomic_evidence_gaps.md) for all unresolved combinations.
