# Presentation Notes

## One-Sentence Pitch

Une carte interactive des metiers francais face a l'IA, construite avec des donnees publiques Eurostat et une justification explicite pour chaque score d'exposition.

## What To Say

This project adapts the original US job-market treemap idea to France.

The surface of each rectangle shows how many people work in that occupation group. The color shows the selected metric: employment trend, salary proxy, education level, or AI exposure.

The default view is AI exposure. A high score does not mean the occupation disappears. It means the work is more likely to be transformed by current AI tools because it contains more digital, textual, analytical, administrative, or structured-information tasks.

## Why This Data Choice

I originally wanted a very granular French dataset, but credibility mattered more than size. The final version uses official Eurostat data because it is public, reproducible, and comparable across Europe.

The result is less granular than a full DARES 225-metier view, but stronger for a public prototype because every numeric field is documented and traceable.

## How To Launch Locally

From the repository root:

```bash
python build_fr_dataset.py
python build_fr_site.py
cd site
python -m http.server 8000
```

Then open:

```text
http://127.0.0.1:8000/
```

## Suggested Demo Flow

1. Open the default `Exposition IA` layer.
2. Hover over a high-exposure digital or administrative occupation.
3. Show the rationale explaining the score.
4. Switch to `Tendance 2019-2024` to show that exposure and employment growth are different concepts.
5. Switch to `Salaire` and `Diplome` to show that the tool is not only an AI ranking, but a labor-market explorer.

## LinkedIn Caption Draft

J'ai adapte l'idee du job-market visualizer US au marche du travail francais.

Chaque rectangle represente un groupe de metiers en France. Sa taille correspond au nombre de personnes en emploi, et sa couleur montre l'exposition estimee a l'IA, la tendance d'emploi, le salaire ou le niveau de diplome dominant.

Point important : exposition a l'IA ne veut pas dire disparition du metier. Cela mesure plutot a quel point le contenu du travail peut etre transforme par les outils d'IA actuels.

Les donnees viennent d'Eurostat, avec une documentation source par source, et chaque metier a une justification en francais pour son score.

## Caveats To Mention

- The project uses ISCO-08 two-digit groups, so it is an occupation-group view rather than a very granular job-title view.
- Salary is a Eurostat SES 2022 proxy at major-group level, averaged across available enterprise-size classes.
- AI scores are analytical estimates, not official forecasts.
- Missing salary values are left blank where the official source does not provide enough data.
