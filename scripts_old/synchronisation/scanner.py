"""Scan du dossier "Version en cours" pour construire les objets Notion."""

from __future__ import annotations

import re

from .config import SiteConfig
from .notion import Document, Notion, TypeDocument

# Dossier de notion : Nxx_NOM_MACHINE
MOTIF_DOSSIER_NOTION = re.compile(r"^(?P<numero>N\d{2})_(?P<nom>.+)$")

# Classement des PDF par préfixe. CORRIGE_TD doit être testé avant CORRIGE
# pour ne pas être classé à tort comme un simple corrigé.
MOTIFS_DOCUMENTS: tuple[tuple[TypeDocument, re.Pattern[str]], ...] = (
    (
        TypeDocument.CORRIGE,
        re.compile(r"^CORRIG(?:E|É)(?:_TD)?_N\d{2}(?:_|$)", re.IGNORECASE),
    ),
    (TypeDocument.COURS, re.compile(r"^COURS_N\d{2}(?:_|$)", re.IGNORECASE)),
    (TypeDocument.TD, re.compile(r"^TD_N\d{2}(?:_|$)", re.IGNORECASE)),
    (
        TypeDocument.AUTOMATISMES,
        re.compile(r"^AUTOMATISMES_N\d{2}(?:_|$)", re.IGNORECASE),
    ),
    (
        TypeDocument.MINITEST,
        re.compile(r"^MINITEST_N\d{2}(?:_|$)", re.IGNORECASE),
    ),
)


def classifier_pdf(nom_fichier_sans_extension: str) -> TypeDocument | None:
    """Reconnaître le type d'un PDF depuis son nom, ou None si inconnu."""
    for type_document, motif in MOTIFS_DOCUMENTS:
        if motif.match(nom_fichier_sans_extension):
            return type_document
    return None


def scanner_notions(config: SiteConfig) -> list[Notion]:
    """Découvrir tous les dossiers Nxx_XXXX et leurs PDF reconnus.

    Les notions sont triées par ordre numérique croissant, qui est
    l'ordre à utiliser partout (navigation, page d'accueil, rapports).
    """
    if not config.source.is_dir():
        raise FileNotFoundError(f"Dossier source introuvable : {config.source}")

    notions: dict[str, Notion] = {}
    for dossier in sorted(config.source.iterdir(), key=lambda item: item.name):
        if not dossier.is_dir():
            continue
        correspondance = MOTIF_DOSSIER_NOTION.match(dossier.name)
        if not correspondance:
            continue

        numero = correspondance.group("numero").upper()
        nom_machine = correspondance.group("nom")
        notions[numero] = Notion(numero=numero, nom_machine=nom_machine, dossier=dossier)

    for notion in notions.values():
        for chemin_pdf in sorted(notion.dossier.glob("*.pdf")):
            type_document = classifier_pdf(chemin_pdf.stem)
            if type_document is None:
                notion.pdf_non_reconnus.append(chemin_pdf)
                continue
            notion.documents.setdefault(type_document, []).append(
                Document(type=type_document, source=chemin_pdf)
            )

    return [notions[numero] for numero in sorted(notions)]
