# Source Checks

Generated: 2026-04-24

## Final Source Decision

- Final occupation backbone: Eurostat ISCO-08 two-digit occupations for France (41 occupations with 2024 employment data).
- This is less granular than the desired DARES 225-metier product, but it is fully accessible, official, Europe-compatible, and reproducible.
- DARES FAP 2021 remains documented as the French taxonomy reference.

## Verified Sources

### eurostat_lfsa_egai2d

- Publisher: Eurostat
- URL: https://ec.europa.eu/eurostat/databrowser/view/lfsa_egai2d/default/table?lang=en
- Retrieved: 2026-04-24
- Last update: 2026-04-17T11:00:00+0200
- Fields used: employment by ISCO-08 occupation, France, 2019-2024
- Note: None

### eurostat_earn_ses22_25

- Publisher: Eurostat
- URL: https://ec.europa.eu/eurostat/databrowser/view/earn_ses22_25/default/table?lang=en
- Retrieved: 2026-04-24
- Last update: 2026-02-09T23:00:00+0100
- Fields used: gross monthly earnings by ISCO-08 major group, France, 2022
- Note: SES salary data is available at ISCO major-group level by enterprise size class, without a total size-class category in this API response. The build uses a simple average across available size classes, then two-digit occupations inherit their major-group salary proxy.

### eurostat_lfsa_egised

- Publisher: Eurostat
- URL: https://ec.europa.eu/eurostat/databrowser/view/lfsa_egised/default/table?lang=en
- Retrieved: 2026-04-24
- Last update: 2026-04-17T11:00:00+0200
- Fields used: dominant education attainment by ISCO-08 major group, France, 2024
- Note: Education is available at ISCO major-group level here; two-digit occupations inherit their major-group education proxy.

### dares_fap_2021

- Publisher: DARES - service statistique du ministère en charge du Travail
- URL: https://www.data.gouv.fr/datasets/la-nomenclature-des-familles-professionnelles-2021
- Retrieved: 2026-04-24
- Last update: 2024-04-30
- Fields used: French occupational taxonomy reference only in this build
- Note: Local data/fap_2021.csv is readable and used as a credibility reference; the final site uses Eurostat ISCO groups for comparable employment data.

### project_ai_rubric

- Publisher: This repository
- URL: n/a
- Retrieved: 2026-04-24
- Last update: n/a
- Fields used: AI exposure score and French rationale
- Note: AI exposure scores are analytical estimates, not official statistics and not disappearance predictions.

## Known Limitations

- Salary is an official Eurostat SES 2022 proxy, not a direct salary observation for every two-digit occupation.
- Eurostat SES values are not available in this pull for armed forces, agriculture, and plant/machine operator major groups; the site leaves those salary cells blank instead of imputing unverifiable values.
- AI exposure scores are project estimates with written rationales, not official labor-market forecasts.

## Rejected Local Files

- `data/metiers_2030.xlsx`: not used; local file starts with HTML/anti-bot security content, not an Excel workbook.
- `data/insee_salaries_2023.xlsx`: not used; local file starts with HTML, not an Excel workbook.
- `data/rome_fiches.json`: not used; local file is a 404 HTML page, not JSON.
- `scores.json`: not used for the French build; it contains the original US occupation scores.
- `synthetic_scores.json`: not used; it is test data only.
