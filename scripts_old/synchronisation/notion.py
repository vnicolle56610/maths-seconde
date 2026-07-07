"""Modèle de données : une notion et ses documents.

C'est la seule structure à partir de laquelle toutes les pages
(mkdocs.yml, docs/index.md, docs/notions/*.md) sont générées.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from .typographie import construire_slug, construire_titre


class TypeDocument(StrEnum):
    """Les cinq types de documents qu'une notion peut publier."""

    COURS = "cours"
    TD = "td"
    CORRIGE = "corrige"
    AUTOMATISMES = "automatismes"
    MINITEST = "minitest"


# Libellé affiché aux élèves pour chaque type de document.
LIBELLES: dict[TypeDocument, str] = {
    TypeDocument.COURS: "Cours",
    TypeDocument.TD: "TD",
    TypeDocument.CORRIGE: "Corrigé",
    TypeDocument.AUTOMATISMES: "Automatismes",
    TypeDocument.MINITEST: "Mini-test",
}

# Sous-dossier de docs/ où chaque type de document est publié.
DOSSIERS_PUBLICATION: dict[TypeDocument, str] = {
    TypeDocument.COURS: "cours",
    TypeDocument.TD: "td",
    TypeDocument.CORRIGE: "corriges",
    TypeDocument.AUTOMATISMES: "automatismes",
    TypeDocument.MINITEST: "automatismes",
}

# Ordre d'affichage des documents sur une page de notion.
ORDRE_AFFICHAGE: dict[TypeDocument, int] = {
    TypeDocument.COURS: 0,
    TypeDocument.TD: 1,
    TypeDocument.AUTOMATISMES: 2,
    TypeDocument.MINITEST: 3,
    TypeDocument.CORRIGE: 4,
}


@dataclass(frozen=True)
class Document:
    """Un PDF source associé à une notion et à un type de document."""

    type: TypeDocument
    source: Path

    @property
    def destination(self) -> Path:
        """Nom de fichier publié dans docs/ (identique au nom source)."""
        return Path(DOSSIERS_PUBLICATION[self.type]) / self.source.name


@dataclass
class Notion:
    """Une notion Nxx, scannée depuis un dossier "Version en cours"."""

    numero: str  # "N06"
    nom_machine: str  # "SECOND_DEGRE_II"
    dossier: Path
    documents: dict[TypeDocument, list[Document]] = field(default_factory=dict)
    pdf_non_reconnus: list[Path] = field(default_factory=list)

    @property
    def slug(self) -> str:
        return construire_slug(self.nom_machine)

    @property
    def titre(self) -> str:
        return construire_titre(self.nom_machine)

    @property
    def nom_fichier_page(self) -> str:
        """Nom du fichier docs/notions/Nxx-slug.md attendu pour cette notion."""
        return f"{self.numero}-{self.slug}.md"

    def documents_du_type(self, type_document: TypeDocument) -> list[Document]:
        return self.documents.get(type_document, [])

    def types_presents(self) -> set[TypeDocument]:
        return {
            type_document
            for type_document, docs in self.documents.items()
            if docs
        }

    def types_absents(self) -> list[TypeDocument]:
        return [
            type_document
            for type_document in TypeDocument
            if type_document not in self.types_presents()
        ]

    def est_complete(self) -> bool:
        return not self.types_absents()

    def tous_les_documents(self) -> list[Document]:
        return [
            document
            for docs in self.documents.values()
            for document in docs
        ]
