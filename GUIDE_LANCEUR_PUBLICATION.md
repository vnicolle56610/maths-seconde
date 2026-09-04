# Guide d'utilisation — `lancer_publication.sh`

Ce script lance la synchronisation du site depuis le dépôt de référence
`~/ENSEIGNEMENT/IA_AGENT_MATHS/GPT-seconde`, construit le site MkDocs, et
peut le publier sur GitHub Pages.

## D'où le lancer

Le script se débrouille pour retrouver la racine du projet tout seul,
mais le plus simple est de toujours se placer dans le dossier du projet
avant de l'appeler :

```bash
cd ~/ENSEIGNEMENT/maths-seconde
./scripts/lancer_publication.sh
```

Il fonctionne aussi en donnant le chemin complet depuis n'importe où :

```bash
~/ENSEIGNEMENT/maths-seconde/scripts/lancer_publication.sh
```

⚠️ Attention à ne pas mettre le `~` avant `scripts` : `~scripts/...` n'est
pas un chemin valide. Le `~` doit toujours être suivi d'un `/`.

## Ouvrir l'interface graphique (cases à cocher)

**Sans argument, le lanceur n'ouvre PAS l'interface graphique** : il exécute
le pipeline automatique (synchronisation + build). Pour obtenir
l'interface avec les cases à cocher, il faut explicitement ajouter
`--gui` :

```bash
cd ~/ENSEIGNEMENT/maths-seconde
./scripts/lancer_publication.sh --gui
```

C'est la **seule** des quatre commandes qui ouvre une fenêtre. Les trois
autres (`--sync-only`, sans argument, `--deploy`) tournent entièrement
dans le terminal, sans aucune fenêtre.

## Les commandes disponibles

| Commande | Ce qu'elle fait |
|---|---|
| `./scripts/lancer_publication.sh --sync-only` | Scanne `GPT-seconde`, régénère les pages/nav/index, affiche le rapport ✓/⚠. **Ne construit pas le site, ne publie rien.** À utiliser pour vérifier ce qui a changé avant d'aller plus loin. |
| `./scripts/lancer_publication.sh` | Fait tout ce que fait `--sync-only`, puis lance `mkdocs build` (construit le site dans `site/`, en local). **Ne publie toujours rien en ligne.** |
| `./scripts/lancer_publication.sh --deploy` | Fait tout ce qui précède, **puis publie sur GitHub Pages** (`mkdocs gh-deploy`, qui pousse sur `origin`). C'est la seule commande qui rend les changements visibles sur `https://vnicolle56610.github.io/maths-seconde/`. |
| `./scripts/lancer_publication.sh --gui` | Ouvre l'ancienne interface graphique (`publier_ressources_gui.py`) avec les cases à cocher pour choisir précisément quels PDF publier. |

## Dans quel ordre travailler

1. **Vérifier d'abord sans rien publier** :
   ```bash
   ./scripts/lancer_publication.sh --sync-only
   ```
   Regarder le rapport : notions complètes (✓), documents manquants (⚠),
   pages créées/renommées/modifiées.

2. **Si le rapport est satisfaisant, publier en ligne** :
   ```bash
   ./scripts/lancer_publication.sh --deploy
   ```

3. **Après un déploiement**, si le site semble ne pas avoir changé dans le
   navigateur, faire un rechargement forcé avant de s'inquiéter :
   `Ctrl+Maj+R` (ou ouvrir la page en navigation privée). C'est
   généralement un cache du navigateur, pas un problème de publication.

## ⚠️ Ne pas alterner avec l'interface graphique sur les mêmes notions

Le pipeline automatique (`--sync-only`, sans argument, `--deploy`) republie
**tout** ce qu'il trouve dans `GPT-seconde`, sans notion de
sélection. L'interface graphique (`--gui`) permet au contraire de
**décocher** certains PDF pour ne pas les publier.

Si vous lancez le pipeline automatique après avoir décoché quelque chose
dans le GUI, il va **régénérer les pages depuis zéro** et donc annuler
silencieusement votre désélection.

Règle simple : pour une notion donnée, choisissez un seul des deux outils
et n'y revenez pas avec l'autre tant que le contenu source n'a pas changé.

## Prérequis

- Être dans un terminal Linux, avec `bash`.
- Un environnement virtuel Python dans `.venv/` (le script l'active tout
  seul s'il existe) contenant `mkdocs`, `mkdocs-material` et `pyyaml`.
- Le dépôt source `GPT-seconde` accessible au chemin indiqué dans
  `config_site.yaml` (à la racine du projet).

# Commande personnelle dans `~/bin`

Copie-colle ceci dans le terminal :

```bash
mkdir -p ~/bin

cat > ~/bin/lancer_publication_seconde <<'EOF'
#!/usr/bin/env bash
exec "$HOME/ENSEIGNEMENT/maths-seconde/scripts/lancer_publication.sh" --gui "$@"
EOF

chmod +x ~/bin/lancer_publication_seconde
```

Puis assure-toi que `~/bin` est bien dans le `PATH` :

```bash
grep -q 'export PATH="$HOME/bin:$PATH"' ~/.bashrc || echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Ensuite, depuis n'importe quel répertoire, tu pourras simplement écrire :

```bash
lancer_publication_seconde
```

Pour vérifier :

```bash
command -v lancer_publication_seconde
```

Tu devrais obtenir quelque chose comme :

```bash
/home/vincent/bin/lancer_publication_seconde
```

Il existe une commande symétrique `lancer_publication_premiere` pour le
site de Première spécialité (`~/ENSEIGNEMENT/maths-premiere-specialite`).
