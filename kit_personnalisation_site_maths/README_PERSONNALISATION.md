# Kit de personnalisation — sites de maths MkDocs

Ce kit ajoute une page d'accueil personnalisée et un habillage graphique léger pour les sites :

- `maths-seconde`
- `maths-premiere-specialite`

Il ne modifie pas les scripts Python de synchronisation, publication ou déploiement.

## Fichiers fournis

```text
docs/assets/images/logo_lycee_franklin.png
docs/stylesheets/extra.css
docs/index_seconde.md
docs/index_premiere.md
mkdocs_fragment.yml
```

## Installation recommandée

Depuis la racine du projet concerné :

```bash
mkdir -p docs/assets/images docs/stylesheets
cp /chemin/du/kit/docs/assets/images/logo_lycee_franklin.png docs/assets/images/
cp /chemin/du/kit/docs/stylesheets/extra.css docs/stylesheets/
```

Pour le site de Seconde :

```bash
cp /chemin/du/kit/docs/index_seconde.md docs/index.md
```

Pour le site de Première spécialité :

```bash
cp /chemin/du/kit/docs/index_premiere.md docs/index.md
```

Puis ajouter dans `mkdocs.yml`, si ce n'est pas déjà présent :

```yaml
extra_css:
  - stylesheets/extra.css
```

Et, dans le bloc `theme`, ajouter ou compléter :

```yaml
logo: assets/images/logo_lycee_franklin.png
favicon: assets/images/logo_lycee_franklin.png
```

## Point important pour tes scripts

Ne supprime pas le titre suivant dans `docs/index.md` :

```markdown
## Accès rapide
```

Les scripts s'en servent pour compléter la page d'accueil avec les liens vers les pages de notions.

## Test après installation

```bash
python scripts/publier.py
mkdocs serve
```

Puis, si tout est bon :

```bash
python scripts/publier.py --deploy
```
