---
title: Variations et extremums de fonctions
description: Cours et exercices de Seconde pour lire ou construire un tableau de variations, déterminer un extremum et résoudre une optimisation simple.
---

# N12 — Variations et extremums

Les variations décrivent comment les valeurs d’une fonction évoluent sur un intervalle. Les ressources font lire et construire des tableaux de variations, repérer des extremums et traiter des problèmes simples d’optimisation. Le travail reste graphique et numérique, avec une attention portée à l’interprétation.

<!-- NOTION-NAV:START -->
<nav class="notion-nav" aria-label="Navigation entre notions">
<a class="notion-nav__btn notion-nav__btn--prev" href="../N11-fonctions-reference/"><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M16 6v12L6 12z" fill="currentColor"/></svg></span><span class="notion-nav__text"><small>Notion précédente</small><span class="notion-nav__title">N11 — Fonctions de référence</span></span></a>
<a class="notion-nav__btn notion-nav__btn--next" href="../N13-equations-inequations-fonctions/"><span class="notion-nav__text"><small>Notion suivante</small><span class="notion-nav__title">N13 — Équations et inéquations avec fonctions</span></span><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M8 6v12l10-6z" fill="currentColor"/></svg></span></a>
</nav>
<!-- NOTION-NAV:END -->

## Objectifs

!!! objectifs ""

    - Lire et construire un tableau de variations.
    - Déterminer un extremum.
    - Traiter un problème simple d'optimisation.

## Documents

<!-- AUTO-DOCS:START -->
- [Cours N12 — Variations et extremums](../cours/COURS_N12_VARIATIONS_EXTREMUMS.pdf)
- [TD N12 — Variations et extremums](../td/TD_N12_VARIATIONS_EXTREMUMS.pdf)
<!-- AUTO-DOCS:END -->

<!-- AUTOMATISMES-WEB:START -->
- ⚡ [Automatismes N12 en ligne : énoncés, corrigés et QCM interactif](../automatismes/automatismes-N12-variations-extremums.md)
<!-- AUTOMATISMES-WEB:END -->

## Notions essentielles

!!! essentiel ""

    Dire qu'une fonction est croissante sur un intervalle signifie que les images augmentent lorsque `x` augmente sur cet intervalle.

    Dire qu'une fonction est décroissante sur un intervalle signifie que les images diminuent lorsque `x` augmente sur cet intervalle.

    Un maximum est la plus grande valeur prise par une fonction sur un intervalle. Un minimum est la plus petite valeur prise par une fonction sur un intervalle.

    Un tableau de variations résume les intervalles sur lesquels la fonction augmente ou diminue, ainsi que les valeurs importantes aux bornes et aux extremums.

    Pour résoudre un problème d'optimisation, on choisit une variable, on précise son domaine, puis on cherche la valeur qui rend une grandeur maximale ou minimale.

## Exemple

!!! exemple ""

    Si une fonction est décroissante sur `[−1 ; 3]` et si `0 < 2`, alors `f(0) ≥ f(2)`.

    Sur cet intervalle, l'ordre des images est inversé parce que la fonction décroît.

## Repère historique — Euclide : un carré pour comprendre un maximum

!!! historique ""

    Euclide, *Éléments*, Alexandrie, vers −300
    {: .frise data-annee="-300" data-etiquette="v. −300" }

    Dans le livre II des *Éléments*, la proposition 5 d’Euclide relie l’aire d’un rectangle à celles de deux carrés. Un segment est partagé en deux parties inégales ; le rectangle construit sur ces longueurs, augmenté d’un certain carré, a la même aire que le carré construit sur la moitié du segment initial. Le raisonnement repose sur un découpage géométrique, sans fonction ni tableau de variations.

    On peut aujourd’hui traduire cette relation par un exemple algébrique. Si deux longueurs positives ont pour somme 12, on les écrit `x` et `12 − x`, avec `0 < x < 12`. Leur produit vérifie `x(12 − x) = 36 − (x − 6)²`. Comme un carré est positif ou nul, ce produit est au plus égal à 36 ; cette valeur est atteinte pour `x = 6`. L’identité justifie ainsi un maximum exact, là où un tableau de valeurs ne donnerait que des indices. Elle distingue la valeur maximale, 36, de la valeur de la variable qui la réalise, 6.

    Source : [Euclide, *Éléments*, II.5, édition commentée de David E. Joyce, université Clark](https://mathcs.clarku.edu/~djoyce/elements/bookII/propII5.html).

## Voir aussi

- PRÉREQUIS : [N09](N09-fonctions-registres.md) (La lecture d’une fonction est nécessaire.)
