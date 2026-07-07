"""Génération automatique : PDF publiés, pages de notion, index, nav mkdocs.

Rien de ce que ce module écrit ne doit être retouché à la main : relancer
la synchronisation doit toujours reproduire exactement le même résultat
(idempotence).
"""

from __future__ import annotations

import filecmp
import logging
import os
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

from .config import SiteConfig
from .notion import LIBELLES, ORDRE_AFFICHAGE, Document, Notion
from .typographie import construire_titre

logger = logging.getLogger(__name__)

MARQUEUR_DEBUT = "<!-- AUTO-DOCS:START -->"
MARQUEUR_FIN = "<!-- AUTO-DOCS:END -->"


@dataclass
class RapportGeneration:
    pdf_copies: list[Path] = field(default_factory=list)
    pdf_inchanges: list[Path] = field(default_factory=list)
    pages_creees: list[Path] = field(default_factory=list)
    pages_renommees: list[tuple[Path, Path]] = field(default_factory=list)
    pages_modifiees: list[Path] = field(default_factory=list)
    avertissements: list[str] = field(default_factory=list)


def _verifier_dans_docs(chemin: Path, docs: Path) -> None:
    if not chemin.resolve(strict=False).is_relative_to(docs.resolve()):
        raise ValueError(f"Chemin en dehors de docs/ refusé : {chemin}")


def _detecter_newline(texte: str) -> str:
    return "\r\n" if "\r\n" in texte else "\n"


def _lien_relatif(page_markdown: Path, cible: Path) -> str:
    chemin_relatif = Path(os.path.relpath(cible, start=page_markdown.parent))
    return quote(chemin_relatif.as_posix(), safe="/")


# --------------------------------------------------------------------------
# Copie des PDF
# --------------------------------------------------------------------------

def copier_documents(config: SiteConfig, notions: list[Notion], rapport: RapportGeneration) -> None:
    for notion in notions:
        for document in notion.tous_les_documents():
            destination = config.docs / document.destination
            _verifier_dans_docs(destination, config.docs)

            if (
                destination.is_file()
                and filecmp.cmp(document.source, destination, shallow=False)
            ):
                rapport.pdf_inchanges.append(destination)
                continue

            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(document.source, destination)
            rapport.pdf_copies.append(destination)


# --------------------------------------------------------------------------
# Pages de notion (docs/notions/Nxx-slug.md)
# --------------------------------------------------------------------------

def _suffixe_distinctif(document: Document, notion: Notion) -> str:
    """Extraire la part du nom de fichier qui distingue deux PDF du même type."""
    correspondance = re.search(
        rf"{notion.numero}_(.+)", document.source.stem, re.IGNORECASE
    )
    if not correspondance:
        return document.source.stem
    suffixe = correspondance.group(1)
    prefixe_notion = f"{notion.nom_machine}_"
    if suffixe.upper().startswith(prefixe_notion.upper()):
        suffixe = suffixe[len(prefixe_notion):]
    return suffixe or document.source.stem


def _libelle_document(document: Document, notion: Notion, doublon: bool) -> str:
    base = f"{LIBELLES[document.type]} {notion.numero}"
    if not doublon:
        return base
    suffixe = _suffixe_distinctif(document, notion)
    return f"{base} — {construire_titre(suffixe)}"


def _rendre_liens_documents(page_markdown: Path, docs: Path, notion: Notion) -> str:
    documents = notion.tous_les_documents()
    occurrences_par_type: dict[str, int] = {}
    for document in documents:
        occurrences_par_type[document.type] = occurrences_par_type.get(document.type, 0) + 1

    documents_tries = sorted(
        documents,
        key=lambda document: (
            ORDRE_AFFICHAGE[document.type],
            document.source.name.casefold(),
        ),
    )
    lignes = []
    for document in documents_tries:
        doublon = occurrences_par_type[document.type] > 1
        libelle = _libelle_document(document, notion, doublon)
        lien = _lien_relatif(page_markdown, docs / document.destination)
        lignes.append(f"- [{libelle}]({lien})")
    return "\n".join(lignes)


def _remplacer_zone_auto_docs(texte: str, contenu: str, newline: str) -> str:
    debut = texte.count(MARQUEUR_DEBUT)
    fin = texte.count(MARQUEUR_FIN)

    if debut == 0 and fin == 0:
        titre_documents = re.search(
            r"^##[ \t]+Documents[ \t]*\r?$", texte, flags=re.MULTILINE | re.IGNORECASE
        )
        bloc = f"{MARQUEUR_DEBUT}{newline}{contenu}{newline}{MARQUEUR_FIN}"
        if titre_documents:
            fin_ligne = texte.find(newline, titre_documents.end())
            point_insertion = (
                len(texte) if fin_ligne == -1 else fin_ligne + len(newline)
            )
            return (
                texte[:point_insertion]
                + newline
                + bloc
                + newline
                + texte[point_insertion:]
            )
        separateur = newline if texte.endswith(("\n", "\r")) else newline * 2
        prefixe = "" if not texte else separateur
        return f"{texte}{prefixe}## Documents{newline}{newline}{bloc}{newline}"

    if debut != 1 or fin != 1:
        raise ValueError("Zone AUTO-DOCS mal formée (plusieurs marqueurs)")

    debut_contenu = texte.index(MARQUEUR_DEBUT) + len(MARQUEUR_DEBUT)
    fin_contenu = texte.index(MARQUEUR_FIN)
    if fin_contenu < debut_contenu:
        raise ValueError("Zone AUTO-DOCS mal formée (END avant START)")

    return (
        texte[:debut_contenu]
        + newline
        + contenu
        + newline
        + texte[fin_contenu:]
    )


