# Guide d'utilisation — `lancer_publication.sh`

Ce script régénère le site depuis la source pédagogique configurée dans
`config_site.yaml` (`~/ENSEIGNEMENT/CLAUDE/Niveau_2nde`), construit le
site MkDocs, et peut le publier sur GitHub Pages.

**Modèle de l'outil : un état de publication, pas une sélection
temporaire.** `publication_manifest.json` (à la racine du projet, suivi
par Git) enregistre explicitement ce qui doit être publié. Le CLI
(`--sync-only`, sans argument, `--deploy`) ne fait que régénérer `docs/`
pour qu'il corresponde exactement à ce manifeste — il ne décide jamais
lui-même d'ajouter ou de retirer une ressource. Seul `--gui` permet de
cocher/décocher l'état final souhaité.

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
| `./scripts/lancer_publication.sh --sync-only` | Régénère `docs/` (copies de PDF, blocs AUTO-DOCS) pour qu'il corresponde exactement à `publication_manifest.json` — n'ajoute, ne retire jamais rien de lui-même. **Ne construit pas le site, ne publie rien.** À utiliser pour vérifier ce qui a changé avant d'aller plus loin. |
| `./scripts/lancer_publication.sh` | Fait tout ce que fait `--sync-only`, puis lance `mkdocs build` (construit le site dans `site/`, en local). **Ne publie toujours rien en ligne.** |
| `./scripts/lancer_publication.sh --deploy` | Fait tout ce qui précède, vérifie que le dépôt local est propre et strictement synchronisé avec `origin/main` (même garde-fou que le bouton « Déployer » du GUI), puis **publie sur GitHub Pages** (`mkdocs gh-deploy`, qui pousse sur `origin`). S'il y a du nouveau contenu à régénérer, ce premier lancement l'écrit sans le publier : il faut le relire, le committer, puis relancer `--deploy`. C'est la seule commande CLI qui rend les changements visibles sur `https://vnicolle56610.github.io/maths-seconde/`. |
| `./scripts/lancer_publication.sh --gui` | Ouvre l'interface graphique (`publier_ressources_gui.py`) : cases à cocher représentant l'état de publication final souhaité, prévisualisation en diff (ajouts/retraits), application avec commit automatique, puis boutons dédiés « Pousser vers GitHub » et « Déployer sur GitHub Pages ». Seul moyen de faire évoluer ce qui est publié (ajout ou retrait, tout type de document). |
| `./scripts/lancer_publication.sh --bootstrap-manifest` | Reconstruit `publication_manifest.json` depuis ce qui est déjà référencé dans les pages (blocs AUTO-DOCS). Opération de migration, à ne lancer qu'une fois (ou avec `--force` pour l'écraser volontairement) ; n'écrit jamais dans `docs/`. |

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

## Le pipeline automatique ne change jamais ce qui est publié

`--sync-only`, le mode par défaut et `--deploy` régénèrent `docs/`
strictement à l'identique de `publication_manifest.json`. Une ressource
absente de la source (`CLAUDE/Niveau_2nde`) mais toujours dans le
manifeste **reste publiée** — elle n'est jamais retirée silencieusement
parce qu'un fichier a disparu du dossier de travail. Seule une action
explicite dans le GUI (décocher, puis confirmer le retrait) peut faire
disparaître une ressource du catalogue.

Pour ajouter une nouveauté ou retirer quoi que ce soit, il faut donc
toujours passer par `--gui`.

## Prérequis

- Être dans un terminal Linux, avec `bash`.
- Un environnement virtuel Python dans `.venv/` (le script l'active tout
  seul s'il existe) contenant `mkdocs`, `mkdocs-material` et `pyyaml`.
- La source pédagogique accessible au chemin indiqué dans
  `config_site.yaml` (`CLAUDE/Niveau_2nde`, à la racine du projet).

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
