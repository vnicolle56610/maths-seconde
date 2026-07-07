"""Rapport de cohérence : quels documents manquent pour chaque notion."""

from __future__ import annotations

from dataclasses import dataclass

from .notion import LIBELLES, Notion


@dataclass(frozen=True)
class RapportNotion:
    notion: Notion
    types_absents: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.types_absents


@dataclass(frozen=True)
class RapportGlobal:
    rapports: tuple[RapportNotion, ...]

    @property
    def nombre_completes(self) -> int:
        return sum(1 for rapport in self.rapports if rapport.complete)

    @property
    def nombre_incompletes(self) -> int:
        return len(self.rapports) - self.nombre_completes

    @property
    def nombre_pdf_non_reconnus(self) -> int:
        return sum(len(rapport.notion.pdf_non_reconnus) for rapport in self.rapports)


def verifier(notions: list[Notion]) -> RapportGlobal:
    rapports = tuple(
        RapportNotion(
            notion=notion,
            types_absents=tuple(
                LIBELLES[type_document] for type_document in notion.types_absents()
            ),
        )
        for notion in notions
    )
    return RapportGlobal(rapports=rapports)


def formater_rapport(rapport: RapportGlobal, niveau: str) -> str:
    """Construire le texte du rapport (glyphes ✓ / ⚠ requis)."""
    lignes = [f"=== Rapport de cohérence — {niveau} ==="]
    for rapport_notion in rapport.rapports:
        notion = rapport_notion.notion
        if rapport_notion.complete:
            lignes.append(f"✓ {notion.numero} — {notion.titre}")
        else:
            lignes.append(f"⚠ {notion.numero} — {notion.titre}")
            for manquant in rapport_notion.types_absents:
                lignes.append(f"    {manquant.lower()} absent")

    lignes.append("")
    lignes.append(
        f"{rapport.nombre_completes} notion(s) complète(s), "
        f"{rapport.nombre_incompletes} incomplète(s) "
        f"sur {len(rapport.rapports)}."
    )

    if rapport.nombre_pdf_non_reconnus:
        lignes.append("")
        lignes.append(
            f"⚠ {rapport.nombre_pdf_non_reconnus} PDF au nom non reconnu "
            "(ignoré·s, jamais publiés) :"
        )
        for rapport_notion in rapport.rapports:
            for chemin in rapport_notion.notion.pdf_non_reconnus:
                lignes.append(
                    f"    {rapport_notion.notion.numero} — "
                    f"{chemin.parent.name}/{chemin.name}"
                )
        lignes.append(
            "  -> renommez ces fichiers selon la convention "
            "TYPE_Nxx_NOM.pdf (COURS_, TD_, CORRIGE_TD_, AUTOMATISMES_, "
            "MINITEST_) pour qu'ils soient pris en compte."
        )

    return "\n".join(lignes)
