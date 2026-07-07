# Memo - restaurer les scripts de publication

Ce memo explique quoi faire si un fichier important de publication est efface
par accident dans le site Seconde.

Le site concerne :

```bash
~/ENSEIGNEMENT/maths-seconde
```

La commande habituelle de publication est :

```bash
lancer_publication_seconde
```

Elle utilise principalement :

```text
scripts/lancer_publication.sh
scripts/publier_ressources_gui.py
scripts/publier_ressources_site.py
scripts/synchronisation/config.py
scripts/synchronisation/__init__.py
```

Les anciens scripts non utilises au quotidien sont ranges dans :

```text
scripts_old/
```

## Regle importante

En cas d'effacement accidentel :

1. Ne pas paniquer.
2. Ne pas refaire un commit tout de suite.
3. Ne pas lancer de commande Git compliquee.
4. Commencer par regarder l'etat du dossier avec `git status`.

## Cas 1 - J'ai efface un fichier, mais je n'ai pas encore committe

C'est le cas le plus simple.

Ouvrir un terminal, puis taper :

```bash
cd ~/ENSEIGNEMENT/maths-seconde
git status
```

Si Git indique des fichiers supprimes dans `scripts/` ou `scripts_old/`, on peut
restaurer toute la zone des scripts avec :

```bash
git restore scripts scripts_old
```

Puis verifier :

```bash
git status --short -- scripts scripts_old
```

Si la commande ne renvoie rien, les scripts sont revenus comme dans le dernier
commit.

## Cas 2 - Je veux restaurer depuis le commit de sauvegarde saine

Le commit de sauvegarde des scripts est :

```text
fe70465 - Sauvegarder les scripts de publication utiles
```

Pour remettre `scripts/` et `scripts_old/` exactement comme dans ce commit :

```bash
cd ~/ENSEIGNEMENT/maths-seconde
git restore --source fe70465 -- scripts scripts_old
```

Puis verifier :

```bash
git status --short -- scripts scripts_old
```

Si des lignes apparaissent, cela signifie que Git a prepare des changements de
restauration. Il faut ensuite les verifier avant de les committer.

## Cas 3 - Le lanceur global a ete efface

Le fichier suivant n'est pas dans le depot Git du site :

```text
/home/vincent/bin/lancer_publication_seconde
```

S'il est efface, le recreer avec ces commandes :

```bash
mkdir -p ~/bin
cat > ~/bin/lancer_publication_seconde <<'EOF'
#!/usr/bin/env bash
exec "$HOME/ENSEIGNEMENT/maths-seconde/scripts/lancer_publication.sh" --gui "$@"
EOF
chmod +x ~/bin/lancer_publication_seconde
```

Puis verifier :

```bash
command -v lancer_publication_seconde
```

La reponse attendue est :

```text
/home/vincent/bin/lancer_publication_seconde
```

## Cas 4 - Je veux seulement verifier que les scripts se chargent

Sans lancer la publication graphique, on peut verifier que le moteur principal
charge la bonne configuration :

```bash
cd ~/ENSEIGNEMENT/maths-seconde
python3 -B -c "import sys; sys.path.insert(0, 'scripts'); import publier_ressources_site as p; print(p.NIVEAU)"
```

La reponse attendue est :

```text
Seconde
```

## Ce qu'il vaut mieux eviter

Ne pas utiliser ces commandes sans aide :

```bash
git reset --hard
git clean -fd
```

Elles peuvent effacer des changements non sauvegardes.

## Sauvegarde hors ordinateur

Un commit Git protege bien contre une suppression accidentelle dans le dossier.
Mais si l'ordinateur ou le disque tombe en panne, il faut aussi que les commits
soient pousses sur GitHub.

Pour voir si le depot contient des commits locaux non pousses :

```bash
cd ~/ENSEIGNEMENT/maths-seconde
git status --short --branch
```

Si la premiere ligne contient `ahead`, cela veut dire qu'il existe des commits
locaux qui ne sont pas encore sur GitHub.
