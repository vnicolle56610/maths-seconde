#!/usr/bin/env python3
"""Publier les devoirs blancs dans la rubrique « Préparer une évaluation ».

Seuls les devoirs blancs sont publiés sur le site, jamais les sujets ni les
corrigés des évaluations réelles (décision du 20/10/2026). Rien n'est
découvert automatiquement dans les dossiers d'évaluations, où les vrais
sujets sont rangés à côté des devoirs blancs : chaque document publié est
déclaré dans ``devoirs_blancs.yaml``, à la racine du site, et c'est le
professeur qui fait avancer son état (non_publie → annonce → sujet →
sujet_et_corrige). « annonce » affiche l'évaluation dans « À venir » (date,
format, notions) sans aucun document, pour que les élèves se projettent.

Le script :
  - copie les PDF déclarés publiés dans docs/preparer-evaluation/<année>/ et
    retire de ce dossier tout PDF qui ne l'est plus ;
  - régénère la zone AUTO-EVAL de docs/preparer-evaluation/index.md
    (« À venir », puis « Pour réviser ») ;
  - ajoute, dans chaque page notion concernée, une zone AUTO-EVAL qui renvoie
    au devoir blanc, et tient à jour la ligne « Prochaine évaluation » de la
    carte de la page d'accueil (si ses marqueurs AUTO-EVAL y sont placés) ;
  - signale les mises en ligne en retard sur le calendrier déclaré, sans
    jamais les faire à la place du professeur ;
  - committe uniquement ce qu'il a écrit (comme publier_ressources_site.py),
    pour laisser l'arbre propre avant le déploiement.

Usage : python3 scripts/publier_devoirs_blancs.py [--dry-run] [--sans-commit]
"""

from __future__ import annotations

import argparse
import datetime as dt
import filecmp
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from synchronisation.config import charger_configuration  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = PROJECT_ROOT / "docs"
DECLARATION_PATH = PROJECT_ROOT / "devoirs_blancs.yaml"
RUBRIQUE = "preparer-evaluation"
RUBRIQUE_ROOT = DOCS_ROOT / RUBRIQUE
INDEX_PATH = RUBRIQUE_ROOT / "index.md"
ACCUEIL_PATH = DOCS_ROOT / "index.md"

ZONE_START = "<!-- AUTO-EVAL:START -->"
ZONE_END = "<!-- AUTO-EVAL:END -->"
AUTO_DOCS_END = "<!-- AUTO-DOCS:END -->"

ETATS = ("non_publie", "annonce", "sujet", "sujet_et_corrige")
PREFIXE_SUJET = "DEVOIR_BLANC_"
PREFIXE_CORRIGE = "CORRIGE_DEVOIR_BLANC_"
ID_PATTERN = re.compile(r"^(?P<type>MT|DS)(?P<numero>\d+)$")
NOTION_PATTERN = re.compile(r"^N\d{2}$")

TYPES = {"MT": "Mini-test", "DS": "Devoir surveillé"}
JOURS = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
MOIS = (
    "janvier", "février", "mars", "avril", "mai", "juin", "juillet",
    "août", "septembre", "octobre", "novembre", "décembre",
)

INDEX_INITIAL = """---
title: Préparer une évaluation
description: Devoirs blancs et corrigés auto-correctifs pour se préparer aux mini-tests et aux devoirs surveillés.
---

# Préparer une évaluation

Avant chaque mini-test et chaque devoir surveillé, un **devoir blanc** est mis en ligne environ une semaine avant. Sa première page, « Ce que je dois savoir faire », annonce les savoir-faire évalués, le format et les critères de rédaction. L'évaluation porte sur ces mêmes savoir-faire, avec d'autres exercices.

**Mode d'emploi**

1. Faire le devoir blanc **seul, sans le cours, en temps limité**.
2. Quand le corrigé est en ligne (quelques jours avant l'évaluation), se corriger au stylo d'une autre couleur.
3. Remplir la grille d'auto-évaluation (non notée) et refaire les exercices de TD indiqués pour chaque savoir-faire « pas encore » acquis.
4. Apporter une question précise au cours suivant.

{start}
{end}
"""


