---
title: Information chiffrée et statistiques
description: Cours et exercices de Seconde pour choisir une population de référence, calculer une évolution et interpréter des indicateurs statistiques.
---

# N16 — Information chiffrée et statistiques

L’information chiffrée demande de savoir ce que l’on mesure et par rapport à quelle population. Les ressources font travailler les évolutions, les pourcentages et les indicateurs statistiques. Le point important est de relier le calcul à une interprétation fiable des données.

## Objectifs

- Choisir la bonne population de référence.
- Calculer une évolution.
- Interpréter un indicateur statistique.

<!-- NOTION-NAV:START -->
<nav class="notion-nav" aria-label="Navigation entre notions">
<a class="notion-nav__btn notion-nav__btn--prev" href="../N15-geometrie-plane-problemes/"><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M16 6v12L6 12z" fill="currentColor"/></svg></span><span class="notion-nav__text"><small>Notion précédente</small><span class="notion-nav__title">N15 — Géométrie plane : problèmes et méthodes</span></span></a>
<a class="notion-nav__btn notion-nav__btn--next" href="../N17-croisement-variables-qualitatives/"><span class="notion-nav__text"><small>Notion suivante</small><span class="notion-nav__title">N17 — Tableaux croisés et variables qualitatives</span></span><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M8 6v12l10-6z" fill="currentColor"/></svg></span></a>
</nav>
<!-- NOTION-NAV:END -->

## Objectifs

- Choisir la bonne population de référence.
- Calculer une évolution.
- Interpréter un indicateur statistique.

## Documents

<!-- AUTO-DOCS:START -->
- [Cours N16 — Information chiffrée et statistiques](../cours/COURS_N16_INFORMATION_CHIFFREE_STATISTIQUES.pdf)
- [TD N16 — Information chiffrée et statistiques](../td/TD_N16_INFORMATION_CHIFFREE_STATISTIQUES.pdf)
- [Automatismes N16 — Information chiffrée et statistiques](../automatismes/AUTOMATISMES_N16_INFORMATION_CHIFFREE_STATISTIQUES.pdf)
<!-- AUTO-DOCS:END -->

## Notions essentielles

Un pourcentage n'a de sens que rapporté à son ensemble de référence : si `A` représente une proportion `p` de `E`, et `B` une proportion `q` de `A`, alors `B` représente une proportion `p × q` de `E`.

Pour une évolution de `V1` vers `V2`, le coefficient multiplicateur est `V2/V1` et le taux d'évolution est `(V2-V1)/V1`. Augmenter de `t %`, c'est multiplier par `1 + t/100` ; diminuer de `t %`, c'est multiplier par `1 - t/100`. Pour des évolutions successives, on multiplie les coefficients multiplicateurs ; l'évolution réciproque a pour coefficient l'inverse.

La moyenne, la médiane, les quartiles, l'étendue et l'écart type ne décrivent pas la même information : la moyenne résume un niveau moyen (elle est sensible aux valeurs extrêmes), la médiane partage la série ordonnée en deux groupes de même effectif (elle y est beaucoup moins sensible), les quartiles encadrent la moitié centrale, l'étendue mesure l'amplitude totale, et l'écart type mesure la dispersion autour de la moyenne. Pour une série regroupée en classes, on estime souvent la moyenne en remplaçant chaque classe par son centre.

Comparer deux séries exige au moins un indicateur de position et un indicateur de dispersion, et une conclusion rédigée avec prudence.

## Exemple

Un prix augmente de 12 %, puis baisse de 10 %. Le coefficient multiplicateur global est `1,12 × 0,90 = 1,008` : le prix final est donc `0,8 %` plus élevé que le prix initial, malgré l'apparente compensation des deux pourcentages.

## Voir aussi

- PROLONGEMENT : [N17](N17-croisement-variables-qualitatives.md) (Les tableaux croisés prolongent l’analyse de données.)
