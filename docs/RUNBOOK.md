# Runbook

## Requirements

- Python 3.11 or newer.
- Internet access if you want to refresh Eurostat data.
- A browser for the static site preview.

No API key is required for the France-first Eurostat build.

## Fresh Build

From the repository root:

```bash
python build_fr_dataset.py
python build_fr_site.py
```

## Preview

```bash
cd site
python -m http.server 8000
```

Open:

```text
http://127.0.0.1:8000/
```

## Validate Outputs

```bash
python -m json.tool site/data.json
python -m json.tool data/source_manifest.json
```

Expected current output:

- 41 occupations.
- 28,520,500 represented employed people.
- 41 AI exposure rationales.
- 33 occupations with salary proxy values.

## Files To Commit

Commit these files for the France build:

- `README.md`
- `GPT.md`
- `build_fr_dataset.py`
- `build_fr_site.py`
- `build_site_data.py`
- `occupations.csv`
- `occupations.json`
- `scores_fr.json`
- `site/index.html`
- `site/data.json`
- `data/fap_2021.csv`
- `data/raw/*.json`
- `data/source_manifest.json`
- `data/source_checks.md`
- `docs/*.md`

Do not commit local experiments such as `agent*.py`, `synthetic_scores.json`, or `site/heatmap.html`.