class DeclarationError(ValueError):
    """devoirs_blancs.yaml est mal formé ou désigne un fichier interdit."""


@dataclass(frozen=True)
class DevoirBlanc:
    id: str
    date: dt.date
    duree: str
    calculatrice: str
    notions: tuple[str, ...]
    dossier: Path
    sujet: str
    corrige: str
    sujet_prevu: dt.date | None
    corrige_prevu: dt.date | None
    etat: str
    # Texte libre quand l'évaluation a lieu à deux dates selon le groupe
    # (« mercredi 4 ou jeudi 5 novembre ») ; ``date`` est alors la dernière.
    date_affichee: str | None = None

    def libelle_date(self, avec_annee: bool = False) -> str:
        if self.date_affichee:
            return f"{self.date_affichee} {self.date.year}" if avec_annee else self.date_affichee
        return date_longue(self.date, avec_annee)

    @property
    def type_label(self) -> str:
        return TYPES[ID_PATTERN.match(self.id)["type"]]

    @property
    def titre(self) -> str:
        # Les élèves disent « le DS1 », mais « le mini-test 2 » (messages Pronote).
        match = ID_PATTERN.match(self.id)
        return f"Mini-test {match['numero']}" if match["type"] == "MT" else self.id

    @property
    def annee_scolaire(self) -> str:
        debut = self.date.year if self.date.month >= 8 else self.date.year - 1
        return f"{debut}-{debut + 1}"

    @property
    def ancre(self) -> str:
        return f"{self.id.lower()}-{self.annee_scolaire}"

    @property
    def fichiers_publies(self) -> tuple[str, ...]:
        if self.etat == "sujet":
            return (self.sujet,)
        if self.etat == "sujet_et_corrige":
            return (self.sujet, self.corrige)
        return ()


@dataclass
class Rapport:
    copies: list[Path] = field(default_factory=list)
    retires: list[Path] = field(default_factory=list)
    pages: list[Path] = field(default_factory=list)
    alertes: list[str] = field(default_factory=list)


def date_longue(jour: dt.date, avec_annee: bool = False) -> str:
    texte = f"{JOURS[jour.weekday()]} {jour.day} {MOIS[jour.month - 1]}"
    return f"{texte} {jour.year}" if avec_annee else texte


def lire_date(valeur, champ: str, ident: str) -> dt.date | None:
    if valeur is None:
        return None
    if isinstance(valeur, dt.date):
        return valeur
    try:
        return dt.date.fromisoformat(str(valeur))
    except ValueError as error:
        raise DeclarationError(f"{ident} : {champ} doit être une date AAAA-MM-JJ") from error


