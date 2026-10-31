---
title: Équations et inéquations avec fonctions
description: Cours et exercices de Seconde pour résoudre graphiquement ou par calcul des équations et inéquations faisant intervenir des fonctions.
---

# N13 — Équations et inéquations avec fonctions

Les équations et inéquations de fonctions se lisent sur une courbe ou se résolvent par le calcul. Les documents font comparer des images, utiliser des tableaux de signes et choisir entre lecture graphique et méthode algébrique. La conclusion doit préciser l’ensemble des solutions.

## Objectifs

!!! objectifs ""

    - Résoudre par lecture graphique.
    - Résoudre par calcul ou tableau de signes.
    - Choisir une méthode adaptée.

<!-- NOTION-NAV:START -->
<nav class="notion-nav" aria-label="Navigation entre notions">
<a class="notion-nav__btn notion-nav__btn--prev" href="../N12-variations-extremums/"><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M16 6v12L6 12z" fill="currentColor"/></svg></span><span class="notion-nav__text"><small>Notion précédente</small><span class="notion-nav__title">N12 — Variations et extremums</span></span></a>
<a class="notion-nav__btn notion-nav__btn--next" href="../N14-synthese-fonctions-modelisation/"><span class="notion-nav__text"><small>Notion suivante</small><span class="notion-nav__title">N14 — Synthèse fonctions et modélisation</span></span><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M8 6v12l10-6z" fill="currentColor"/></svg></span></a>
</nav>
<!-- NOTION-NAV:END -->

## Objectifs

!!! objectifs ""

    - Résoudre par lecture graphique.
    - Résoudre par calcul et tableau de signes.
    - Choisir la méthode adaptée.

## Documents

<!-- AUTO-DOCS:START -->
- [Cours N13 — Équations et inéquations avec fonctions](../cours/COURS_N13_EQUATIONS_INEQUATIONS_FONCTIONS.pdf)
- [TD N13 — Équations et inéquations avec fonctions](../td/TD_N13_EQUATIONS_INEQUATIONS_FONCTIONS.pdf)
- [Automatismes N13 — Équations et inéquations avec fonctions](../automatismes/AUTOMATISMES_N13_EQUATIONS_INEQUATIONS_FONCTIONS.pdf)
<!-- AUTO-DOCS:END -->

## Notions essentielles

!!! essentiel ""

    Résoudre `f(x) = g(x)`, c'est chercher toutes les abscisses `x` pour lesquelles les deux fonctions ont la même image. Graphiquement, ce sont les abscisses des points d'intersection des courbes. Trois méthodes sont possibles : une lecture graphique (vue globale, valeur parfois approchée), une résolution algébrique (transformer en `f(x) - g(x) = 0` puis factoriser) ou une méthode numérique (table de valeurs, encadrement) lorsqu'aucune valeur exacte simple n'est accessible.

    Le signe d'un produit se déduit du signe de ses facteurs, et ses zéros sont les zéros des facteurs. Pour résoudre une inéquation avec un produit, on factorise, on repère et on ordonne les zéros, puis on construit un tableau de signes.

    Un quotient `A(x)/B(x)` n'est défini que si `B(x) ≠ 0` : toute valeur qui annule le dénominateur est une valeur interdite et n'appartient jamais à l'ensemble des solutions, même si elle apparaît comme une borne naturelle du tableau.

    Résoudre `f(x) > g(x)` revient à résoudre `f(x) - g(x) > 0` : graphiquement, on repère où la courbe de `f` est au-dessus de celle de `g` ; algébriquement, on étudie le signe de `f - g`.

## Exemple

!!! exemple ""

    Pour résoudre `(x-1)/(x+2) ≤ 0`, on commence par le domaine : `x = -2` est une valeur interdite. Le numérateur s'annule en `x = 1`.

    Le tableau de signes donne `S = ]-2 ; 1]` : l'intervalle contient `1`, où le quotient est nul, mais exclut `-2`, valeur interdite.

## Repère historique — Khayyam : résoudre en faisant se rencontrer des courbes

!!! historique ""

    Omar Khayyam, XIe siècle
    {: .frise data-annee="1070" data-etiquette="XIe s." }

    Au XIe siècle, Omar Khayyam étudie des équations du troisième degré et organise leur résolution géométrique à l’aide d’intersections de coniques, comme les cercles et les paraboles. Le point commun à deux courbes permet d’obtenir une longueur recherchée. Il ne travaille pas avec notre notation de fonctions ni avec un simple tracé approximatif : ses constructions s’appuient sur des relations géométriques démontrées.

    Une illustration moderne plus simple, adaptée à la Seconde, consiste à comparer `f(x) = x²` et `g(x) = 2x`. Les intersections de leurs courbes ont pour abscisses les solutions de `x² = 2x`. Le calcul donne `x(x − 2) = 0`, donc 0 et 2. Entre ces deux abscisses, `x(x − 2)` est négatif : la parabole est alors sous la droite, ce qui résout aussi `x² ≤ 2x` sur `[0 ; 2]`. Graphique et factorisation décrivent donc la même situation. Le dessin aide à voir les solutions ; le calcul précise leurs valeurs et justifie les bornes de l’intervalle.

    Source : [MacTutor, université de St Andrews, biographie d’Omar Khayyam](https://mathshistory.st-andrews.ac.uk/Biographies/Khayyam/).

## Voir aussi

- PRÉREQUIS : [N05](N05-equations-inequations.md) (Les équations et inéquations sont le socle algébrique.)
- PRÉREQUIS : [N09](N09-fonctions-registres.md) (Les lectures de fonctions sont mobilisées.)
