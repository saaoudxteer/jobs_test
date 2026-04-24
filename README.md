# Les metiers francais face a l'IA

Interactive treemap inspired by the original [US Job Market Visualizer](https://github.com/karpathy/jobs), rebuilt for the French labor market with official European public data.

The goal is simple: show which French occupation groups are most exposed to current AI tools, without pretending that exposure means job disappearance. The visualization keeps the original treemap-first UI and adapts the data, copy, labels, sources, and scoring rationales for a French/European context.

## Live Concept

Each rectangle represents one occupation group in France.

- Area: number of employed people in 2024.
- Color: selected metric.
- Default layer: AI exposure score from 0 to 10.
- Tooltip: employment, trend, salary proxy, education level, AI score, and the reason behind the score.

Available layers:

- `Exposition IA`: analytical score with a French rationale for every occupation.
- `Tendance 2019-2024`: employment change from Eurostat labor-force data.
- `Salaire`: gross monthly salary proxy from Eurostat SES 2022.
- `Diplome`: dominant education level by ISCO major group.

## Data Scope

The current version is France-first and uses Eurostat ISCO-08 two-digit occupation groups.

- 41 occupation groups.
- 28,520,500 employed people represented in France in 2024.
- 41/41 occupations have an AI exposure score and rationale.
- Salary is available for 33/41 groups. Missing salary values are left blank when Eurostat does not publish them in the selected table.

This is less granular than a 225-metier DARES product, but it is fully reproducible from accessible official sources and works cleanly for a public LinkedIn-ready prototype.

## Data Sources

Primary official sources:

- Eurostat `lfsa_egai2d`: employed persons by detailed occupation, France, 2019-2024.
- Eurostat `earn_ses22_25`: gross monthly earnings by occupation and enterprise size class, France, 2022.
- Eurostat `lfsa_egised`: employed persons by occupation and educational attainment level, France, 2024.
- DARES FAP 2021: French occupation taxonomy reference.

Detailed source notes are in [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md), [data/source_manifest.json](data/source_manifest.json), and [data/source_checks.md](data/source_checks.md).

## Project Files

| Path | Purpose |
| --- | --- |
| `site/index.html` | Static treemap UI, regenerated from the original committed design and localized for France. |
| `site/data.json` | Compact frontend dataset consumed by the site. |
| `build_fr_dataset.py` | Reproducible Eurostat data pull, normalization, scoring, and JSON/CSV export. |
| `build_fr_site.py` | Rebuilds the localized site from the original UI baseline. |
| `build_site_data.py` | Compatibility wrapper that runs the France dataset build. |
| `occupations.csv` | Human-readable generated occupation table. |
| `occupations.json` | Generated occupation data with metadata. |
| `scores_fr.json` | AI exposure scores and French rationales. |
| `data/raw/` | Cached Eurostat API responses used by the build. |
| `GPT.md` | Working project plan and implementation context for future agents. |

## Run Locally

Use Python 3.11+.

```bash
python build_fr_dataset.py
python build_fr_site.py
cd site
python -m http.server 8000
```

Open:

```text
http://127.0.0.1:8000/
```

The local server is required because the page loads `data.json` with `fetch()`.

## Rebuild Data

```bash
python build_fr_dataset.py
```

This writes:

- `data/raw/*.json`
- `data/source_manifest.json`
- `data/source_checks.md`
- `occupations.csv`
- `occupations.json`
- `scores_fr.json`
- `site/data.json`

The script uses cached raw files if a network call fails.

## Rebuild Site

```bash
python build_fr_site.py
```

This regenerates `site/index.html` from the original committed `site/index.html` through `git show HEAD:site/index.html`, then applies France-specific labels, legends, units, and source copy.

## Methodology

AI exposure is a project estimate, not an official statistic. A higher score means the occupation contains more tasks that current AI systems can transform through automation, assistance, productivity gains, or task redesign.

The score considers:

- Digital work share.
- Text, code, data, reporting, and document workflows.
- Repetitive or structured information processing.
- Need for physical presence.
- Human relationship, care, teaching, negotiation, or trust.
- Regulation, responsibility, safety, and judgment.
- On-site constraints and unpredictable environments.

A high score does not mean the job disappears. It means the work content is more likely to change.

## Validation

Current validation checks:

```bash
python -m json.tool site/data.json
python -m json.tool data/source_manifest.json
```

Expected current dataset:

- `41` occupations.
- `28,520,500` represented employed people.
- `41` AI rationales.
- `33` groups with salary proxy values.

## Credits

Original idea and UI inspiration: [karpathy/jobs](https://github.com/karpathy/jobs).

French/European adaptation, data pipeline, source manifest, and AI exposure rationales are specific to this repository.