def charger_declarations(chemin: Path, source_root: Path) -> list[DevoirBlanc]:
    if not chemin.is_file():
        raise DeclarationError(f"Fichier introuvable : {chemin}")
    donnees = yaml.safe_load(chemin.read_text(encoding="utf-8")) or {}
    entrees = donnees.get("devoirs_blancs") or []
    if not isinstance(entrees, list):
        raise DeclarationError("« devoirs_blancs » doit être une liste")

    devoirs: list[DevoirBlanc] = []
    vus: set[str] = set()
    for brut in entrees:
        ident = str(brut.get("id", "")).strip()
        if not ID_PATTERN.match(ident):
            raise DeclarationError(f"id invalide « {ident} » (attendu MT2, DS1…)")
        date = lire_date(brut.get("date"), "date", ident)
        if date is None:
            raise DeclarationError(f"{ident} : date manquante")
        etat = str(brut.get("etat", "non_publie"))
        if etat not in ETATS:
            raise DeclarationError(f"{ident} : etat « {etat} » inconnu ({', '.join(ETATS)})")

        dossier = (source_root / str(brut.get("dossier", ""))).resolve()
        if not dossier.is_relative_to(source_root.resolve()) or dossier == source_root.resolve():
            raise DeclarationError(f"{ident} : dossier hors de la source")
        sujet = str(brut.get("sujet", ""))
        corrige = str(brut.get("corrige", ""))
        # Garde-fou : un vrai sujet (DS1_1S_SUJET_A.pdf…) est rangé dans le
        # même dossier ; seul un nom de devoir blanc peut partir sur le site.
        if not (sujet.startswith(PREFIXE_SUJET) and sujet.endswith(".pdf")):
            raise DeclarationError(f"{ident} : sujet « {sujet} » refusé (doit commencer par {PREFIXE_SUJET})")
        if not (corrige.startswith(PREFIXE_CORRIGE) and corrige.endswith(".pdf")):
            raise DeclarationError(f"{ident} : corrigé « {corrige} » refusé (doit commencer par {PREFIXE_CORRIGE})")

        notions = tuple(str(n) for n in brut.get("notions") or [])
        if not notions or not all(NOTION_PATTERN.match(n) for n in notions):
            raise DeclarationError(f"{ident} : notions attendues sous la forme [N03, N05]")

        devoir = DevoirBlanc(
            id=ident,
            date=date,
            duree=str(brut.get("duree", "")).strip(),
            calculatrice=str(brut.get("calculatrice", "")).strip(),
            notions=notions,
            dossier=dossier,
            sujet=sujet,
            corrige=corrige,
            sujet_prevu=lire_date(brut.get("sujet_prevu"), "sujet_prevu", ident),
            corrige_prevu=lire_date(brut.get("corrige_prevu"), "corrige_prevu", ident),
            etat=etat,
            date_affichee=str(brut["date_affichee"]).strip() if brut.get("date_affichee") else None,
        )
        if devoir.ancre in vus:
            raise DeclarationError(f"{ident} déclaré deux fois pour {devoir.annee_scolaire}")
        vus.add(devoir.ancre)
        for nom in devoir.fichiers_publies:
            if not (dossier / nom).is_file():
                raise DeclarationError(f"{ident} : fichier introuvable {dossier / nom}")
        devoirs.append(devoir)
    return devoirs


def page_notion(notion: str) -> Path | None:
    pages = sorted((DOCS_ROOT / "notions").glob(f"{notion}-*.md"))
    return pages[0] if len(pages) == 1 else None


def titre_notion(page: Path) -> str:
    for ligne in page.read_text(encoding="utf-8").splitlines():
        if ligne.startswith("# "):
            return ligne[2:].strip()
    return page.stem


def nom_court(devoir: DevoirBlanc) -> str:
    return devoir.titre if devoir.titre == devoir.id else devoir.titre.lower()


def destination(devoir: DevoirBlanc, nom: str) -> Path:
    return RUBRIQUE_ROOT / devoir.annee_scolaire / nom


def synchroniser_pdf(devoirs: list[DevoirBlanc], rapport: Rapport, dry_run: bool) -> None:
    voulus: set[Path] = set()
    for devoir in devoirs:
        for nom in devoir.fichiers_publies:
            cible = destination(devoir, nom)
            voulus.add(cible)
            source = devoir.dossier / nom
            if cible.is_file() and filecmp.cmp(source, cible, shallow=False):
                continue
            rapport.copies.append(cible)
            if not dry_run:
                cible.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, cible)
    if RUBRIQUE_ROOT.is_dir():
        for present in sorted(RUBRIQUE_ROOT.rglob("*.pdf")):
            if present not in voulus:
                rapport.retires.append(present)
                if not dry_run:
                    present.unlink()


