#!/usr/bin/env python3
"""Commande unique de publication du site.

    python scripts/publier.py             # synchronise + build
    python scripts/publier.py --deploy     # + push GitHub Pages (gh-deploy)

Étapes : synchronisation -> vérification -> génération -> mkdocs build
-> (optionnel) publication GitHub Pages.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import synchroniser
from synchronisation.config import charger_configuration
from synchronisation.publication import construire_site, publier_github_pages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=synchroniser.CONFIG_PAR_DEFAUT,
        help="chemin du fichier config_site.yaml (défaut : racine du projet)",
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="publier sur GitHub Pages après le build (mkdocs gh-deploy)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print("=== 1/3 : synchronisation ===")
    sys.argv = [sys.argv[0], "--config", str(args.config)]
    code_synchronisation = synchroniser.main()
    if code_synchronisation != 0:
        print("\nSynchronisation en échec, arrêt avant le build.")
        return code_synchronisation

    config = charger_configuration(args.config)

    print("\n=== 2/3 : mkdocs build ===")
    code_build = construire_site(config)
    if code_build != 0:
        print("\nÉchec de mkdocs build, arrêt avant publication.")
        return code_build

    if not args.deploy:
        print("\nTerminé (site construit dans docs/../site). "
              "Ajoutez --deploy pour publier sur GitHub Pages.")
        return 0

    print("\n=== 3/3 : publication GitHub Pages (mkdocs gh-deploy) ===")
    return publier_github_pages(config)


if __name__ == "__main__":
    raise SystemExit(main())
