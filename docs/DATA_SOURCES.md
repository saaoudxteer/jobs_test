# Data Sources

This document records the public data sources used for the France-first version of the job-market AI exposure treemap.

## Final Source Decision

The final visualization uses Eurostat ISCO-08 two-digit occupation groups for France.

Reason:

- The data is official, public, reproducible, and accessible through stable API endpoints.
- It supports a France-first view while remaining compatible with European labor-market comparisons.
- It avoids relying on local files that turned out to be anti-bot HTML pages, 404 responses, or synthetic test data.

Tradeoff:

- ISCO two-digit groups are less granular than the ideal DARES 225-metier product.
- The gain is credibility and reproducibility.

## Source 1: Eurostat Employment

Dataset:

`lfsa_egai2d`

Name:

Employed persons by detailed occupation (ISCO-08 two digit level).

Use:

- Occupation backbone.
- France employment counts.
- 2019-2024 employment trend.

API:

```text
https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/lfsa_egai2d?lang=en&freq=A&unit=THS_PER&sex=T&age=Y_GE15&geo=FR&sinceTimePeriod=2019&untilTimePeriod=2024
```

Browser:

```text
https://ec.europa.eu/eurostat/databrowser/view/lfsa_egai2d/default/table?lang=en
```

Local cache:

`data/raw/eurostat_lfsa_egai2d_fr_2019_2024.json`

## Source 2: Eurostat Earnings

Dataset:

`earn_ses22_25`

Name:

Mean monthly earnings by sex, occupation and size class of the enterprise.

Use:

- Gross monthly earnings proxy.
- France, 2022.
- ISCO major-group level.

API:

```text
https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/earn_ses22_25?lang=en&freq=A&sex=T&indic_se=ERN&unit=EUR&geo=FR
```

Browser:

```text
https://ec.europa.eu/eurostat/databrowser/view/earn_ses22_25/default/table?lang=en
```

Local cache:

`data/raw/eurostat_earn_ses22_25_fr.json`

Important limitation:

The API response provides salary values by enterprise size class and does not include a total size-class category for the selected view. The build uses a simple average across available enterprise size classes. The result is a salary proxy, not a direct salary estimate for every two-digit occupation.

Missing values:

Eurostat does not publish usable salary values in this pull for armed forces, agriculture, and plant/machine operator major groups. These salary cells are left blank instead of imputing unverifiable values.

## Source 3: Eurostat Education

Dataset:

`lfsa_egised`

Name:

Employed persons by occupation and educational attainment level.

Use:

- Dominant education level by occupation major group.
- France, 2024.

API:

```text
https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/lfsa_egised?lang=en&freq=A&unit=THS_PER&sex=T&age=Y_GE15&geo=FR&time=2024
```

Browser:

```text
https://ec.europa.eu/eurostat/databrowser/view/lfsa_egised/default/table?lang=en
```

Local cache:

`data/raw/eurostat_lfsa_egised_fr_2024.json`

Limitation:

Education data is available at ISCO major-group level in this build. Two-digit occupations inherit the dominant education level of their major group.

## Source 4: DARES FAP 2021

Dataset:

La nomenclature des familles professionnelles 2021.

Use:

- French occupational taxonomy reference.
- Credibility check for French labor-market terminology.

Browser:

```text
https://www.data.gouv.fr/datasets/la-nomenclature-des-familles-professionnelles-2021
```

Local file:

`data/fap_2021.csv`

Note:

The current treemap uses ISCO groups rather than FAP groups because Eurostat provides a cleaner reproducible employment backbone for this public prototype.

## Rejected Local Files

These files are intentionally not used in the final pipeline:

- `data/metiers_2030.xlsx`: local file contains anti-bot/security HTML, not an Excel workbook.
- `data/insee_salaries_2023.xlsx`: local file contains HTML, not an Excel workbook.
- `data/rome_fiches.json`: local file is a 404 HTML page, not JSON.
- `scores.json`: original US scores, not French scores.
- `synthetic_scores.json`: test data only.

## AI Exposure Scores

The AI score is not an official source. It is an analytical rubric maintained in this repository.

Generated files:

- `scores_fr.json`
- `site/data.json`

Each score includes a French rationale explaining why the occupation is exposed or protected, based on digital task share, data/document intensity, physical constraints, human interaction, safety, regulation, and on-site work.