def lignes_entree(devoir: DevoirBlanc, aujourd_hui: dt.date) -> list[str]:
    passe = devoir.date < aujourd_hui
    lignes = [
        f"### {devoir.titre} — {devoir.libelle_date(avec_annee=passe)} {{#{devoir.ancre}}}",
        "",
    ]
    format_ = [devoir.type_label]
    if devoir.duree:
        format_.append(devoir.duree)
    if devoir.calculatrice:
        format_.append(f"calculatrice {devoir.calculatrice}")
    lignes.append(f"**{' · '.join(format_)}**  ")

    liens = []
    for notion in devoir.notions:
        page = page_notion(notion)
        if page is None:
            liens.append(notion)
        else:
            liens.append(f"[{titre_notion(page)}](../notions/{page.name})")
    lignes += [f"Notions : {' · '.join(liens)}", ""]

    dossier = devoir.annee_scolaire
    if devoir.etat == "annonce":
        quand = f"le {date_longue(devoir.sujet_prevu)}" if devoir.sujet_prevu else "environ une semaine avant"
        lignes += [f"- 📄 Devoir blanc et fiche « Ce que je dois savoir faire » : en ligne {quand}.", ""]
        return lignes
    lignes.append(
        f"- 📄 [Devoir blanc : fiche « Ce que je dois savoir faire » et sujet]({dossier}/{devoir.sujet})"
    )
    if devoir.etat == "sujet_et_corrige":
        lignes.append(f"- ✅ [Corrigé et grille d'auto-évaluation]({dossier}/{devoir.corrige})")
    elif devoir.corrige_prevu:
        lignes.append(
            f"- ✅ Corrigé et grille d'auto-évaluation : en ligne le {date_longue(devoir.corrige_prevu)}."
        )
    else:
        lignes.append("- ✅ Corrigé et grille d'auto-évaluation : en ligne quelques jours avant l'évaluation.")
    lignes.append("")
    return lignes


def contenu_index(devoirs: list[DevoirBlanc], aujourd_hui: dt.date) -> str:
    publies = [d for d in devoirs if d.etat != "non_publie"]
    a_venir = sorted((d for d in publies if d.date >= aujourd_hui), key=lambda d: d.date)
    # Une évaluation seulement annoncée n'a rien à réviser une fois passée.
    passes = sorted(
        (d for d in publies if d.date < aujourd_hui and d.etat != "annonce"),
        key=lambda d: d.date,
    )

    lignes = ["## À venir", ""]
    if a_venir:
        for devoir in a_venir:
            lignes += lignes_entree(devoir, aujourd_hui)
    else:
        lignes += [
            "Aucune évaluation annoncée pour le moment : le prochain devoir blanc sera publié environ une semaine avant l'évaluation.",
            "",
        ]
    if passes:
        lignes += [
            "## Pour réviser — évaluations passées",
            "",
            "Les devoirs blancs des évaluations passées restent en ligne pour les révisions.",
            "",
        ]
        for devoir in passes:
            lignes += lignes_entree(devoir, aujourd_hui)
    return "\n".join(lignes).rstrip("\n")


def remplacer_zone(texte: str, contenu: str | None, ancrage: str | None) -> str:
    """Remplacer (ou créer, ou retirer si contenu vaut None) la zone AUTO-EVAL."""
    if texte.count(ZONE_START) > 1 or texte.count(ZONE_END) > 1 or (
        texte.count(ZONE_START) != texte.count(ZONE_END)
    ):
        raise ValueError("zone AUTO-EVAL mal formée")
    if ZONE_START in texte:
        debut = texte.index(ZONE_START)
        fin = texte.index(ZONE_END) + len(ZONE_END)
        if fin < debut:
            raise ValueError("zone AUTO-EVAL mal formée : END précède START")
        if contenu is None:
            avant = texte[:debut].rstrip("\n")
            apres = texte[fin:].lstrip("\n")
            return f"{avant}\n\n{apres}" if apres else f"{avant}\n"
        return f"{texte[:debut]}{ZONE_START}\n{contenu}\n{ZONE_END}{texte[fin:]}"
    if contenu is None:
        return texte
    zone = f"{ZONE_START}\n{contenu}\n{ZONE_END}"
    if ancrage and ancrage in texte:
        position = texte.index(ancrage) + len(ancrage)
        return f"{texte[:position]}\n\n{zone}{texte[position:]}"
    return f"{texte.rstrip()}\n\n{zone}\n"


def ecrire_si_change(page: Path, nouveau: str, rapport: Rapport, dry_run: bool) -> None:
    ancien = page.read_text(encoding="utf-8") if page.is_file() else None
    if nouveau == ancien:
        return
    rapport.pages.append(page)
    if not dry_run:
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(nouveau, encoding="utf-8")