def _remplacer_titre(texte: str, nouveau_titre: str, newline: str) -> str:
    """Remplacer le premier titre H1, ou l'ajouter s'il n'existe pas."""
    motif_h1 = re.compile(r"^#[ \t]+.+?[ \t]*\r?$", flags=re.MULTILINE)
    if motif_h1.search(texte):
        return motif_h1.sub(f"# {nouveau_titre}", texte, count=1)
    return f"# {nouveau_titre}{newline}{newline}{texte}" if texte else f"# {nouveau_titre}{newline}"


def _trouver_page_existante(dossier_notions: Path, notion: Notion) -> Path | None:
    correspondances = sorted(dossier_notions.glob(f"{notion.numero}-*.md"))
    if not correspondances:
        return None
    if len(correspondances) > 1:
        raise ValueError(
            f"Plusieurs pages correspondent à {notion.numero} : "
            + ", ".join(str(chemin) for chemin in correspondances)
        )
    return correspondances[0]


def generer_page_notion(config: SiteConfig, notion: Notion, rapport: RapportGeneration) -> Path:
    dossier_notions = config.docs / "notions"
    dossier_notions.mkdir(parents=True, exist_ok=True)

    page_actuelle = _trouver_page_existante(dossier_notions, notion)
    page_cible = dossier_notions / notion.nom_fichier_page
    _verifier_dans_docs(page_cible, config.docs)

    if page_actuelle is None:
        texte_original = ""
        octets_originaux = b""
    else:
        octets_originaux = page_actuelle.read_bytes()
        texte_original = octets_originaux.decode("utf-8")
        if page_actuelle != page_cible:
            page_actuelle.rename(page_cible)
            rapport.pages_renommees.append((page_actuelle, page_cible))

    newline = _detecter_newline(texte_original) if texte_original else "\n"
    titre_complet = f"{notion.numero} — {notion.titre}"

    texte = _remplacer_titre(texte_original, titre_complet, newline)
    contenu_liens = _rendre_liens_documents(page_cible, config.docs, notion).replace(
        "\n", newline
    )
    texte = _remplacer_zone_auto_docs(texte, contenu_liens, newline)

    octets_mis_a_jour = texte.encode("utf-8")
    if octets_mis_a_jour == octets_originaux:
        return page_cible

    page_cible.write_bytes(octets_mis_a_jour)
    if page_actuelle is None:
        rapport.pages_creees.append(page_cible)
    else:
        rapport.pages_modifiees.append(page_cible)
    return page_cible


# --------------------------------------------------------------------------
# docs/index.md — section "## Accès rapide"
# --------------------------------------------------------------------------

def generer_index(config: SiteConfig, notions: list[Notion], rapport: RapportGeneration) -> None:
    index_path = config.docs / "index.md"
    _verifier_dans_docs(index_path, config.docs)
    if not index_path.is_file():
        rapport.avertissements.append(f"{index_path} introuvable, section non générée")
        return

    octets_originaux = index_path.read_bytes()
    texte_original = octets_originaux.decode("utf-8")
    newline = _detecter_newline(texte_original)

    titre_section = re.search(
        r"^##[ \t]+Accès rapide[ \t]*\r?$", texte_original, flags=re.MULTILINE | re.IGNORECASE
    )
    if not titre_section:
        rapport.avertissements.append(
            f"{index_path} : section « Accès rapide » introuvable, non modifiée"
        )
        return

    fin_ligne_titre = texte_original.find(newline, titre_section.end())
    debut_section = (
        len(texte_original) if fin_ligne_titre == -1 else fin_ligne_titre + len(newline)
    )
    prochain_titre = re.search(
        r"^#{1,2}[ \t]+", texte_original[debut_section:], flags=re.MULTILINE
    )
    fin_section = (
        len(texte_original)
        if prochain_titre is None
        else debut_section + prochain_titre.start()
    )

    section = texte_original[debut_section:fin_section]
    lignes_section = section.splitlines()

    motif_lien_notion = re.compile(r"^-\s+\[.*\]\(notions/N\d{2}-.*\.md\)\s*$")
    lignes_conservees = [
        ligne for ligne in lignes_section if not motif_lien_notion.match(ligne.strip())
    ]
    # Retirer les lignes vides en fin de bloc conservé pour maîtriser l'espacement.
    while lignes_conservees and not lignes_conservees[-1].strip():
        lignes_conservees.pop()

    lignes_notions = [
        f"- [{notion.numero} — {notion.titre}]"
        f"(notions/{notion.nom_fichier_page})"
        for notion in notions
    ]

    bloc_final = lignes_conservees + lignes_notions
    nouvelle_section = newline.join(bloc_final) + newline if bloc_final else newline

    texte_final = (
        texte_original[:debut_section] + nouvelle_section + texte_original[fin_section:]
    )
    octets_finaux = texte_final.encode("utf-8")
    if octets_finaux == octets_originaux:
        return
    index_path.write_bytes(octets_finaux)
    rapport.pages_modifiees.append(index_path)


