"""Construction et publication du site (mkdocs build / gh-deploy)."""

from __future__ import annotations

import subprocess

from .config import SiteConfig


def construire_site(config: SiteConfig) -> int:
    """Lancer ``mkdocs build``. Retourne le code de sortie."""
    resultat = subprocess.run(
        ["mkdocs", "build"],
        cwd=config.destination,
        check=False,
    )
    return resultat.returncode


def publier_github_pages(config: SiteConfig) -> int:
    """Lancer ``mkdocs gh-deploy`` (pousse la branche gh-pages sur origin).

    Action visible par d'autres et difficile à annuler : n'est jamais
    appelée automatiquement, seulement si l'utilisateur passe --deploy.
    """
    resultat = subprocess.run(
        ["mkdocs", "gh-deploy"],
        cwd=config.destination,
        check=False,
    )
    return resultat.returncode
