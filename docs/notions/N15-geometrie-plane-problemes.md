---
title: "Géométrie plane : problèmes et méthodes"
description: Cours et exercices de Seconde pour résoudre des problèmes avec Pythagore, Thalès, trigonométrie, vecteurs et droites.
---

# N15 — Géométrie plane : problèmes et méthodes

Les problèmes de géométrie plane demandent souvent de choisir entre plusieurs outils. Les ressources mobilisent Pythagore, Thalès, la trigonométrie, les vecteurs, les droites et parfois les fonctions. L’enjeu est d’identifier la méthode pertinente, d’organiser les calculs et de justifier les étapes.

<!-- NOTION-NAV:START -->
<nav class="notion-nav" aria-label="Navigation entre notions">
<a class="notion-nav__btn notion-nav__btn--prev" href="../N14-synthese-fonctions-modelisation/"><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M16 6v12L6 12z" fill="currentColor"/></svg></span><span class="notion-nav__text"><small>Notion précédente</small><span class="notion-nav__title">N14 — Synthèse fonctions et modélisation</span></span></a>
<a class="notion-nav__btn notion-nav__btn--next" href="../N16-information-chiffree-statistiques/"><span class="notion-nav__text"><small>Notion suivante</small><span class="notion-nav__title">N16 — Information chiffrée et statistiques</span></span><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M8 6v12l10-6z" fill="currentColor"/></svg></span></a>
</nav>
<!-- NOTION-NAV:END -->

## Objectifs

!!! objectifs ""

    - Choisir une méthode de géométrie plane adaptée.
    - Utiliser Pythagore, Thalès ou la trigonométrie.
    - Combiner vecteurs, droites et fonctions.

## Documents

<!-- AUTO-DOCS:START -->
- [Cours N15 — Géométrie plane : problèmes et méthodes](../cours/COURS_N15_GEOMETRIE_PLANE_PROBLEMES.pdf)
- [TD N15 — Géométrie plane : problèmes et méthodes](../td/TD_N15_GEOMETRIE_PLANE_PROBLEMES.pdf)
- [Automatismes N15 — Géométrie plane : problèmes et méthodes](../automatismes/AUTOMATISMES_N15_GEOMETRIE_PLANE_PROBLEMES.pdf)
<!-- AUTO-DOCS:END -->

## Notions essentielles

!!! essentiel ""

    Le projeté orthogonal d'un point `A` sur une droite `(d)` est le point `H` de `(d)` tel que `AH ⊥ (d)`. Il vérifie une propriété importante : pour tout point `M` de `(d)`, `AM ≥ AH`, avec égalité seulement lorsque `M = H`. Cette propriété se démontre grâce à Pythagore, dans le triangle `AHM` rectangle en `H`.

    Un même problème de géométrie peut se résoudre par plusieurs voies : géométrie classique (Pythagore, Thalès, trigonométrie), géométrie repérée (coordonnées, distances, milieux), vecteurs (colinéarité, alignement, parallélisme) ou fonctions (aire, longueur ou coût dépendant d'une variable). Repérer les indices de l'énoncé aide à choisir la méthode la plus efficace.

    Optimiser une grandeur géométrique, c'est chercher sa valeur maximale ou minimale en respectant les contraintes du problème. La méthode suit toujours les mêmes étapes : faire une figure et nommer la variable, déterminer l'intervalle des valeurs possibles, exprimer la grandeur à optimiser en fonction de la variable, étudier ses variations, puis conclure dans le contexte.

## Exemple

!!! exemple ""

    On veut construire un rectangle de périmètre 20 cm. Si une dimension vaut `x`, l'autre vaut `10 - x`, avec `0 < x < 10`. L'aire est `A(x) = x(10 - x)`.

    Le tableau de variations de `A` montre un maximum égal à 25 pour `x = 5` : le rectangle d'aire maximale est donc le carré de côté 5 cm.

## Repère historique — Ératosthène : mesurer loin grâce aux angles

!!! historique ""

    Ératosthène, Alexandrie, IIIe siècle avant notre ère
    {: .frise data-annee="-240" data-etiquette="IIIe s. av. J.-C." }

    Au IIIe siècle avant notre ère, Ératosthène estime la circonférence terrestre en comparant la direction du Soleil à Syène et à Alexandrie. Son ouvrage est perdu ; sa méthode nous est connue par des auteurs postérieurs. Le raisonnement suppose une Terre sphérique et des rayons solaires pratiquement parallèles. L’angle observé grâce à une ombre permet alors de retrouver un angle au centre de la Terre.

    Dans une reconstitution scolaire simplifiée, on suppose deux villes sur un même méridien, séparées par un arc de 800 km, et un angle au centre de `7,2°`. Cet angle vaut `360°/50` : l’arc représente donc un cinquantième du tour, d’où une circonférence estimée à `50 × 800 = 40 000 km`. Ces données modernes arrondies illustrent la méthode, sans être les mesures exactes d’Ératosthène. La longueur de l’unité antique, le stade, reste d’ailleurs discutée. L’exemple montre comment parallélisme, angles et proportionnalité permettent de calculer une distance inaccessible, à condition d’expliciter les hypothèses et la précision des données.

    Source : [MacTutor, université de St Andrews, biographie d’Ératosthène](https://mathshistory.st-andrews.ac.uk/Biographies/Eratosthenes/).

## Voir aussi

- PRÉREQUIS : [N07](N07-vecteurs-du-plan.md) (Les vecteurs peuvent servir dans les configurations.)
- PRÉREQUIS : [N08](N08-droites-equations.md) (Les droites interviennent dans les problèmes.)
