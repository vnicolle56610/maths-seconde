#!/usr/bin/env python3
"""Rubrique « Nouveautés » de la page d'accueil (identique sur les trois sites).

Régénère, dans docs/index.md, la zone comprise entre
<!-- AUTO-NEWS:START --> et <!-- AUTO-NEWS:END --> :

  - « 🆕 Nouveautés » : les documents mis en ligne pour la première fois ces
    JOURS_FENETRE derniers jours (au plus MAX_LIGNES lignes), regroupés par
    date et par type, avec lien vers la page de la notion ;
  - « 🔁 Réviser avec un parcours guidé » : mode d'emploi, affiché seulement
    si le site publie au moins un parcours guidé.

La date de mise en ligne d'un fichier est celle du commit Git qui l'a ajouté
dans docs/ ; un fichier ajouté mais pas encore commité compte pour aujourd'hui.
Seuls les AJOUTS comptent : un document republié (correction d'une coquille)
n'est pas annoncé. Un document retiré du site disparaît des nouveautés.

Usage : python3 scripts/generer_nouveautes.py [--date AAAA-MM-JJ] [--dry-run]
Appelé par scripts/lancer_publication.sh après les autres générateurs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOCS = RACINE / "docs"
INDEX = DOCS / "index.md"

ZONE_START = "<!-- AUTO-NEWS:START -->"
ZONE_END = "<!-- AUTO-NEWS:END -->"

JOURS_FENETRE = 21
MAX_LIGNES = 4

NBSP = " "

# Ordre d'affichage à date égale, puis libellés (singulier, pluriel).
TYPES = {
    "devoir_blanc": ("Devoir blanc", "Devoirs blancs"),
    "corrige_devoir_blanc": ("Corrigé du devoir blanc", "Corrigés des devoirs blancs"),
    "apres_evaluation": ("Après l'évaluation", "Après l'évaluation"),
    "parcours": ("Parcours guidé", "Parcours guidés"),
    "corrige_parcours": ("Corrigés du parcours guidé", "Corrigés des parcours guidés"),
    "cours": ("Cours", "Cours"),
    "td": ("TD", "TD"),
    "corrige_td": ("Corrigé du TD", "Corrigés des TD"),
    "automatismes": ("Automatismes", "Automatismes"),
}
ORDRE = list(TYPES)

RE_NOTION = re.compile(r"(?<![A-Z0-9])N(\d{2})(?![0-9])")


def classer(chemin: str) -> tuple[str, str] | None:
    """(type, clé) d'un fichier de docs/, ou None s'il n'est pas à annoncer.

    clé = « Nxx » pour les ressources de notion, identifiant de l'évaluation
    pour les devoirs blancs.
    """
    p = Path(chemin)
    nom = p.name
    parties = p.parts
    if not parties:
        return None
    if parties[0] == "preparer-evaluation":
        if nom.lower().endswith(".pdf") and any(x.startswith("apres-") for x in parties):
            dossier = next(x for x in parties if x.startswith("apres-"))
            return "apres_evaluation", dossier[len("apres-"):].upper()
        m = re.match(r"^(CORRIGE_)?DEVOIR_BLANC_([A-Z0-9]+)", nom)
        if m and nom.endswith(".pdf"):
            return ("corrige_devoir_blanc" if m.group(1) else "devoir_blanc"), m.group(2)
        return None
    m = RE_NOTION.search(nom)
    if not m:
        return None
    notion = "N" + m.group(1)
    if parties[0] == "parcours-guide" and nom.endswith(".pdf"):
        return ("corrige_parcours" if "_CORRIGE" in nom else "parcours"), notion
    if parties[0] == "cours" and nom.startswith("COURS_") and nom.endswith(".pdf"):
        return "cours", notion
    if parties[0] == "td" and nom.startswith("TD_") and nom.endswith(".pdf"):
        return "td", notion
    if parties[0] == "corriges" and nom.startswith("CORRIGE_TD_") and nom.endswith(".pdf"):
        return "corrige_td", notion
    if parties[0] == "automatismes" and len(parties) == 2 and (
        nom.startswith("AUTOMATISMES_") or nom.startswith("automatismes-") or nom.startswith("qcm-")
    ):
        return "automatismes", notion
    return None


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=RACINE, check=True, capture_output=True, text=True
    ).stdout


def dates_ajout(aujourdhui: dt.date) -> dict[str, dt.date]:
    """Date de première mise en ligne de chaque fichier présent dans docs/."""
    dates: dict[str, dt.date] = {}
    try:
        journal = git(
            "log", "--diff-filter=A", "--name-only", "--format=@%ad",
            "--date=short", "--no-renames", "--", "docs",
        )
        statut = git("status", "--porcelain", "--untracked-files=all", "--", "docs")
    except (subprocess.CalledProcessError, FileNotFoundError):
        journal, statut = "", ""
    courante = None
    # Le journal va du plus récent au plus ancien : on garde le plus ancien
    # ajout (un fichier retiré puis remis garde sa première date).
    for ligne in journal.splitlines():
        if ligne.startswith("@"):
            courante = dt.date.fromisoformat(ligne[1:].strip())
        elif ligne.strip() and courante:
            dates[ligne.strip()] = courante
    for ligne in statut.splitlines():
        code, chemin = ligne[:2], ligne[3:].strip().strip('"')
        if ("?" in code or "A" in code) and chemin not in dates:
            dates[chemin] = aujourdhui
    return {c: d for c, d in dates.items() if (RACINE / c).is_file()}


def pages_notions() -> dict[str, tuple[str, str]]:
    """Nxx -> (chemin relatif de la page, titre court)."""
    pages = {}
    for page in sorted((DOCS / "notions").glob("N[0-9][0-9]-*.md")):
        notion = page.name[:3]
        titre = ""
        for ligne in page.read_text(encoding="utf-8").splitlines():
            if ligne.startswith("# "):
                titre = ligne[2:].split("—", 1)[-1].split(" : ", 1)[0].strip()
                break
        pages[notion] = (f"notions/{page.stem}/", titre)
    return pages


@dataclass
class Ligne:
    date: dt.date
    type: str
    cles: list[str] = field(default_factory=list)
    avec_corriges: set[str] = field(default_factory=set)


def regrouper(dates: dict[str, dt.date], aujourdhui: dt.date) -> list[Ligne]:
    limite = aujourdhui - dt.timedelta(days=JOURS_FENETRE - 1)
    groupes: dict[tuple[dt.date, str], set[str]] = {}
    for chemin, date in dates.items():
        if date < limite or date > aujourdhui:
            continue
        classe = classer(str(Path(chemin).relative_to("docs")))
        if classe:
            groupes.setdefault((date, classe[0]), set()).add(classe[1])
    lignes = []
    for (date, typ), cles in groupes.items():
        if typ == "corrige_parcours":
            # Fiches et corrigés mis en ligne le même jour : une seule ligne.
            cles = cles - groupes.get((date, "parcours"), set())
            if not cles:
                continue
        ligne = Ligne(date, typ, sorted(cles))
        if typ == "parcours":
            ligne.avec_corriges = cles & groupes.get((date, "corrige_parcours"), set())
        if typ == "corrige_devoir_blanc":
            ligne.cles = sorted(cles - groupes.get((date, "devoir_blanc"), set()))
            if not ligne.cles:
                continue
        if typ == "devoir_blanc":
            ligne.avec_corriges = cles & groupes.get((date, "corrige_devoir_blanc"), set())
        lignes.append(ligne)
    lignes.sort(key=lambda l: (-l.date.toordinal(), ORDRE.index(l.type)))
    return lignes[:MAX_LIGNES]


def plages(notions: list[str]) -> list[list[str]]:
    """Regrouper N01, N02, N03, N05 en [[N01, N02, N03], [N05]]."""
    blocs: list[list[str]] = []
    for n in notions:
        if blocs and int(n[1:]) == int(blocs[-1][-1][1:]) + 1:
            blocs[-1].append(n)
        else:
            blocs.append([n])
    return blocs


def lien(href: str, texte: str) -> str:
    return f'<a href="{html.escape(href)}">{html.escape(texte)}</a>'


def rendre_ligne(ligne: Ligne, pages: dict[str, tuple[str, str]]) -> str:
    singulier, pluriel = TYPES[ligne.type]
    cles = ligne.cles
    if ligne.type in ("devoir_blanc", "corrige_devoir_blanc", "apres_evaluation"):
        libelle = singulier if len(cles) == 1 else pluriel
        noms = " · ".join(html.escape(c) for c in cles)
        if ligne.type == "apres_evaluation":
            # « remédiation » seulement si des fiches pour retravailler sont en ligne.
            fiches = any(
                "FICHE" in f.name.upper()
                for c in cles
                for f in (DOCS / "preparer-evaluation").glob(f"*/apres-{c.lower()}/*.pdf")
            )
            suite = "sujets, corrigés et remédiation" if fiches else "sujets et corrigés"
            corps = f"<strong>Après le {noms}</strong>{NBSP}: {suite}"
        else:
            suite = ", avec corrigé" if ligne.avec_corriges == set(cles) and cles else ""
            corps = f"<strong>{libelle} {noms}</strong>{suite}"
        return corps + f" — {lien('preparer-evaluation/', 'Préparer une évaluation')}"

    if ligne.type == "automatismes":
        liste = " · ".join(
            f"{b[0]} à {b[-1]}" if len(b) >= 3 else " · ".join(b) for b in plages(cles)
        )
        return f"<strong>{lien('automatismes/', 'Automatismes en ligne')}</strong>{NBSP}: {liste}"

    ancre = "#parcours-guide" if ligne.type in ("parcours", "corrige_parcours") else ""
    cible = lambda n: pages[n][0] + ancre if n in pages else "notions/"  # noqa: E731

    libelle = singulier if len(cles) == 1 else pluriel
    if len(cles) == 1:
        n = cles[0]
        titre = pages.get(n, ("", ""))[1]
        texte = f"{n} {titre}".strip()
        morceaux = [lien(cible(n), texte)]
    elif len(cles) > 6:
        morceaux = []
        for bloc in plages(cles):
            if len(bloc) >= 3:
                morceaux.append(f"{lien(cible(bloc[0]), bloc[0])} à {lien(cible(bloc[-1]), bloc[-1])}")
            else:
                morceaux.extend(lien(cible(n), n) for n in bloc)
    else:
        morceaux = [lien(cible(n), n) for n in cles]

    suite = ""
    if ligne.type == "parcours" and ligne.avec_corriges:
        if ligne.avec_corriges == set(cles):
            suite = ", avec corrigés"
        else:
            morceaux = [
                m + (" (avec corrigés)" if n in ligne.avec_corriges else "")
                for n, m in zip(cles, morceaux)
            ]
    return f"<strong>{libelle}</strong>{NBSP}: " + " · ".join(morceaux) + suite


BLOC_REVISER = f"""  <div class="maths-news-box maths-news-box--revise">
    <h3>🔁 Réviser avec un parcours guidé</h3>
    <ol class="maths-steps">
      <li>Sur la page de la notion, ouvrir le <strong>parcours guidé</strong>.</li>
      <li>Pour chaque bloc, <strong>tenter la dernière question sans aide</strong>. Réussie{NBSP}: bloc suivant. Sinon{NBSP}: lire l'exemple résolu, puis faire tout le bloc.</li>
      <li>Se corriger avec <strong>«{NBSP}Je vérifie{NBSP}»</strong> (réponses à l'envers){NBSP}; si besoin, relire <strong>«{NBSP}Dans mon cours{NBSP}»</strong>.</li>
      <li>Terminer par les <strong>exercices du TD</strong> indiqués à côté de chaque question.</li>
    </ol>
    <p class="maths-news-foot">Avant un mini-test ou un DS{NBSP}: commencer par les notions qui résistent.</p>
  </div>"""


def site_a_des_parcours() -> bool:
    dossier = DOCS / "parcours-guide"
    return dossier.is_dir() and any(dossier.glob("PARCOURS_GUIDE_*.pdf"))


def construire_zone(aujourdhui: dt.date) -> str:
    pages = pages_notions()
    lignes = regrouper(dates_ajout(aujourdhui), aujourdhui)
    if lignes:
        items = "\n".join(
            f'      <li><span class="maths-news-date">{l.date:%d/%m}</span>'
            f"<span>{rendre_ligne(l, pages)}</span></li>"
            for l in lignes
        )
    else:
        items = (
            '      <li class="maths-news-empty">Pas de nouveau document ces trois dernières '
            "semaines : tout est dans les pages notions.</li>"
        )
    reviser = site_a_des_parcours()
    classe = "maths-news" + ("" if reviser else " maths-news--single")
    return "\n".join(
        [
            ZONE_START,
            "<!-- Zone régénérée par scripts/generer_nouveautes.py : ne pas modifier à la main. -->",
            f'<section class="{classe}">',
            '  <div class="maths-news-box">',
            "    <h3>🆕 Nouveautés</h3>",
            '    <ul class="maths-news-list">',
            items,
            "    </ul>",
            "  </div>",
            *([BLOC_REVISER] if reviser else []),
            "</section>",
            ZONE_END,
        ]
    )


def remplacer_zone(texte: str, zone: str) -> str:
    if texte.count(ZONE_START) != 1 or texte.count(ZONE_END) != 1:
        raise ValueError("zone AUTO-NEWS absente ou mal formée dans docs/index.md")
    debut = texte.index(ZONE_START)
    fin = texte.index(ZONE_END) + len(ZONE_END)
    if fin < debut:
        raise ValueError("zone AUTO-NEWS mal formée : END précède START")
    return texte[:debut] + zone + texte[fin:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--date", help="date du jour (AAAA-MM-JJ), pour les essais")
    parser.add_argument("--dry-run", action="store_true", help="afficher sans écrire")
    args = parser.parse_args(argv)
    aujourdhui = dt.date.fromisoformat(args.date) if args.date else dt.date.today()

    texte = INDEX.read_text(encoding="utf-8")
    if ZONE_START not in texte:
        print("Nouveautés : pas de marqueurs AUTO-NEWS dans docs/index.md, rien à faire.")
        return 0
    zone = construire_zone(aujourdhui)
    if args.dry_run:
        print(zone)
        return 0
    nouveau = remplacer_zone(texte, zone)
    if nouveau != texte:
        INDEX.write_text(nouveau, encoding="utf-8")
        print("Nouveautés : page d'accueil mise à jour.")
    else:
        print("Nouveautés : page d'accueil déjà à jour.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
