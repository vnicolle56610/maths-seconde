"""Chargement de la configuration du site depuis ``config_site.yaml``."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class SiteConfig:
    """Paramètres nécessaires pour synchroniser un site MkDocs.

    Ce même code doit fonctionner pour Seconde, Première, Terminale ou
    Maths expertes : seul le contenu de ``config_site.yaml`` change.
    """

    source: Path
    destination: Path
    niveau: str

    @property
    def docs(self) -> Path:
        return self.destination / "docs"

    @property
    def mkdocs_yml(self) -> Path:
        return self.destination / "mkdocs.yml"


def charger_configuration(chemin_config: Path) -> SiteConfig:
    """Lire un fichier ``config_site.yaml`` et résoudre les chemins.

    ``destination`` est résolu relativement au dossier contenant le
    fichier de configuration, afin qu'un simple "." désigne toujours la
    racine du site courant.
    """
    if not chemin_config.is_file():
        raise FileNotFoundError(
            f"Fichier de configuration introuvable : {chemin_config}"
        )

    donnees = yaml.safe_load(chemin_config.read_text(encoding="utf-8")) or {}

    for cle in ("source", "destination", "niveau"):
        if cle not in donnees:
            raise ValueError(
                f"Clé « {cle} » manquante dans {chemin_config}"
            )

    dossier_config = chemin_config.resolve().parent
    source = Path(donnees["source"]).expanduser().resolve()
    destination = (dossier_config / Path(donnees["destination"]).expanduser()).resolve()

    return SiteConfig(
        source=source,
        destination=destination,
        niveau=str(donnees["niveau"]),
    )
