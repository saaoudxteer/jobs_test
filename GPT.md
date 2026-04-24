# GPT.md - France / Europe Job Market AI Exposure Project Plan

## Goal

Rebuild the original US job-market visualizer idea for the French labor market, with optional Europe-level context, so it is credible enough to publish on LinkedIn.

The final product should feel like the original project:

- Treemap-based visual exploration of occupations.
- Rectangle area represents labor-market size.
- Color represents a selected metric, with AI exposure as the default layer.
- Each occupation has a clear rationale explaining why it received its AI exposure score.
- Every numeric field should be traceable to an official or clearly documented source.

## Current Implementation Snapshot

- The implemented version is France-first and uses Eurostat ISCO-08 two-digit occupation groups for reproducible official data.
- `build_fr_dataset.py` writes `occupations.csv`, `occupations.json`, `scores_fr.json`, `data/source_manifest.json`, `data/source_checks.md`, and `site/data.json`.
- `build_fr_site.py` regenerates `site/index.html` from `git show HEAD:site/index.html`, preserving the original treemap UI while translating labels and metric units.
- The current generated dataset has 41 occupations, 28,520,500 represented employed people for France in 2024, and 41/41 AI rationales.
- Salary uses Eurostat SES 2022 gross monthly earnings by major ISCO group and averages available enterprise-size classes. Missing official salary values are left blank for armed forces, agriculture, and plant/machine operator groups.
- The final page should be served from `site/` because `site/index.html` loads `data.json` with `fetch()`.

## Non-Negotiable Constraints

1. Preserve the original website UI design and interaction model as much as possible.
   - Do not redesign the visual language.
   - Do not introduce a new landing page, new card-heavy layout, or a new visual system.
   - Keep the original treemap-first experience.
   - Only adapt labels, data fields, tooltips, legends, and source text where needed for the French dataset.

2. Data credibility is more important than dataset size.
   - Prefer fewer occupations with solid official data over many occupations with weak or fabricated fields.
   - Do not rely on broken local downloads, anti-bot HTML pages saved as `.xlsx`, placeholder data, or synthetic scores in final output.
   - Keep a source manifest with URL, publisher, retrieval date, license/access note, and fields used.

3. Every job must include an explanation.
   - For AI exposure, store both a numeric score and a French rationale.
   - The rationale must explain the cause: digital work, automatable text/data tasks, physical constraints, human interaction, regulated judgment, on-site work, etc.
   - The site tooltip should show the score and the explanation.

4. Keep the distinction clear.
   - "AI exposure" does not mean "job disappearance".
   - It means the occupation is likely to be transformed by current AI tools through automation, augmentation, productivity gains, or task redesign.

## Recommended Scope

Primary scope: France-first.

Use French official sources for the main treemap. Add a small Europe context layer only where the data is comparable and reliable.

Reason:

- France has detailed occupation-specific sources through DARES, France Travail, FAP, ROME, and France Strategie.
- Europe-wide public data is useful for context, but usually coarser at occupation level through ISCO aggregates.
- A France-first version will be more accurate, more explainable, and stronger for a French LinkedIn audience.

## Candidate Official Sources

### DARES - Portraits statistiques des metiers

Use for:

- Occupation list if downloadable structured data can be obtained.
- Employment counts.
- Salary indicators.
- Diploma/education indicators.
- Employment evolution and labor-market characteristics.

Why:

- It is the closest French equivalent to the BLS Occupational Outlook Handbook concept.
- It covers 225 French occupations and provides labor-market indicators.

Risk:

- The DARES page may be protected by anti-bot checks.
- If direct data export is blocked, use another official DARES/France Strategie source with documented fields.

### DARES - FAP 2021 nomenclature

Use for:

- Occupation taxonomy.
- Mapping between FAP, PCS, and ROME where available.
- Sector/domain grouping.

Why:

- FAP is designed to analyze labor-market data by profession.
- It bridges PCS and ROME, making it useful for joining statistics and job descriptions.

Local note:

- `data/fap_2021.csv` is readable and appears valid.

### France Travail - ROME 4.0

Use for:

- Job descriptions.
- Skills.
- Certifications/diplomas.
- Work contexts.
- Inputs to the AI exposure scoring prompt.

Why:

- ROME is the official operational job/skills reference in France.
- It provides richer descriptions than a simple occupation title.

Risk:

