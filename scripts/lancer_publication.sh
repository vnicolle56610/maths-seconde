#!/usr/bin/env bash
# Lance la synchronisation + le build du site, quel que soit le dossier
# depuis lequel on l'appelle.
#
#   ./scripts/lancer_publication.sh              synchronise + mkdocs build
#   ./scripts/lancer_publication.sh --deploy     + publication GitHub Pages
#   ./scripts/lancer_publication.sh --sync-only  synchronise sans build
#   ./scripts/lancer_publication.sh --gui        interface graphique de sélection des PDF
#
# --sync-only, le mode par défaut et --deploy ne publient automatiquement
# que les COURS et TD (déjà relus). Les automatismes, mini-tests, corrigés
# et DS nouveaux ou modifiés doivent être relus et publiés via --gui.
#
# --deploy vérifie d'abord que le dépôt local est propre et synchronisé
# avec origin/main (même garde-fou que le bouton « Déployer » du GUI) :
# s'il y a du nouveau contenu à synchroniser, ce premier lancement va
# l'écrire sans le publier — il faut le relire, le committer, puis
# relancer --deploy.

set -euo pipefail

RACINE_PROJET="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RACINE_PROJET"

if [[ -f ".venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source ".venv/bin/activate"
fi

MODE="${1:-}"

if [[ "$MODE" == "--gui" ]]; then
    exec python3 scripts/publier_ressources_gui.py
fi

if [[ -n "$MODE" && "$MODE" != "--sync-only" && "$MODE" != "--deploy" ]]; then
    echo "Option inconnue : $MODE" >&2
    echo "Options disponibles : --gui, --sync-only, --deploy (ou aucune)." >&2
    exit 1
fi

python3 scripts/publier_ressources_site.py --non-interactive

if [[ "$MODE" == "--sync-only" ]]; then
    exit 0
fi

mkdocs build

if [[ "$MODE" != "--deploy" ]]; then
    exit 0
fi

echo
echo "=== Pré-vol Git avant publication GitHub Pages ==="
if ! python3 - <<'PYEOF'
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from publier_ressources_gui import check_deploy_preflight

result = check_deploy_preflight(Path.cwd())
print(result.user_message)
if not result.ok:
    print()
    print(result.details)
sys.exit(0 if result.ok else 1)
PYEOF
then
    exit 1
fi

SITE_TMP="$(mktemp -d -t "$(basename "$RACINE_PROJET")-gh-pages-XXXXXX")"
trap 'rm -rf "$SITE_TMP"' EXIT

echo
echo "=== Publication GitHub Pages (mkdocs gh-deploy) ==="
mkdocs gh-deploy --strict --force --site-dir "$SITE_TMP"
