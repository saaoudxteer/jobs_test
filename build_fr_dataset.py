"""
Build the France-first AI exposure dataset from verified public sources.

The output is intentionally shaped like the original site/data.json so the
original treemap UI can be reused with only French labels.

Primary official source:
    Eurostat EU-LFS, employed persons by ISCO-08 two digit occupation.

Supporting official sources:
    Eurostat SES 2022, mean monthly earnings by ISCO-08 major group.
    Eurostat EU-LFS, education attainment by ISCO-08 major group.
    DARES FAP 2021, French occupation taxonomy reference.

Usage:
    python build_fr_dataset.py
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
SITE_DIR = ROOT / "site"

EUROSTAT_BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
DATA_BROWSER_BASE = "https://ec.europa.eu/eurostat/databrowser/view"

EMPLOYMENT_URL = (
    f"{EUROSTAT_BASE}/lfsa_egai2d"
    "?lang=en&freq=A&unit=THS_PER&sex=T&age=Y_GE15&geo=FR"
    "&sinceTimePeriod=2019&untilTimePeriod=2024"
)
EARNINGS_URL = (
    f"{EUROSTAT_BASE}/earn_ses22_25"
    "?lang=en&freq=A&sex=T&indic_se=ERN&unit=EUR&geo=FR"
)
EDUCATION_URL = (
    f"{EUROSTAT_BASE}/lfsa_egised"
    "?lang=en&freq=A&unit=THS_PER&sex=T&age=Y_GE15&geo=FR&time=2024"
)


MAJOR_CATEGORY_FR = {
    "OC0": "Forces armées",
    "OC1": "Direction et management",
    "OC2": "Professions intellectuelles et scientifiques",
    "OC3": "Techniciens et professions intermédiaires",
    "OC4": "Employés administratifs",
    "OC5": "Services et vente",
    "OC6": "Agriculture, forêt et pêche",
    "OC7": "Artisanat, bâtiment et industrie qualifiée",
    "OC8": "Conduite d'installations et de machines",
    "OC9": "Professions élémentaires",
}

ISCO_FR = {
    "OC01": "Officiers des forces armées",
    "OC02": "Sous-officiers des forces armées",
    "OC03": "Militaires du rang",
    "OC11": "Dirigeants, hauts fonctionnaires et élus",
    "OC12": "Directeurs administratifs et commerciaux",
    "OC13": "Directeurs de production et de services spécialisés",
    "OC14": "Directeurs de l'hôtellerie, du commerce et autres services",
    "OC21": "Professionnels des sciences et de l'ingénierie",
    "OC22": "Professionnels de santé",
    "OC23": "Professionnels de l'enseignement",
    "OC24": "Professionnels de la gestion et de l'administration",
    "OC25": "Professionnels des technologies de l'information",
    "OC26": "Professionnels du droit, des sciences sociales et de la culture",
    "OC31": "Techniciens des sciences et de l'ingénierie",
    "OC32": "Professions intermédiaires de santé",
    "OC33": "Professions intermédiaires de gestion et d'administration",
    "OC34": "Professions intermédiaires du droit, du social et de la culture",
    "OC35": "Techniciens de l'information et des communications",
    "OC41": "Employés de bureau et opérateurs de saisie",
    "OC42": "Employés de relation client",
    "OC43": "Employés de comptabilité, stocks et logistique administrative",
    "OC44": "Autres employés administratifs",
    "OC51": "Services directs aux particuliers",
    "OC52": "Vendeurs",
    "OC53": "Personnel de soin et d'aide à la personne",
    "OC54": "Services de protection et sécurité",
    "OC61": "Agriculteurs et ouvriers qualifiés de l'agriculture",
    "OC62": "Ouvriers qualifiés de la forêt, de la pêche et de la chasse",
    "OC63": "Agriculteurs, pêcheurs et chasseurs de subsistance",
    "OC71": "Métiers qualifiés du bâtiment, hors électriciens",
    "OC72": "Métiers qualifiés de la métallurgie et de la mécanique",
    "OC73": "Métiers de l'artisanat et de l'impression",
    "OC74": "Métiers qualifiés de l'électricité et de l'électronique",
    "OC75": "Métiers qualifiés de l'alimentation, du bois et du textile",
    "OC81": "Conducteurs d'installations fixes et de machines",
    "OC82": "Assembleurs",
    "OC83": "Conducteurs et opérateurs mobiles",
    "OC91": "Agents de nettoyage et aides",
    "OC92": "Manoeuvres agricoles, forestiers et pêcheurs",
    "OC93": "Manoeuvres de l'industrie, du bâtiment et des transports",
    "OC94": "Aides de cuisine",
    "OC95": "Vendeurs ambulants et services de rue",
    "OC96": "Éboueurs et autres professions élémentaires",
}

AI_SCORES = {
    "OC01": (4.5, "Le travail d'officier combine analyse d'information, planification et commandement, que l'IA peut assister fortement. L'exposition reste limitée par la responsabilité opérationnelle, la chaîne de commandement et les situations physiques à haut risque."),
    "OC02": (3.8, "Les sous-officiers utilisent des informations structurées et des outils de coordination, mais leur coeur de métier reste l'encadrement terrain et l'exécution opérationnelle. L'IA peut aider à la préparation et au suivi, sans remplacer la présence et le jugement en situation."),
    "OC03": (2.8, "Les militaires du rang exercent surtout des missions physiques, opérationnelles et contextuelles. L'IA peut améliorer l'équipement, la surveillance ou la logistique, mais l'exécution reste fortement contrainte par le terrain."),
    "OC11": (6.7, "Ces fonctions reposent sur l'analyse de dossiers, la production de décisions et la coordination d'organisations. L'IA peut accélérer la veille, la synthèse et la rédaction, mais la responsabilité publique, politique ou stratégique maintient une forte intervention humaine."),
    "OC12": (7.2, "Les directions administratives et commerciales manipulent beaucoup de données, documents, reporting et arbitrages. L'IA peut automatiser l'analyse, les tableaux de bord et une partie de la communication, tout en laissant les décisions relationnelles et managériales aux humains."),
    "OC13": (5.8, "La gestion de production et de services spécialisés combine pilotage numérique, optimisation et supervision de terrain. L'IA peut améliorer la planification et la maintenance prédictive, mais les contraintes physiques, industrielles et organisationnelles limitent l'automatisation complète."),
    "OC14": (4.5, "Ces métiers de management reposent beaucoup sur la présence client, la coordination locale et les imprévus de service. L'IA peut aider à prévoir la demande, gérer les plannings et analyser les ventes, mais le coeur opérationnel reste humain."),
    "OC21": (7.3, "Les sciences et l'ingénierie produisent des modèles, calculs, plans, simulations et documents techniques. L'IA peut fortement augmenter la productivité, mais la validation, la responsabilité technique et les contraintes physiques gardent un rôle humain important."),
    "OC22": (4.4, "Les professionnels de santé utilisent des données et de la documentation médicale que l'IA peut assister. L'exposition est freinée par l'examen physique, la relation de soin, la responsabilité clinique et la réglementation."),
    "OC23": (6.2, "L'enseignement comporte de la préparation de cours, de l'évaluation et de l'accompagnement que l'IA peut transformer. La présence pédagogique, la gestion de classe et la relation avec les apprenants limitent toutefois la substitution directe."),
    "OC24": (8.0, "La gestion, la finance, les RH et l'administration sont très documentaires et orientées données. L'IA peut automatiser une partie de l'analyse, de la rédaction, du contrôle et du reporting, avec une exposition élevée malgré le besoin de jugement."),
    "OC25": (9.0, "Les professionnels de l'informatique travaillent presque entièrement sur des artefacts numériques. Génération de code, tests, documentation, support et analyse de systèmes sont déjà fortement augmentés par l'IA, ce qui expose fortement l'organisation du travail."),
    "OC26": (7.7, "Le droit, les sciences sociales et la culture produisent beaucoup de recherche, synthèse, rédaction et contenu numérique. L'IA peut automatiser ou accélérer ces tâches, mais l'interprétation, la responsabilité, la créativité et la relation humaine restent déterminantes."),
    "OC31": (5.8, "Ces techniciens combinent mesures, plans, diagnostics et interventions matérielles. L'IA peut aider à l'analyse, à la documentation et au diagnostic, mais l'exécution dépend souvent du terrain, des équipements et de contrôles humains."),
    "OC32": (3.8, "Les professions intermédiaires de santé sont fortement liées au soin, aux gestes, à la présence et au suivi humain. L'IA peut assister la documentation et certains diagnostics, mais l'automatisation directe du coeur du métier reste limitée."),
    "OC33": (7.2, "Ces fonctions traitent des dossiers, chiffres, procédures, clients internes et outils numériques. L'IA peut automatiser la saisie, le contrôle, la recherche d'information et une partie de la communication, ce qui crée une exposition élevée."),
    "OC34": (6.2, "Le travail social, juridique et culturel intermédiaire mélange dossiers, accompagnement et interaction humaine. L'IA peut aider la rédaction et la recherche d'information, mais le contexte social, l'écoute et l'arbitrage limitent l'automatisation."),
    "OC35": (7.6, "Les techniciens informatiques travaillent sur des systèmes numériques, incidents, configurations et documentation. L'IA peut accélérer le support, le diagnostic et l'automatisation de scripts, même si les infrastructures et interventions restent supervisées."),
    "OC41": (8.8, "La saisie, le secrétariat et les tâches de bureau structurées sont fortement numériques et répétables. L'IA peut produire des courriers, résumer, classer, saisir et contrôler des informations, ce qui rend l'exposition très élevée."),
    "OC42": (7.5, "La relation client standardisée est déjà transformée par les agents conversationnels et l'automatisation des demandes simples. Les cas sensibles, la négociation et l'empathie gardent de la valeur humaine, mais le volume de tâches automatisables est important."),
    "OC43": (8.0, "La comptabilité de base, les stocks et l'enregistrement administratif reposent sur des données structurées. L'IA et l'automatisation peuvent traiter, rapprocher, détecter les anomalies et générer des documents, avec une forte exposition."),
    "OC44": (7.2, "Ces emplois administratifs manipulent des dossiers, formulaires, archives et flux d'information. L'IA peut trier, extraire, résumer et préparer les documents, mais les exceptions et le contact organisationnel nécessitent encore des humains."),
    "OC51": (3.5, "Les services directs aux particuliers dépendent fortement de la présence physique, de l'adaptation immédiate et de la relation. L'IA peut aider à organiser l'activité ou recommander des actions, mais elle touche moins le coeur du travail."),
    "OC52": (5.6, "La vente combine relation client, conseil, encaissement et outils numériques. L'IA peut automatiser la recommandation, le marketing et le support, mais la présence en magasin et la persuasion humaine réduisent l'exposition directe."),
    "OC53": (2.8, "Le soin et l'aide à la personne exigent présence, gestes, confiance et adaptation fine aux situations humaines. L'IA peut assister le suivi ou la coordination, mais elle ne remplace pas facilement le coeur relationnel et physique."),
    "OC54": (3.4, "La sécurité et la protection reposent sur la présence, l'intervention et le jugement en situation réelle. L'IA peut améliorer la surveillance, l'analyse d'images ou la coordination, mais l'action terrain reste humaine."),
    "OC61": (2.2, "L'agriculture qualifiée reste très matérielle, saisonnière et dépendante d'environnements variables. L'IA peut optimiser les décisions et piloter certains équipements, mais l'exécution physique limite l'exposition directe."),
    "OC62": (1.8, "La forêt, la pêche et la chasse qualifiées se déroulent dans des environnements physiques difficiles et peu standardisés. L'IA peut aider à la cartographie ou à la prévision, mais le coeur du travail reste manuel et terrain."),
    "OC63": (1.5, "Les activités de subsistance sont principalement physiques, locales et peu numérisées. L'IA peut avoir un effet périphérique via l'information ou la météo, mais l'exposition directe est minimale."),
    "OC71": (2.4, "Les métiers du bâtiment nécessitent gestes techniques, déplacement, adaptation au chantier et manipulation de matériaux. L'IA peut aider aux plans et au diagnostic, mais le travail physique limite fortement la substitution."),
    "OC72": (3.2, "La métallurgie et la mécanique combinent savoir-faire manuel, machines et contrôle qualité. L'IA peut soutenir le diagnostic, la programmation ou la maintenance, mais l'intervention physique reste centrale."),
    "OC73": (4.6, "L'artisanat et l'impression mélangent production matérielle et parfois conception numérique. L'IA peut transformer la création, la prépresse et certains flux, mais le geste, la finition et les machines limitent l'automatisation totale."),
    "OC74": (3.5, "L'électricité et l'électronique exigent installation, contrôle, réparation et sécurité sur site. L'IA peut assister le diagnostic et la documentation, mais les gestes techniques et la responsabilité terrain restent importants."),
    "OC75": (2.6, "L'alimentation, le bois et le textile qualifiés restent fortement liés aux matériaux, outils et gestes. L'IA peut aider à la conception, au contrôle ou à la planification, mais le coeur de production est peu numérisable."),
    "OC81": (5.0, "Les conducteurs d'installations travaillent avec des machines et des données de supervision. L'IA peut optimiser les réglages, détecter des anomalies et automatiser des séquences, mais la sécurité et la surveillance humaine restent nécessaires."),
    "OC82": (4.2, "L'assemblage contient des tâches répétitives exposées à l'automatisation industrielle. L'IA peut renforcer la robotique et le contrôle qualité, mais les postes variables ou manuels restent moins exposés."),
    "OC83": (4.0, "La conduite et les opérations mobiles sont touchées par l'aide à la navigation, l'optimisation et l'autonomie progressive. Les contraintes réglementaires, la sécurité, la route et la manutention limitent encore la substitution directe."),
    "OC91": (2.0, "Le nettoyage et les aides reposent sur des gestes physiques dans des lieux variés. L'IA peut optimiser les tournées ou guider des robots spécialisés, mais le travail quotidien reste peu numérisable."),
    "OC92": (1.8, "Les manoeuvres agricoles et forestiers réalisent surtout des tâches physiques saisonnières et en extérieur. L'IA peut orienter les décisions, mais son effet sur le coeur manuel reste faible."),
    "OC93": (2.5, "Ces manoeuvres exécutent des tâches physiques dans l'industrie, le bâtiment et les transports. L'automatisation peut toucher certains postes répétitifs, mais la variabilité des environnements maintient une exposition limitée."),
    "OC94": (2.6, "Les aides de cuisine travaillent dans un environnement physique, rythmé et contraint par l'organisation du service. L'IA peut aider les achats ou les plannings, mais les gestes de préparation et de nettoyage restent humains."),
    "OC95": (3.8, "La vente et les services de rue reposent sur l'interaction directe et la présence physique. L'IA peut influencer les paiements, la recommandation ou la traduction, mais l'exposition reste modérée."),
    "OC96": (2.3, "Les éboueurs et autres professions élémentaires travaillent surtout sur des tâches physiques et locales. L'IA peut optimiser les tournées ou la maintenance, mais elle transforme surtout les outils plutôt que le coeur du métier."),
}


def fetch_json(url: str, cache_path: Path) -> dict:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=45) as response:
            payload = response.read().decode("utf-8")
        cache_path.write_text(payload, encoding="utf-8")
        return json.loads(payload)
    except Exception:
        if cache_path.exists():
            return json.loads(cache_path.read_text(encoding="utf-8"))
        raise


def jsonstat_records(payload: dict) -> list[dict]:
    ids = payload["id"]
    sizes = payload["size"]
    labels_by_dim = {}
    code_by_position = {}
    for dim in ids:
        category = payload["dimension"][dim]["category"]
        index = category["index"]
        labels_by_dim[dim] = category.get("label", {})
        reverse = {}
        for code, pos in index.items():
            reverse[pos] = code
        code_by_position[dim] = reverse

    values = payload.get("value", {})
    if isinstance(values, list):
        value_items = ((str(i), v) for i, v in enumerate(values) if v is not None)
    else:
        value_items = values.items()

    records = []
    for flat_key, value in value_items:
        flat = int(flat_key)
        positions = []
        rem = flat
        for size in reversed(sizes):
            positions.append(rem % size)
            rem //= size
        positions.reverse()

        row = {"value": value}
        for dim, pos in zip(ids, positions):
            code = code_by_position[dim][pos]
            row[dim] = code
            row[f"{dim}_label"] = labels_by_dim[dim].get(code, code)
        records.append(row)
    return records


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def major_code(isco: str) -> str:
    return isco[:3]


def education_label(education_counts: dict[str, float]) -> str:
    labels = {
        "ED0-2": "Secondaire ou moins",
        "ED3_4": "Secondaire / post-secondaire",
        "ED5-8": "Supérieur",
    }
    if not education_counts:
        return "Non renseigné"
    best = max(education_counts.items(), key=lambda item: item[1])[0]
    return labels.get(best, "Non renseigné")


def outlook_desc(change_pct: float | None) -> str:
    if change_pct is None:
        return "non disponible"
    if change_pct <= -10:
        return "fort recul 2019-2024"
    if change_pct < -2:
        return "recul 2019-2024"
    if change_pct <= 2:
        return "stable 2019-2024"
    if change_pct < 10:
        return "hausse 2019-2024"
    return "forte hausse 2019-2024"


def source_manifest(raw_payloads: dict[str, dict]) -> list[dict]:
    today = date.today().isoformat()
    return [
        {
            "id": "eurostat_lfsa_egai2d",
            "name": "Employed persons by detailed occupation (ISCO-08 two digit level)",
            "publisher": "Eurostat",
            "url": f"{DATA_BROWSER_BASE}/lfsa_egai2d/default/table?lang=en",
            "api_url": EMPLOYMENT_URL,
            "retrieved_date": today,
            "last_update": raw_payloads["employment"].get("updated"),
            "license": "Eurostat reuse policy / European Commission data reuse",
            "fields_used": ["employment by ISCO-08 occupation, France, 2019-2024"],
        },
        {
            "id": "eurostat_earn_ses22_25",
            "name": "Mean monthly earnings by sex, occupation and size class of the enterprise (2022)",
            "publisher": "Eurostat",
            "url": f"{DATA_BROWSER_BASE}/earn_ses22_25/default/table?lang=en",
            "api_url": EARNINGS_URL,
            "retrieved_date": today,
            "last_update": raw_payloads["earnings"].get("updated"),
            "license": "Eurostat reuse policy / European Commission data reuse",
            "fields_used": ["gross monthly earnings by ISCO-08 major group, France, 2022"],
            "note": "SES salary data is available at ISCO major-group level by enterprise size class, without a total size-class category in this API response. The build uses a simple average across available size classes, then two-digit occupations inherit their major-group salary proxy.",
        },
        {
            "id": "eurostat_lfsa_egised",
            "name": "Employed persons by occupation and educational attainment level",
            "publisher": "Eurostat",
            "url": f"{DATA_BROWSER_BASE}/lfsa_egised/default/table?lang=en",
            "api_url": EDUCATION_URL,
            "retrieved_date": today,
            "last_update": raw_payloads["education"].get("updated"),
            "license": "Eurostat reuse policy / European Commission data reuse",
            "fields_used": ["dominant education attainment by ISCO-08 major group, France, 2024"],
            "note": "Education is available at ISCO major-group level here; two-digit occupations inherit their major-group education proxy.",
        },
        {
            "id": "dares_fap_2021",
            "name": "La nomenclature des familles professionnelles 2021",
            "publisher": "DARES - service statistique du ministère en charge du Travail",
            "url": "https://www.data.gouv.fr/datasets/la-nomenclature-des-familles-professionnelles-2021",
            "retrieved_date": today,
            "last_update": "2024-04-30",
            "license": "See data.gouv.fr dataset page",
            "fields_used": ["French occupational taxonomy reference only in this build"],
            "note": "Local data/fap_2021.csv is readable and used as a credibility reference; the final site uses Eurostat ISCO groups for comparable employment data.",
        },
        {
            "id": "project_ai_rubric",
            "name": "Project analytical AI exposure rubric",
            "publisher": "This repository",
            "retrieved_date": today,
            "fields_used": ["AI exposure score and French rationale"],
            "note": "AI exposure scores are analytical estimates, not official statistics and not disappearance predictions.",
        },
    ]


def write_source_checks(manifest: list[dict], occupations_count: int) -> None:
    lines = [
        "# Source Checks",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Final Source Decision",
        "",
        f"- Final occupation backbone: Eurostat ISCO-08 two-digit occupations for France ({occupations_count} occupations with 2024 employment data).",
        "- This is less granular than the desired DARES 225-metier product, but it is fully accessible, official, Europe-compatible, and reproducible.",
        "- DARES FAP 2021 remains documented as the French taxonomy reference.",
        "",
        "## Verified Sources",
        "",
    ]
    for source in manifest:
        lines.extend(
            [
                f"### {source['id']}",
                "",
                f"- Publisher: {source.get('publisher', 'n/a')}",
                f"- URL: {source.get('url', 'n/a')}",
                f"- Retrieved: {source.get('retrieved_date', 'n/a')}",
                f"- Last update: {source.get('last_update', 'n/a')}",
                f"- Fields used: {', '.join(source.get('fields_used', []))}",
                f"- Note: {source.get('note', 'None')}",
                "",
            ]
        )

    lines.extend(
        [
            "## Known Limitations",
            "",
            "- Salary is an official Eurostat SES 2022 proxy, not a direct salary observation for every two-digit occupation.",
            "- Eurostat SES values are not available in this pull for armed forces, agriculture, and plant/machine operator major groups; the site leaves those salary cells blank instead of imputing unverifiable values.",
            "- AI exposure scores are project estimates with written rationales, not official labor-market forecasts.",
            "",
            "## Rejected Local Files",
            "",
            "- `data/metiers_2030.xlsx`: not used; local file starts with HTML/anti-bot security content, not an Excel workbook.",
            "- `data/insee_salaries_2023.xlsx`: not used; local file starts with HTML, not an Excel workbook.",
            "- `data/rome_fiches.json`: not used; local file is a 404 HTML page, not JSON.",
            "- `scores.json`: not used for the French build; it contains the original US occupation scores.",
            "- `synthetic_scores.json`: not used; it is test data only.",
            "",
        ]
    )
    (DATA_DIR / "source_checks.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    SITE_DIR.mkdir(exist_ok=True)

    employment_payload = fetch_json(EMPLOYMENT_URL, RAW_DIR / "eurostat_lfsa_egai2d_fr_2019_2024.json")
    earnings_payload = fetch_json(EARNINGS_URL, RAW_DIR / "eurostat_earn_ses22_25_fr.json")
    education_payload = fetch_json(EDUCATION_URL, RAW_DIR / "eurostat_lfsa_egised_fr_2024.json")

    raw_payloads = {
        "employment": employment_payload,
        "earnings": earnings_payload,
        "education": education_payload,
    }

    employment_by_code: dict[str, dict[str, float]] = {}
    english_labels: dict[str, str] = {}
    for row in jsonstat_records(employment_payload):
        code = row["isco08"]
        if not re.fullmatch(r"OC\d{2}", code):
            continue
        employment_by_code.setdefault(code, {})[row["time"]] = float(row["value"])
        english_labels[code] = row.get("isco08_label", code)

    earnings_values_by_major: dict[str, list[float]] = {}
    for row in jsonstat_records(earnings_payload):
        code = row["isco08"]
        if re.fullmatch(r"OC\d", code) and row.get("unit") == "EUR" and row.get("indic_se") == "ERN":
            earnings_values_by_major.setdefault(code, []).append(float(row["value"]))
    earnings_by_major = {
        code: sum(values) / len(values)
        for code, values in earnings_values_by_major.items()
        if values
    }

    education_counts_by_major: dict[str, dict[str, float]] = {}
    for row in jsonstat_records(education_payload):
        code = row["isco08"]
        isced = row["isced11"]
        if re.fullmatch(r"OC\d", code) and isced in {"ED0-2", "ED3_4", "ED5-8"}:
            education_counts_by_major.setdefault(code, {})[isced] = float(row["value"])

    occupations = []
    for code in sorted(employment_by_code.keys()):
        emp_2024_ths = employment_by_code[code].get("2024")
        if emp_2024_ths is None or emp_2024_ths <= 0:
            continue

        emp_2019_ths = employment_by_code[code].get("2019")
        change = None
        if emp_2019_ths and emp_2019_ths > 0:
            change = (emp_2024_ths - emp_2019_ths) / emp_2019_ths * 100

        major = major_code(code)
        title = ISCO_FR.get(code, english_labels.get(code, code))
        score, rationale = AI_SCORES[code]
        occupation = {
            "title": title,
            "slug": slugify(title),
            "isco08": code,
            "category": MAJOR_CATEGORY_FR.get(major, "Autre"),
            "jobs": int(round(emp_2024_ths * 1000)),
            "pay": round(earnings_by_major[major]) if major in earnings_by_major else None,
            "outlook": round(change, 1) if change is not None else None,
            "outlook_desc": outlook_desc(change),
            "education": education_label(education_counts_by_major.get(major, {})),
            "exposure": score,
            "exposure_rationale": rationale,
            "url": f"{DATA_BROWSER_BASE}/lfsa_egai2d/default/table?lang=en",
            "source_refs": [
                "eurostat_lfsa_egai2d",
                "eurostat_earn_ses22_25",
                "eurostat_lfsa_egised",
                "project_ai_rubric",
            ],
        }
        occupations.append(occupation)

    occupations.sort(key=lambda row: row["jobs"], reverse=True)

    manifest = source_manifest(raw_payloads)
    (DATA_DIR / "source_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_source_checks(manifest, len(occupations))

    with (ROOT / "occupations.csv").open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "title",
            "slug",
            "isco08",
            "category",
            "jobs",
            "pay",
            "outlook",
            "outlook_desc",
            "education",
            "exposure",
            "exposure_rationale",
            "url",
            "source_refs",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in occupations:
            csv_row = dict(row)
            csv_row["source_refs"] = "|".join(row["source_refs"])
            writer.writerow(csv_row)

    (ROOT / "occupations.json").write_text(
        json.dumps(occupations, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (ROOT / "scores_fr.json").write_text(
        json.dumps(
            [
                {
                    "slug": row["slug"],
                    "title": row["title"],
                    "isco08": row["isco08"],
                    "exposure": row["exposure"],
                    "rationale": row["exposure_rationale"],
                }
                for row in occupations
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (SITE_DIR / "data.json").write_text(
        json.dumps(occupations, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    total_jobs = sum(row["jobs"] for row in occupations)
    scored = sum(1 for row in occupations if row["exposure"] is not None)
    print(f"Wrote {len(occupations)} France occupations to site/data.json")
    print(f"Total 2024 employment represented: {total_jobs:,}")
    print(f"AI exposure rationales: {scored}/{len(occupations)}")


if __name__ == "__main__":
    main()
