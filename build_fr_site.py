"""
Regenerate site/index.html from the original committed UI, localized for France.

This preserves the original treemap-first design while changing only copy,
labels, metric names, and unit handling.

Usage:
    python build_fr_site.py
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SITE_INDEX = ROOT / "site" / "index.html"


INTRO = """  <div class="intro">
    <h1>Les métiers français face à l'IA <a href="https://github.com/karpathy/jobs">Projet original</a></h1>
    <p>Cette visualisation reprend l'idée du projet original pour explorer le marché du travail français avec des données publiques européennes. Elle couvre les groupes de métiers <b>ISCO-08 à deux chiffres</b> pour la France. Chaque rectangle a une <b>surface</b> proportionnelle au nombre de personnes en emploi en 2024. La <b>couleur</b> montre la couche sélectionnée : tendance d'emploi 2019-2024, salaire brut mensuel, niveau de diplôme dominant, ou exposition à l'IA.</p>
    <p><b>Sources vérifiées :</b> l'emploi provient de l'enquête européenne sur les forces de travail publiée par <a href="https://ec.europa.eu/eurostat/databrowser/view/lfsa_egai2d/default/table?lang=en">Eurostat</a>. Les salaires proviennent de l'enquête Structure of Earnings Survey 2022 d'Eurostat et sont disponibles ici au niveau des grands groupes ISCO par taille d'entreprise ; la visualisation utilise une moyenne simple des tailles disponibles comme proxy pour les sous-groupes. Le niveau de diplôme dominant provient aussi d'Eurostat au niveau des grands groupes. La nomenclature française DARES FAP 2021 est documentée comme référence de crédibilité, mais la treemap utilise ISCO pour garder une base comparable France/Europe.</p>
    <details>
      <summary>Voir la grille d'exposition à l'IA utilisée</summary>
      <div class="prompt-box">L'exposition à l'IA mesure à quel point les tâches d'un métier peuvent être transformées par les outils d'IA actuels : automatisation, assistance, gains de productivité ou réorganisation du travail.

0-1 : exposition minimale. Travail surtout physique, terrain, manuel ou très imprévisible.
2-3 : faible. Présence humaine, gestes, soin ou intervention terrain au coeur du métier.
4-5 : modérée. Mélange de tâches physiques, relationnelles, administratives et numériques.
6-7 : élevée. Beaucoup de documents, analyse, coordination, reporting ou production de contenu.
8-9 : très élevée. Travail majoritairement numérique : code, texte, données, finance, support, recherche.
10 : maximale. Traitement d'information routinier et presque entièrement automatisable.

Chaque score est accompagné d'une justification en français qui explique les causes concrètes du score : part numérique, tâches répétables, besoin de présence physique, relation humaine, responsabilité réglementaire ou jugement terrain.</div>
    </details>
    <p><b>Attention :</b> un score élevé ne signifie pas que le métier va disparaître. Il signifie que le contenu du travail est susceptible d'être fortement transformé par l'IA. Les scores ne remplacent pas une étude économique complète et ne tiennent pas compte de toutes les contraintes de demande, réglementation, adoption ou préférences sociales.</p>
  </div>"""


def replace_block(text: str, start: str, end: str, replacement: str) -> str:
    pattern = re.escape(start) + r".*?" + re.escape(end)
    return re.sub(pattern, replacement, text, flags=re.S)


def main() -> None:
    base = subprocess.check_output(
        ["git", "show", "HEAD:site/index.html"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )

    html = base
    html = html.replace('<html lang="en">', '<html lang="fr">')
    html = html.replace("<title>US Job Market Visualizer</title>", "<title>Les métiers français face à l'IA</title>")
    html = replace_block(
        html,
        '  <div class="intro">',
        '  <div class="controls-row">',
        INTRO + "\n\n  <div class=\"controls-row\">",
    )

    html = html.replace(
        """        <button data-mode="outlook" class="active">BLS Outlook</button>
        <button data-mode="pay">Median Pay</button>
        <button data-mode="education">Education</button>
        <button data-mode="exposure">Digital AI Exposure</button>""",
        """        <button data-mode="outlook">Tendance 2019-2024</button>
        <button data-mode="pay">Salaire</button>
        <button data-mode="education">Diplôme</button>
        <button data-mode="exposure" class="active">Exposition IA</button>""",
    )
    html = html.replace("<h3>Total jobs</h3>", "<h3>Total emplois</h3>")
    html = html.replace('let colorMode = "outlook";', 'let colorMode = "exposure";')

    html = replace_block(
        html,
        "const EDU_LEVELS = [",
        "];\n\n// Color for a normalized value",
        """const EDU_LEVELS = [
  "Secondaire ou moins",
  "Secondaire / post-secondaire",
  "Supérieur",
  "Non renseigné",
];

