---
title: Vecteurs du plan
description: Cours et exercices de Seconde sur les vecteurs, coordonnées, normes, milieux, déterminant et alignement.
---

# N07 — Vecteurs du plan

<!-- NOTION-NAV:START -->
<nav class="notion-nav" aria-label="Navigation entre notions">
<a class="notion-nav__btn notion-nav__btn--prev" href="../N06-synthese-nombres-calculs/"><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M16 6v12L6 12z" fill="currentColor"/></svg></span><span class="notion-nav__text"><small>Notion précédente</small><span class="notion-nav__title">N06 — Synthèse nombres et calculs</span></span></a>
<a class="notion-nav__btn notion-nav__btn--next" href="../N08-droites-equations/"><span class="notion-nav__text"><small>Notion suivante</small><span class="notion-nav__title">N08 — Droites et équations dans le plan</span></span><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M8 6v12l10-6z" fill="currentColor"/></svg></span></a>
</nav>
<!-- NOTION-NAV:END -->

Un vecteur code un déplacement et permet de calculer dans le plan. Les ressources portent sur les coordonnées, les normes, les milieux et le déterminant, avec des applications à l’alignement. Cette approche prépare l’étude des droites et donne une méthode de preuve dans un repère.

## Objectifs

- Calculer les coordonnées d’un vecteur.
- Utiliser normes et milieux.
- Prouver un alignement avec le déterminant.

## Documents

<!-- AUTO-DOCS:START -->
- [Cours N07 — Vecteurs du plan](../cours/COURS_N07_VECTEURS_DU_PLAN.pdf)
- [TD N07 — Vecteurs du plan](../td/TD_N07_VECTEURS_DU_PLAN.pdf)
- [Automatismes N07 — Vecteurs du plan](../automatismes/AUTOMATISMES_N07_VECTEURS_DU_PLAN.pdf)
<!-- AUTO-DOCS:END -->

## Notions essentielles

Un vecteur représente un déplacement : il possède une direction, un sens et une longueur appelée norme.

Deux vecteurs sont égaux lorsqu'ils décrivent le même déplacement. Le point de départ choisi pour les représenter n'est pas ce qui compte.

Dans un repère, les coordonnées de `AB` se calculent en faisant arrivée moins départ : abscisse de `B` moins abscisse de `A`, puis ordonnée de `B` moins ordonnée de `A`.

La norme d'un vecteur donne une distance. Les coordonnées du milieu d'un segment se calculent en faisant la moyenne des coordonnées des extrémités.

Deux vecteurs colinéaires ont la même direction. On peut tester la colinéarité avec la proportionnalité des coordonnées ou avec un déterminant nul. Cela sert à prouver des alignements ou des parallélismes.

## Exemple

Si `A(1 ; 2)` et `B(4 ; -1)`, alors le vecteur `AB` a pour coordonnées `(4 - 1 ; -1 - 2)`, donc `(3 ; -3)`.

Ce vecteur indique que l'on avance de 3 unités horizontalement et que l'on descend de 3 unités verticalement.

## Voir aussi

- PROLONGEMENT : [N08](N08-droites-equations.md) (Les droites utilisent directions et déterminants.)
