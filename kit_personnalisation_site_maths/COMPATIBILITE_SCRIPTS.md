# Compatibilité avec les scripts de publication

Objectif : personnaliser le site sans casser la chaîne existante.

## Ce qui est modifié

- `docs/index.md` : page d'accueil plus visuelle.
- `docs/stylesheets/extra.css` : style graphique.
- `docs/assets/images/logo_lycee_franklin.png` : logo du lycée.
- `mkdocs.yml` : ajout d'un logo et du fichier CSS.

## Ce qui ne doit pas être modifié

- `scripts/publier.py`
- `scripts/synchroniser.py`
- `scripts/publier_ressources_site.py`
- `scripts/publier_ressources_gui.py`
- les zones `<!-- AUTO-DOCS:START -->` et `<!-- AUTO-DOCS:END -->` dans les pages de notions.

## Pourquoi cela reste compatible

La personnalisation agit seulement sur l'affichage. Les scripts continuent à :

1. synchroniser les notions ;
2. copier les PDF dans `docs/cours`, `docs/td`, `docs/corriges`, `docs/automatismes`, `docs/ds` ;
3. mettre à jour la section `## Accès rapide` de la page d'accueil ;
4. construire le site avec MkDocs ;
5. déployer sur GitHub Pages si l'option `--deploy` est utilisée.