// Color for a normalized value""",
    )

    html = re.sub(
        r"function payColor\(v, a\) \{.*?\n\}",
        """function payColor(v, a) {
  if (v == null) return `rgba(128,128,128,${a})`;
  const t = 1 - (Math.log(Math.max(1400, Math.min(8000, v))) - Math.log(1400)) / (Math.log(8000) - Math.log(1400));
  return greenRedCSS(t, a);
}""",
        html,
        flags=re.S,
    )

    html = html.replace(
        """      "No formal educational credential": "No formal",
      "High school diploma or equivalent": "HS diploma",
      "Postsecondary nondegree award": "Postsecondary",
      "Some college, no degree": "Some college",
      "Associate's degree": "Associate's",
      "Bachelor's degree": "Bachelor's",
      "Master's degree": "Master's",
      "Doctoral or professional degree": "Doctoral/Prof",""",
        """      "Secondaire ou moins": "Secondaire",
      "Secondaire / post-secondaire": "Post-sec",
      "Supérieur": "Supérieur",
      "Non renseigné": "n.d.",""",
    )

    html = html.replace(' + " jobs"', ' + " emplois"')
    html = html.replace('formatNumber(r.jobs) + " jobs"', 'formatNumber(r.jobs) + " emplois"')
    html = html.replace(
        'function formatPay(n) { return n == null ? "\\u2014" : "$" + n.toLocaleString(); }',
        'function formatPay(n) { return n == null ? "\\u2014" : Math.round(n).toLocaleString("fr-FR") + " €/mois"; }',
    )

    html = html.replace("Digital AI Exposure: ${v}/10", "Exposition IA : ${v}/10")
    html = html.replace("Outlook: ${v > 0 ? '+' : ''}${v}%", "Tendance emploi : ${v > 0 ? '+' : ''}${v}%")
    html = html.replace("Median Pay: ${formatPay(v)}", "Salaire brut mensuel : ${formatPay(v)}")
    html = html.replace("Education: ${edu || '\\u2014'}", "Diplôme dominant : ${edu || '\\u2014'}")

    html = html.replace(
        """    <span class="label">Median pay</span><span class="value">${formatPay(d.pay)}</span>
    <span class="label">Jobs (2024)</span><span class="value">${formatNumber(d.jobs)}</span>
    <span class="label">Outlook</span><span class="value">${d.outlook != null ? d.outlook + '%' : '\\u2014'} ${d.outlook_desc ? '(' + d.outlook_desc + ')' : ''}</span>
    <span class="label">Education</span><span class="value">${d.education || '\\u2014'}</span>`;""",
        """    <span class="label">Salaire brut</span><span class="value">${formatPay(d.pay)}</span>
    <span class="label">Emploi 2024</span><span class="value">${formatNumber(d.jobs)}</span>
    <span class="label">Tendance</span><span class="value">${d.outlook != null ? (d.outlook > 0 ? '+' : '') + d.outlook + '%' : '\\u2014'} ${d.outlook_desc ? '(' + d.outlook_desc + ')' : ''}</span>
    <span class="label">Diplôme</span><span class="value">${d.education || '\\u2014'}</span>`;""",
    )

    html = replace_block(
        html,
        "const PAY_BANDS = [",
        "];\n\nconst EDU_GROUPS = [",
        """const PAY_BANDS = [
  { label: "<1,8k€", min: 0, max: 1800 },
  { label: "1,8-2,5k€", min: 1800, max: 2500 },
  { label: "2,5-3,5k€", min: 2500, max: 3500 },
  { label: "3,5-5k€", min: 3500, max: 5000 },
  { label: "5k€+", min: 5000, max: Infinity },
];

const EDU_GROUPS = [""",
    )
    html = replace_block(
        html,
        "const EDU_GROUPS = [",
        "];\n\nconst OUTLOOK_TIERS = [",
        """const EDU_GROUPS = [
  { label: "Secondaire-", match: ["Secondaire ou moins"] },
  { label: "Post-sec", match: ["Secondaire / post-secondaire"] },
  { label: "Supérieur", match: ["Supérieur"] },
  { label: "n.d.", match: ["Non renseigné"] },
];

const OUTLOOK_TIERS = [""",
    )
    html = replace_block(
        html,
        "const OUTLOOK_TIERS = [",
        "];\n\n// Weighted avg",
        """const OUTLOOK_TIERS = [
  { label: "Recul (<0%)", min: -Infinity, max: -0.1 },
  { label: "Stable (0-2%)", min: 0, max: 2 },
  { label: "Hausse (2-10%)", min: 2.1, max: 10 },
  { label: "Forte hausse (10%+)", min: 10.1, max: Infinity },
];

// Weighted avg""",
    )

    replacements = {
        'Avg. outlook': 'Tendance moy.',
        'job-weighted': "pondéré par l'emploi",
        'Jobs by outlook': 'Emplois par tendance',
        'Outlook tiers': 'Niveaux tendance',
        'Outlook by pay': 'Tendance par salaire',
        'Outlook by education': 'Tendance par diplôme',
        'Declining jobs': 'Emplois en recul',
        'negative outlook': 'tendance négative',
        'Growing jobs': 'Emplois en hausse',
        'positive outlook': 'tendance positive',
        'Avg. pay': 'Salaire moyen',
        'Jobs by pay': 'Emplois par salaire',
        'Pay tiers': 'Niveaux salaire',
        'Pay by education': 'Salaire par diplôme',
        'Pay by outlook': 'Salaire par tendance',
        'Total wages': 'Masse salariale',
        'annual': 'annuelle estimée',
        "Bachelor's+": 'Supérieur',
        'of all jobs': 'des emplois',
        'Jobs by education': 'Emplois par diplôme',
        'Education tiers': 'Niveaux diplôme',
        'Avg pay by education': 'Salaire par diplôme',
        'Avg outlook by education': 'Tendance par diplôme',
        'No degree / HS': 'Secondaire ou moins',
        'jobs, no degree required': 'emplois',
        'Avg. exposure': 'Exposition moy.',
        'Jobs by exposure': 'Emplois par exposition',
        'Exposure tiers': "Niveaux d'exposition",
        'Exposure by pay': 'Exposition par salaire',
        'Exposure by education': 'Exposition par diplôme',
        'Wages exposed': 'Masse salariale exposée',
        'annual, in jobs scoring 7+': 'annuelle, score 7+',
        'Minimal (0\\u20131)': 'Minimale (0-1)',
        'Low (2\\u20133)': 'Faible (2-3)',
        'Moderate (4\\u20135)': 'Modérée (4-5)',
        'High (6\\u20137)': 'Élevée (6-7)',
        'Very high (8\\u201310)': 'Très élevée (8-10)',
        'Low': 'Faible',
        'High': 'Élevée',
        'Declining': 'Recul',
        'Growing': 'Hausse',
        'No degree': 'Secondaire-',
        'Doctoral': 'Supérieur',
    }
    for old, new in replacements.items():
        html = html.replace(old, new)

    html = html.replace('"$25K", high: "$250K"', '"1,4k€", high: "8k€"')
    html = html.replace('document.getElementById("statTotalJobs").textContent = (totalJobs / 1e6).toFixed(0) + "M";',
                        'document.getElementById("statTotalJobs").textContent = (totalJobs / 1e6).toFixed(1) + "M";')
    html = html.replace('histogram[d.exposure] += d.jobs;', 'histogram[Math.round(d.exposure)] += d.jobs;')
    html = html.replace('totalWages += d.pay * d.jobs;', 'totalWages += d.pay * 12 * d.jobs;')
    html = html.replace('wagesExposed += d.jobs * d.pay;', 'wagesExposed += d.jobs * d.pay * 12;')
    html = html.replace('$${(totalWages / 1e12).toFixed(1)}T', '€${(totalWages / 1e12).toFixed(1)}T')
    html = html.replace('$${(wagesExposed / 1e12).toFixed(1)}T', '€${(wagesExposed / 1e12).toFixed(1)}T')

    html = html.replace(
        '<div class="stat-big"><span style="color:${payColor(avg, 1)}">$${Math.round(avg / 1000)}K</span></div>',
        '<div class="stat-big"><span style="color:${payColor(avg, 1)}">${Math.round(avg).toLocaleString("fr-FR")}€</span></div>',
    )
    html = html.replace(
        'val: "$" + Math.round(g.avg / 1000) + "K",',
        'val: Math.round(g.avg).toLocaleString("fr-FR") + "€",',
    )
    html = html.replace("Math.log(Math.max(25000, g.avg)) - Math.log(25000)) / (Math.log(250000) - Math.log(25000))",
                        "Math.log(Math.max(1400, g.avg)) - Math.log(1400)) / (Math.log(8000) - Math.log(1400))")
    html = html.replace("Math.log(Math.max(25000, g.avg)) - Math.log(25000)) / (Math.log(250000) - Math.log(25000))",
                        "Math.log(Math.max(1400, g.avg)) - Math.log(1400)) / (Math.log(8000) - Math.log(1400))")
    html = html.replace("v / 150000 * 100", "(v - 1400) / (8000 - 1400) * 100")
    html = html.replace(
        """  const buckets = [
    { lo: 0, hi: 30000, mid: 25000 }, { lo: 30000, hi: 40000, mid: 35000 }, { lo: 40000, hi: 55000, mid: 47000 },
    { lo: 55000, hi: 75000, mid: 65000 }, { lo: 75000, hi: 100000, mid: 87000 }, { lo: 100000, hi: Infinity, mid: 130000 },
  ];""",
        """  const buckets = [
    { lo: 0, hi: 1800, mid: 1600 }, { lo: 1800, hi: 2500, mid: 2150 }, { lo: 2500, hi: 3500, mid: 3000 },
    { lo: 3500, hi: 5000, mid: 4250 }, { lo: 5000, hi: 6500, mid: 5750 }, { lo: 6500, hi: Infinity, mid: 7000 },
  ];""",
    )
    html = html.replace(
        '<div class="hist-labels"><span>$30K</span><span>$65K</span><span>$100K+</span></div>`;',
        '<div class="hist-labels"><span>1,8k€</span><span>3,5k€</span><span>6,5k€+</span></div>`;',
    )
    html = html.replace(
        '<div class="hist-labels"><span>HS</span><span>BS</span><span>PhD</span></div>`;',
        '<div class="hist-labels"><span>Sec.</span><span>Post-sec</span><span>Sup.</span></div>`;',
    )
    html = html.replace(
        "payColor(t.max === Infinity ? 130000 : (t.min + t.max) / 2, 1)",
        "payColor(t.max === Infinity ? 7000 : (t.min + t.max) / 2, 1)",
    )
    html = html.replace(
        'if (d.jobs && ["Bachelor\\\'s degree", "Master\\\'s degree", "Doctoral or professional degree"].includes(d.education)) bsJobs += d.jobs;',
        'if (d.jobs && d.education === "Supérieur") bsJobs += d.jobs;',
    )
    html = html.replace(
        'if (d.jobs && ["No formal educational credential", "High school diploma or equivalent"].includes(d.education)) noDeg += d.jobs;',
        'if (d.jobs && d.education === "Secondaire ou moins") noDeg += d.jobs;',
    )
    html = re.sub(
        r'if \(d\.jobs && \[[^\]]*Bachelor[^\]]*\]\.includes\(d\.education\)\) bsJobs \+= d\.jobs;',
        'if (d.jobs && d.education === "Supérieur") bsJobs += d.jobs;',
        html,
    )
    html = re.sub(
        r'if \(d\.jobs && \[[^\]]*No formal[^\]]*\]\.includes\(d\.education\)\) noDeg \+= d\.jobs;',
        'if (d.jobs && d.education === "Secondaire ou moins") noDeg += d.jobs;',
        html,
    )
    html = html.replace(
        "annuelle estimée, in jobs scoring 7+",
        "annuelle, score 7+",
    )
    html = html.replace(
        "// Impact: jobs with no formal degree",
        "// Impact: emplois avec niveau secondaire ou moins",
    )

    html = html.replace('console.log(`France IA Exposition: Loaded ${allData.length} professions`);', '')
    SITE_INDEX.write_text(html, encoding="utf-8")
    print(f"Wrote {SITE_INDEX}")


if __name__ == "__main__":
    main()