def mettre_a_jour_index(devoirs: list[DevoirBlanc], aujourd_hui: dt.date, rapport: Rapport, dry_run: bool) -> None:
    texte = (
        INDEX_PATH.read_text(encoding="utf-8")
        if INDEX_PATH.is_file()
        else INDEX_INITIAL.format(start=ZONE_START, end=ZONE_END)
    )
    ecrire_si_change(INDEX_PATH, remplacer_zone(texte, contenu_index(devoirs, aujourd_hui), None), rapport, dry_run)


def mettre_a_jour_notions(devoirs: list[DevoirBlanc], aujourd_hui: dt.date, rapport: Rapport, dry_run: bool) -> None:
    par_notion: dict[str, list[DevoirBlanc]] = {}
    for devoir in devoirs:
        if devoir.etat == "non_publie":
            continue
        for notion in devoir.notions:
            par_notion.setdefault(notion, []).append(devoir)

    for page in sorted((DOCS_ROOT / "notions").glob("N[0-9][0-9]-*.md")):
        notion = page.name[:3]
        lignes = []
        for devoir in sorted(par_notion.get(notion, []), key=lambda d: d.date):
            lien = f"../{RUBRIQUE}/index.md#{devoir.ancre}"
            if devoir.date >= aujourd_hui and devoir.etat == "annonce":
                quand = f"le {date_longue(devoir.sujet_prevu)}" if devoir.sujet_prevu else "bientôt"
                lignes.append(
                    f"- 🎯 Évaluée au {nom_court(devoir)} du {devoir.libelle_date()} : "
                    f"[devoir blanc en ligne {quand}]({lien})"
                )
            elif devoir.etat == "annonce":
                continue
            elif devoir.date >= aujourd_hui:
                lignes.append(
                    f"- 🎯 Évaluée au {nom_court(devoir)} du {devoir.libelle_date()} : "
                    f"[voir le devoir blanc]({lien})"
                )
            else:
                lignes.append(
                    f"- 🎯 Pour réviser : [devoir blanc du {nom_court(devoir)} "
                    f"du {devoir.libelle_date(avec_annee=True)}]({lien})"
                )
        texte = page.read_text(encoding="utf-8")
        contenu = "\n".join(lignes) if lignes else None
        ecrire_si_change(page, remplacer_zone(texte, contenu, AUTO_DOCS_END), rapport, dry_run)


def contenu_accueil(devoirs: list[DevoirBlanc], aujourd_hui: dt.date) -> str:
    """Ligne « Prochaine évaluation » de la carte de la page d'accueil."""
    a_venir = sorted(
        (d for d in devoirs if d.etat != "non_publie" and d.date >= aujourd_hui), key=lambda d: d.date
    )
    if not a_venir:
        return '    <p class="maths-card-next">Le prochain devoir blanc sera publié environ une semaine avant l\'évaluation.</p>'
    prochain = a_venir[0]
    if prochain.etat == "annonce":
        suite = (
            f"devoir blanc en ligne le {date_longue(prochain.sujet_prevu)}"
            if prochain.sujet_prevu else "devoir blanc bientôt en ligne"
        )
    elif prochain.etat == "sujet":
        suite = "devoir blanc en ligne"
    else:
        suite = "devoir blanc et corrigé en ligne"
    return (
        f'    <p class="maths-card-next">Prochaine évaluation : <strong>{prochain.titre}</strong>, '
        f"{prochain.libelle_date()} — {suite}.</p>"
    )


def mettre_a_jour_accueil(devoirs: list[DevoirBlanc], aujourd_hui: dt.date, rapport: Rapport, dry_run: bool) -> None:
    # La carte de l'accueil est écrite à la main ; on ne remplit sa zone que si
    # les marqueurs y ont été placés, sans jamais en créer.
    if not ACCUEIL_PATH.is_file():
        return
    texte = ACCUEIL_PATH.read_text(encoding="utf-8")
    if ZONE_START not in texte:
        return
    ecrire_si_change(ACCUEIL_PATH, remplacer_zone(texte, contenu_accueil(devoirs, aujourd_hui), None), rapport, dry_run)


