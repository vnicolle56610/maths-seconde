#!/usr/bin/env bash
# Lance la synchronisation + le build du site, quel que soit le dossier
# depuis lequel on l'appelle.
#
#   ./scripts/lancer_publication.sh              synchronise + mkdocs build
#   ./scripts/lancer_publication.sh --deploy     + publication GitHub Pages
#   ./scripts/lancer_publication.sh --sync-only  synchronise sans build
#   ./scripts/lancer_publication.sh --gui        interface graphique de sélection des PDF

set -euo pipefail

RACINE_PROJET="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RACINE_PROJET"

if [[ -f ".venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source ".venv/bin/activate"
fi

if [[ "${1:-}" == "--gui" ]]; then
    exec python3 scripts/publier_ressources_gui.py
fi

if [[ "${1:-}" == "--sync-only" ]]; then
    exec python3 scripts/synchroniser.py
fi

exec python3 scripts/publier.py "$@"
