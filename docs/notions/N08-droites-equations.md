---
title: Droites et équations dans le plan
description: Cours et exercices de Seconde pour décrire une droite par une direction, construire ses équations et étudier positions relatives.
---

# N08 — Droites et équations dans le plan

Une droite peut être décrite par un point, une direction, une pente ou une équation. Les documents travaillent l’équation cartésienne avec le déterminant, le passage à l’équation réduite et l’étude d’alignements, de parallélismes ou d’intersections. Le périmètre reste strictement géométrique et analytique autour des droites du plan.

<!-- NOTION-NAV:START -->
<nav class="notion-nav" aria-label="Navigation entre notions">
<a class="notion-nav__btn notion-nav__btn--prev" href="../N07-vecteurs-du-plan/"><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M16 6v12L6 12z" fill="currentColor"/></svg></span><span class="notion-nav__text"><small>Notion précédente</small><span class="notion-nav__title">N07 — Vecteurs du plan</span></span></a>
<a class="notion-nav__btn notion-nav__btn--next" href="../N09-fonctions-registres/"><span class="notion-nav__text"><small>Notion suivante</small><span class="notion-nav__title">N09 — Fonctions : images, antécédents et registres</span></span><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M8 6v12l10-6z" fill="currentColor"/></svg></span></a>
</nav>
<!-- NOTION-NAV:END -->

## Objectifs

!!! objectifs ""

    - Décrire une droite par un point et une direction.
    - Construire une équation cartésienne ou réduite.
    - Étudier alignement, parallélisme et intersections.

## Documents

<!-- AUTO-DOCS:START -->
- [Cours N08 — Droites et équations dans le plan](../cours/COURS_N08_DROITES_DU_PLAN.pdf)
- [TD N08 — Droites et équations dans le plan](../td/TD_N08_DROITES_DU_PLAN.pdf)
<!-- AUTO-DOCS:END -->

<!-- AUTOMATISMES-WEB:START -->
- ⚡ [Automatismes N08 en ligne : énoncés, corrigés et QCM interactif](../automatismes/automatismes-N08-droites-equations.md)
<!-- AUTOMATISMES-WEB:END -->

## Notions essentielles

!!! essentiel ""

    Une droite peut être décrite par un point et un vecteur directeur non nul. Le vecteur directeur donne la direction de la droite.

    Une équation cartésienne de droite s'écrit sous la forme `ax + by + c = 0`, avec `a` et `b` qui ne sont pas tous les deux nuls.

    Lorsqu'une droite n'est pas verticale, elle peut aussi s'écrire sous forme réduite `y = mx + p`. Le nombre `m` est le coefficient directeur, ou pente, et `p` est l'ordonnée à l'origine.

    Une droite verticale s'écrit sous la forme `x = k` et n'a pas de coefficient directeur.

    Pour étudier deux droites, on choisit l'outil adapté : comparer des directions pour le parallélisme, résoudre un système pour une intersection, ou vérifier qu'un point satisfait une équation.

## Exemple

!!! exemple ""

    La droite d'équation `y = 2x - 1` a pour coefficient directeur 2 et pour ordonnée à l'origine -1.

    Le point `A(3 ; 5)` appartient à cette droite car `2 × 3 - 1 = 5`.

## Repère historique — Descartes : reconnaître un lieu grâce à une équation

!!! historique ""

    René Descartes, *La Géométrie*, 1637
    {: .frise data-annee="1637" }

    Dans *La Géométrie*, publiée en 1637, René Descartes développe une méthode qui traduit des relations entre longueurs en équations. Un problème de lieu géométrique consiste à chercher tous les points satisfaisant une condition : le calcul peut alors aider à reconnaître la courbe obtenue. Cette articulation entre algèbre et géométrie est une étape majeure de la géométrie analytique ; elle ne se présente toutefois pas encore sous la forme exacte de nos repères scolaires et de notre langage vectoriel.

    Prenons un exemple moderne : on cherche les points `M(x ; y)` équidistants de `A(0 ; 0)` et de `B(4 ; 0)`. Dans un repère orthonormé, l’égalité des carrés des distances s’écrit `x² + y² = (x − 4)² + y²`. Après développement et réduction, elle devient `x = 2`. On reconnaît la médiatrice de `[AB]`, une droite verticale. Cet exemple montre pourquoi l’équation cartésienne est utile : certaines droites se décrivent très simplement, même lorsqu’aucune écriture `y = mx + p` n’est possible.

    Source : [Stanford Encyclopedia of Philosophy, *Descartes’ Mathematics*](https://plato.stanford.edu/entries/descartes-mathematics/).

## Voir aussi

- PRÉREQUIS : [N07](N07-vecteurs-du-plan.md) (Les vecteurs donnent les directions et le déterminant.)