def verifier_calendrier(devoirs: list[DevoirBlanc], aujourd_hui: dt.date, rapport: Rapport) -> None:
    for devoir in devoirs:
        if devoir.date < aujourd_hui:
            continue
        if devoir.etat in ("non_publie", "annonce") and devoir.sujet_prevu and devoir.sujet_prevu <= aujourd_hui:
            rapport.alertes.append(
                f"{devoir.id} : devoir blanc prévu le {devoir.sujet_prevu:%d/%m}, pas encore publié "
                "(passer etat à « sujet »)."
            )
        if devoir.etat != "sujet_et_corrige" and devoir.corrige_prevu and devoir.corrige_prevu <= aujourd_hui:
            rapport.alertes.append(
                f"{devoir.id} : corrigé prévu le {devoir.corrige_prevu:%d/%m}, pas encore publié "
                "(passer etat à « sujet_et_corrige »)."
            )


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=PROJECT_ROOT, text=True, capture_output=True, check=False)


def committer(rapport: Rapport) -> str | None:
    """Committer uniquement ce que cette exécution a écrit, plus la déclaration."""
    chemins = [*rapport.copies, *rapport.retires, *rapport.pages, DECLARATION_PATH]
    ajout = git("add", "-A", "--", *[str(c) for c in chemins])
    if ajout.returncode != 0:
        raise RuntimeError(f"git add a échoué :\n{ajout.stderr}")
    if git("diff", "--cached", "--quiet").returncode == 0:
        return None
    message = [
        "Préparer une évaluation : "
        f"{len(rapport.copies)} PDF copié(s), {len(rapport.retires)} retiré(s), "
        f"{len(rapport.pages)} page(s) mise(s) à jour",
        "",
        "Généré par scripts/publier_devoirs_blancs.py depuis devoirs_blancs.yaml.",
    ]
    commit = git("commit", "-m", "\n".join(message))
    if commit.returncode != 0:
        raise RuntimeError(f"git commit a échoué :\n{commit.stderr or commit.stdout}")
    return git("rev-parse", "HEAD").stdout.strip()


def afficher(titre: str, chemins: list[Path]) -> None:
    print(f"{titre} : {len(chemins)}")
    for chemin in chemins:
        print(f"  - {chemin.relative_to(PROJECT_ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="simuler sans rien écrire")
    parser.add_argument("--sans-commit", action="store_true", help="écrire sans committer")
    parser.add_argument("--date", help="date du jour simulée (AAAA-MM-JJ), pour tester")
    args = parser.parse_args()

    aujourd_hui = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    config = charger_configuration(PROJECT_ROOT / "config_site.yaml")
    print(f"Devoirs blancs : {DECLARATION_PATH.relative_to(PROJECT_ROOT)} (source {config.source})")

    try:
        devoirs = charger_declarations(DECLARATION_PATH, config.source)
        rapport = Rapport()
        synchroniser_pdf(devoirs, rapport, args.dry_run)
        mettre_a_jour_index(devoirs, aujourd_hui, rapport, args.dry_run)
        mettre_a_jour_notions(devoirs, aujourd_hui, rapport, args.dry_run)
        mettre_a_jour_accueil(devoirs, aujourd_hui, rapport, args.dry_run)
        verifier_calendrier(devoirs, aujourd_hui, rapport)
    except (DeclarationError, OSError, ValueError, yaml.YAMLError) as error:
        print(f"\nERREUR : {error}")
        return 1

    for devoir in sorted(devoirs, key=lambda d: d.date):
        print(f"  {devoir.id:<4} {devoir.date:%d/%m/%Y}  {devoir.etat}")
    afficher("PDF copiés", rapport.copies)
    afficher("PDF retirés", rapport.retires)
    afficher("Pages mises à jour", rapport.pages)
    for alerte in rapport.alertes:
        print(f"À FAIRE : {alerte}")

    if args.dry_run or args.sans_commit:
        return 0
    try:
        sha = committer(rapport)
    except RuntimeError as error:
        print(f"\nERREUR : {error}")
        return 1
    print(f"Commit créé : {sha[:12]}" if sha else "Aucun changement à committer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