- API access may require registration/habilitation.
- The local `data/rome_fiches.json` is currently not valid data; it is a 404 HTML page and must not be used.

### France Strategie / DARES - Les metiers en 2030

Use for:

- 2030 outlook layer.
- Job creation/destruction projections.
- Recruitment needs.
- Potential labor shortages.

Why:

- This gives the project the same "outlook" dimension as the US original.

Risk:

- Local `data/metiers_2030.xlsx` is not a real Excel workbook; it is an anti-bot/security HTML page.
- Need a clean official download or an alternative structured source.

### France Travail - API Marche du travail

Use for:

- Job offers.
- Demand/supply tension.
- Recruitment difficulty.
- Proposed salary where available.
- Territory-level indicators if a later version adds regional filtering.

Why:

- Updated quarterly and relevant to current labor-market conditions.

Risk:

- May require API access setup.

### Eurostat EU-LFS / SES

Use for optional context only:

- Compare France against EU averages at broad ISCO occupation levels.
- Provide a small "Europe context" panel or toggle, not the main treemap.

Why:

- Eurostat is comparable across countries.

Risk:

- Occupation granularity is coarser than French FAP/ROME data.
- Not suitable as the primary data backbone for a French LinkedIn-ready visualization.

## Current Repo State

This repository started as a US BLS Occupational Outlook Handbook visualizer.

Current local French attempt:

- `agent1.py` through `agent5.py` are experimental scripts.
- `occupations.csv` and `occupations.json` have been changed to French FAP-like occupations.
- `site/data.json` currently has 341 French occupations but almost no usable scores, employment, or salary values.
- `scores.json` still contains the original US scores, so it does not match the French occupations.
- `synthetic_scores.json` is only test data and must not be used in final output.
- `site/index.html` has already been changed from the original; before final implementation, compare against the original committed UI and preserve the official/original design.

Broken local data that must not be trusted:

- `data/metiers_2030.xlsx`: appears to be anti-bot/security HTML, not an Excel workbook.
- `data/insee_salaries_2023.xlsx`: appears to be HTML, not an Excel workbook.
- `data/rome_fiches.json`: appears to be a 404 HTML page, not JSON.

Valid-looking local data:

- `data/fap_2021.csv`: readable semicolon-delimited FAP 2021 taxonomy.

## Data Model Target

Final `site/data.json` should use a stable structure like:

```json
{
  "metadata": {
    "title": "Les metiers francais face a l'IA",
    "generated_date": "YYYY-MM-DD",
    "country": "France",
    "occupation_count": 225,
    "source_manifest": []
  },
  "occupations": [
    {
      "title": "Comptables",
      "slug": "comptables",
      "category": "Gestion, administration des entreprises",
      "employment": 123000,
      "median_salary": 2400,
      "education": "Bac+2 / Bac+3",
      "outlook_2030": 0.08,
      "recruitment_tension": "Elevee",
      "ai_score": 8.2,
      "ai_rationale": "Explication en francais...",
      "source_refs": ["dares_portraits", "rome_4"]
    }
  ]
}
```

Adjust field names only if required by the original frontend, but avoid mixing old US fields with new French semantics.

## AI Exposure Scoring Rubric

Use a French-language scoring prompt, but keep the rubric auditable:

- 0-1: Minimal exposure. Mostly physical, on-site, manual, highly variable environments.
- 2-3: Low exposure. Strong physical presence or human care component; AI mostly assists.
- 4-5: Moderate exposure. Mixed cognitive, relational, administrative, and physical work.
- 6-7: High exposure. Many structured digital tasks: documents, coordination, analysis, reporting.
- 8-9: Very high exposure. Mostly information work: writing, coding, analysis, legal/financial/admin processing.
- 10: Maximum exposure. Fully digital, highly structured, directly automatable tasks.

Rationale requirements:

- 2 to 4 French sentences.
- Mention the concrete causes of the score.
- Avoid claiming that the job will disappear.
- Mention blockers to automation where relevant: physical presence, regulation, responsibility, trust, social interaction, real-time judgment.

## Implementation Phases

### Phase 1 - Source Verification

Deliverables:

- `data/source_manifest.json`
- `data/source_checks.md`

Tasks:

- Verify each official source URL.
- Record publisher, update date, license/access status, and fields used.
- Replace broken local files with clean downloads only after confirmation/access is available.
- Document any blocked source and chosen fallback.

