#!/usr/bin/env python3
"""Synchroniser le site depuis "Version en cours" (idempotent).

    python scripts/synchroniser.py [--config CHEMIN]

Étapes : scan des notions -> génération (PDF, pages, index, nav) ->
rapport de cohérence. Ne construit pas le site (voir scripts/publier.py).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from synchronisation.config import charger_configuration
from synchronisation.generateur import RapportGeneration, generer_site
from synchronisation.scanner import scanner_notions
from synchronisation.verification import formater_rapport, verifier

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PAR_DEFAUT = PROJECT_ROOT / "config_site.yaml"


def afficher_rapport_generation(rapport: RapportGeneration) -> None:
    print(f"PDF copiés         : {len(rapport.pdf_copies)}")
    for chemin in rapport.pdf_copies:
        print(f"  - {chemin.relative_to(PROJECT_ROOT)}")
    print(f"PDF déjà à jour    : {len(rapport.pdf_inchanges)}")

    print(f"Pages créées       : {len(rapport.pages_creees)}")
    for chemin in rapport.pages_creees:
        print(f"  - {chemin.relative_to(PROJECT_ROOT)}")

    print(f"Pages renommées    : {len(rapport.pages_renommees)}")
    for ancien, nouveau in rapport.pages_renommees:
        print(f"  - {ancien.name} -> {nouveau.name}")

    print(f"Pages mises à jour : {len(rapport.pages_modifiees)}")
    for chemin in rapport.pages_modifiees:
        print(f"  - {chemin.relative_to(PROJECT_ROOT)}")

    if rapport.avertissements:
        print(f"Avertissements     : {len(rapport.avertissements)}")
        for avertissement in rapport.avertissements:
            print(f"  - {avertissement}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=CONFIG_PAR_DEFAUT,
        help="chemin du fichier config_site.yaml (défaut : racine du projet)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config = charger_configuration(args.config)
        print(f"Niveau      : {config.niveau}")
        print(f"Source      : {config.source}")
        print(f"Destination : {config.destination}")

        notions = scanner_notions(config)
        print(f"\n{len(notions)} notion(s) détectée(s) dans la source.\n")

        rapport_generation = generer_site(config, notions)
        afficher_rapport_generation(rapport_generation)

        rapport_verification = verifier(notions)
        print()
        print(formater_rapport(rapport_verification, config.niveau))
    except (FileNotFoundError, ValueError, OSError) as erreur:
        print(f"\nERREUR : {erreur}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