# --------------------------------------------------------------------------
# mkdocs.yml — bloc "Notions:" imbriqué sous nav:
# --------------------------------------------------------------------------

def generer_nav_mkdocs(config: SiteConfig, notions: list[Notion], rapport: RapportGeneration) -> None:
    mkdocs_path = config.mkdocs_yml
    if not mkdocs_path.is_file():
        rapport.avertissements.append(f"{mkdocs_path} introuvable, nav non générée")
        return

    octets_originaux = mkdocs_path.read_bytes()
    texte_original = octets_originaux.decode("utf-8")
    newline = _detecter_newline(texte_original)
    lignes = texte_original.splitlines(keepends=True)

    index_nav = [
        i for i, ligne in enumerate(lignes)
        if re.fullmatch(r"(?P<indent> *)nav:[ \t]*(?:#.*)?(?:\r?\n)?", ligne)
    ]
    if len(index_nav) != 1:
        rapport.avertissements.append(f"{mkdocs_path} : bloc nav ambigu ou absent")
        return
    i_nav = index_nav[0]
    indent_nav = len(lignes[i_nav]) - len(lignes[i_nav].lstrip(" "))

    fin_nav = len(lignes)
    for i in range(i_nav + 1, len(lignes)):
        stripped = lignes[i].strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(lignes[i]) - len(lignes[i].lstrip(" "))
        if indent <= indent_nav:
            fin_nav = i
            break

    motif_notions = re.compile(
        r'(?P<indent> *)-[ \t]+(?:"Notions"|\'Notions\'|Notions):[ \t]*(?:#.*)?(?:\r?\n)?'
    )
    index_notions = [
        i for i in range(i_nav + 1, fin_nav) if motif_notions.fullmatch(lignes[i])
    ]
    if len(index_notions) != 1:
        rapport.avertissements.append(f"{mkdocs_path} : bloc « Notions » ambigu ou absent")
        return
    i_notions = index_notions[0]
    indent_notions = len(lignes[i_notions]) - len(lignes[i_notions].lstrip(" "))

    fin_bloc = fin_nav
    for i in range(i_notions + 1, fin_nav):
        stripped = lignes[i].strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(lignes[i]) - len(lignes[i].lstrip(" "))
        if indent <= indent_notions:
            fin_bloc = i
            break

    style_citation = '"'
    for i in range(i_notions + 1, fin_bloc):
        stripped = lignes[i].strip()
        if stripped and not stripped.startswith("#"):
            contenu_apres_tiret = stripped[1:].lstrip()
            if contenu_apres_tiret.startswith("'"):
                style_citation = "'"
            break

    indent_entree = indent_notions + 4
    for i in range(i_notions + 1, fin_bloc):
        stripped = lignes[i].strip()
        if stripped and not stripped.startswith("#"):
            indent_entree = len(lignes[i]) - len(lignes[i].lstrip(" "))
            break

    def echapper(titre: str) -> str:
        if style_citation == "'":
            return "'" + titre.replace("'", "''") + "'"
        echappe = titre.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{echappe}"'

    nouvelles_lignes_bloc = [
        f"{' ' * indent_entree}- {echapper(f'{notion.numero} — {notion.titre}')}: "
        f"notions/{notion.nom_fichier_page}{newline}"
        for notion in notions
    ]

    lignes_finales = lignes[: i_notions + 1] + nouvelles_lignes_bloc + lignes[fin_bloc:]
    texte_final = "".join(lignes_finales)
    octets_finaux = texte_final.encode("utf-8")
    if octets_finaux == octets_originaux:
        return
    mkdocs_path.write_bytes(octets_finaux)
    rapport.pages_modifiees.append(mkdocs_path)


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def generer_site(config: SiteConfig, notions: list[Notion]) -> RapportGeneration:
    rapport = RapportGeneration()
    copier_documents(config, notions, rapport)
    for notion in notions:
        generer_page_notion(config, notion, rapport)
    generer_index(config, notions, rapport)
    generer_nav_mkdocs(config, notions, rapport)
    return rapport