Acceptance criteria:

- No final data field depends on a broken local file.
- Every source used in the site is listed in the manifest.

### Phase 2 - Occupation Backbone

Deliverables:

- `data/occupations_fr_raw.*`
- `data/occupations_fr_normalized.json`

Tasks:

- Choose the final occupation level: ideally 225 DARES portrait occupations, otherwise FAP 86/228 depending on data quality.
- Normalize titles, slugs, categories, and codes.
- Keep original source identifiers for traceability.

Acceptance criteria:

- Each occupation has title, slug, category, source code, and source reference.

### Phase 3 - Labor-Market Metrics

Deliverables:

- `occupations_fr.csv`
- enriched `occupations_fr_normalized.json`

Tasks:

- Add employment counts.
- Add salary if available and credible.
- Add education/diploma indicator if available.
- Add 2030 outlook/recruitment needs if available.
- Add recruitment tension if available.

Acceptance criteria:

- Missing values are explicit nulls, not zero unless zero is real.
- Tooltip/site labels do not pretend unavailable values are known.

### Phase 4 - Description Pages

Deliverables:

- `pages_fr/{slug}.md`

Tasks:

- Build job descriptions from ROME/FAP/DARES fields.
- Include skills, tasks, work context, education, and source references.

Acceptance criteria:

- Every occupation to be scored has enough text context for scoring.

### Phase 5 - AI Scoring

Deliverables:

- `scores_fr.json`
- `scores_fr_audit.csv`

Tasks:

- Score each occupation with the rubric.
- Store score, rationale, model/provider, prompt version, and timestamp.
- Include an audit table for review.

Acceptance criteria:

- Every occupation shown in the final site has `ai_score` and `ai_rationale`.
- Scores are not copied from the US dataset unless there is a documented crosswalk and manual review.

### Phase 6 - Site Data Build

Deliverables:

- `site/data.json`

Tasks:

- Merge occupations, labor metrics, source refs, and AI scores.
- Keep the JSON compact but traceable.
- Include metadata and source summaries.

Acceptance criteria:

- The frontend can load `site/data.json` without special build steps.
- Dataset counts match the source manifest.

### Phase 7 - Frontend Adaptation

Deliverables:

- `site/index.html`

Tasks:

- Preserve the original UI design and treemap interaction.
- Adapt labels to French.
- Add tooltip fields for French metrics.
- Add source/caveat copy without changing the overall layout.
- Keep AI exposure as default color mode.

Acceptance criteria:

- Visual design remains recognizably the original project.
- No new unrelated UI framework.
- Search, tooltip, color modes, and responsive layout work.

### Phase 8 - QA and LinkedIn Readiness

Deliverables:

- `README.md` update or `METHODOLOGY.md`
- screenshots for sharing

Tasks:

- Run local static server and inspect the page.
- Check console errors.
- Check random sample of occupations against source data.
- Add methodology/caveats for LinkedIn audience.

Acceptance criteria:

- The page is credible, visually clean, source-backed, and explains what AI exposure means.

## Agent Handoff Rules

If multiple agents work on this project:

- Read this file first.
- Do not overwrite another agent's changes.
- Do not redesign the UI.
- Do not use synthetic scores or broken local data.
- Keep all source decisions documented.
- Prefer small, reviewable commits or file changes.
- When editing, state which phase and deliverable you are working on.

Suggested parallel work split:

- Agent A: source verification and downloads.
- Agent B: occupation normalization and data model.
- Agent C: scoring prompt and score audit format.
- Agent D: frontend preservation/adaptation.

## Open Decisions Before Implementation

1. Final occupation granularity:
   - Preferred: DARES 225 occupations if structured data is available.
   - Fallback: FAP 86 or FAP 228 if 225-level source extraction is blocked.

2. Source access:
   - Confirm whether France Travail API access credentials are available or need to be requested.

3. Scoring provider:
   - Confirm whether to use OpenAI, Anthropic, or another provider for French AI exposure scores.

4. Europe layer:
   - Recommended: optional context only.
   - Do not delay France-first launch for Europe-wide data.

## Immediate Next Step

After user confirmation, start Phase 1:

1. Build `data/source_manifest.json`.
2. Verify/download official French sources.
3. Decide final occupation granularity based on actual available structured data.
4. Report back before generating final scores if source access is blocked or the occupation backbone changes.
