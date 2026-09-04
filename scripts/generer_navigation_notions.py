"""Insérer un bandeau de navigation (notion précédente / suivante) sur les pages Nxx.

Le script parcourt les pages ``docs/notions/Nxx-*.md`` référencées dans la
navigation de ``mkdocs.yml`` et insère, juste sous le titre de chaque page,
un bandeau HTML délimité par les marqueurs ``NOTION-NAV``. Il est idempotent :
relancé après l'ajout d'une notion, il met à jour tous les bandeaux existants.

Usage :
    python3 scripts/generer_navigation_notions.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTIONS_DIR = PROJECT_ROOT / "docs" / "notions"
MKDOCS_FILE = PROJECT_ROOT / "mkdocs.yml"

NAV_START = "<!-- NOTION-NAV:START -->"
NAV_END = "<!-- NOTION-NAV:END -->"

ICON_PREV = (
    '<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true">'
    '<path d="M16 6v12L6 12z" fill="currentColor"/></svg>'
)
ICON_NEXT = (
    '<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true">'
    '<path d="M8 6v12l10-6z" fill="currentColor"/></svg>'
)


def detect_newline(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def lister_notions_navigation() -> list[Path]:
    """Retourner les pages de notions citées dans mkdocs.yml, triées par numéro."""
    texte = MKDOCS_FILE.read_text(encoding="utf-8")
    noms = re.findall(r"notions/(N\d+[^\s:]*\.md)", texte)
    pages: list[Path] = []
    for nom in noms:
        page = NOTIONS_DIR / nom
        if page.is_file():
            pages.append(page)
        else:
            print(f"AVERTISSEMENT : page absente du dossier notions : {nom}")

    def numero(page: Path) -> int:
        match = re.match(r"N(\d+)", page.name)
        return int(match.group(1)) if match else 0

    return sorted(pages, key=numero)


def extraire_titre(page: Path) -> str:
    """Lire le titre H1 de la page ; repli sur le nom du fichier."""
    for ligne in page.read_text(encoding="utf-8").splitlines():
        if ligne.startswith("# "):
            return ligne[2:].strip()
    return page.stem.replace("-", " ")


def construire_bandeau(
    precedente: tuple[str, str] | None,
    suivante: tuple[str, str] | None,
) -> str:
    """Construire le bloc HTML du bandeau. Chaque voisin est (slug, titre)."""
    boutons: list[str] = []
    if precedente is not None:
        slug, titre = precedente
        boutons.append(
            f'<a class="notion-nav__btn notion-nav__btn--prev" href="../{slug}/">'
            f'<span class="notion-nav__icon">{ICON_PREV}</span>'
            f'<span class="notion-nav__text"><small>Notion précédente</small>'
            f'<span class="notion-nav__title">{titre}</span></span></a>'
        )
    if suivante is not None:
        slug, titre = suivante
        boutons.append(
            f'<a class="notion-nav__btn notion-nav__btn--next" href="../{slug}/">'
            f'<span class="notion-nav__text"><small>Notion suivante</small>'
            f'<span class="notion-nav__title">{titre}</span></span>'
            f'<span class="notion-nav__icon">{ICON_NEXT}</span></a>'
        )
    lignes = "\n".join(boutons)
    return (
        f'<nav class="notion-nav" aria-label="Navigation entre notions">\n'
        f"{lignes}\n"
        f"</nav>"
    )


def inserer_bandeau(texte: str, bandeau: str, newline: str) -> str:
    """Placer le bandeau sous le titre H1, ou mettre à jour la zone existante."""
    bloc = f"{NAV_START}{newline}{bandeau}{newline}{NAV_END}"

    if NAV_START in texte and NAV_END in texte:
        debut = texte.index(NAV_START)
        fin = texte.index(NAV_END) + len(NAV_END)
        return texte[:debut] + bloc + texte[fin:]

    lignes = texte.split(newline)
    for indice, ligne in enumerate(lignes):
        if ligne.startswith("# "):
            lignes[indice + 1 : indice + 1] = ["", bloc]
            return newline.join(lignes)

    return f"{bloc}{newline}{newline}{texte}"


def main() -> int:
    pages = lister_notions_navigation()
    if not pages:
        print("Aucune page de notion trouvée dans la navigation de mkdocs.yml.")
        return 1

    infos = [(page, page.stem, extraire_titre(page)) for page in pages]
    for indice, (page, _slug, _titre) in enumerate(infos):
        precedente = infos[indice - 1][1:] if indice > 0 else None
        suivante = infos[indice + 1][1:] if indice < len(infos) - 1 else None

        texte = page.read_text(encoding="utf-8")
        newline = detect_newline(texte)
        bandeau = construire_bandeau(precedente, suivante)
        bandeau = bandeau.replace("\n", newline)
        nouveau_texte = inserer_bandeau(texte, bandeau, newline)
        if nouveau_texte != texte:
            page.write_text(nouveau_texte, encoding="utf-8")
            print(f"Bandeau mis à jour : {page.name}")
        else:
            print(f"Déjà à jour : {page.name}")

    print(f"{len(infos)} page(s) traitée(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
