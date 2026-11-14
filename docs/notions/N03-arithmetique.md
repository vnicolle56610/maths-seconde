---
title: "Arithmétique : multiples, restes et fractions"
description: Cours et exercices de Seconde pour travailler multiples, restes, fractions et petites démonstrations arithmétiques.
---

# N03 — Arithmétique

<!-- NOTION-NAV:START -->
<nav class="notion-nav" aria-label="Navigation entre notions">
<a class="notion-nav__btn notion-nav__btn--prev" href="../N02-nombres-reels-intervalles/"><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M16 6v12L6 12z" fill="currentColor"/></svg></span><span class="notion-nav__text"><small>Notion précédente</small><span class="notion-nav__title">N02 — Nombres réels, intervalles et valeur absolue</span></span></a>
<a class="notion-nav__btn notion-nav__btn--next" href="../N04-calcul-litteral/"><span class="notion-nav__text"><small>Notion suivante</small><span class="notion-nav__title">N04 — Calcul littéral</span></span><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M8 6v12l10-6z" fill="currentColor"/></svg></span></a>
</nav>
<!-- NOTION-NAV:END -->

L'arithmétique donne des outils simples pour raisonner sur les entiers. Les documents font travailler les multiples, les restes, la réduction de fractions et la rédaction de petites démonstrations. L'enjeu n'est pas seulement de calculer, mais de reconnaître la structure d'un nombre et de justifier une conclusion.

## Objectifs

!!! objectifs ""

    - Reconnaître des multiples et exploiter des restes.
    - Réduire une fraction.
    - Rédiger une petite démonstration arithmétique.

## Documents

<!-- AUTO-DOCS:START -->
- [Cours N03 — Arithmétique](../cours/COURS_N03_ARITHMETIQUE.pdf)
- [TD N03 — Arithmétique](../td/TD_N03_ARITHMETIQUE.pdf)
- [Corrigé TD N03](../corriges/CORRIGE_TD_N03_ARITHMETIQUE.pdf)
<!-- AUTO-DOCS:END -->

<!-- AUTOMATISMES-WEB:START -->
- ⚡ [Automatismes N03 en ligne : énoncés, corrigés et QCM interactif](../automatismes/automatismes-N03-arithmetique.md)
<!-- AUTOMATISMES-WEB:END -->

<!-- PARCOURS-GUIDE:START -->
### Parcours guidé

Des fiches pour reprendre la notion en autonomie : à la maison, après une absence ou avant une évaluation. Chaque bloc commence par un **exemple résolu**. Les réponses sont imprimées **à l'envers** dans les cadres « Je vérifie » : répondre d'abord, retourner la feuille ensuite.

- 📝 [Fiche 1 — Multiples et diviseurs](../parcours-guide/PARCOURS_GUIDE_N03_FICHE_1.pdf) : reconnaître un multiple et un diviseur (a = b × k), division euclidienne (quotient, reste, plus grand multiple), liste des diviseurs par paires, pair et impair ; pour aller plus loin : démontrer avec des multiples.
- 📝 [Fiche 2 — Critères de divisibilité](../parcours-guide/PARCOURS_GUIDE_N03_FICHE_2.pdf) : divisibilité par 2, 5 et 10 avec le dernier chiffre, par 3 et 9 avec la somme des chiffres, trouver un chiffre manquant, reconnaître un nombre premier.
- 📝 [Fiche 3 — Fractions irréductibles](../parcours-guide/PARCOURS_GUIDE_N03_FICHE_3.pdf) : simplifier une fraction par étapes, décomposer un nombre en facteurs premiers avec un arbre, rendre une fraction irréductible avec les décompositions, dire si une fraction est irréductible.
- 📝 [Fiche passerelle — Problèmes de partage](../parcours-guide/PARCOURS_GUIDE_N03_FICHE_4.pdf) : fiche passerelle : traduire « sans reste » par un diviseur, partager deux quantités avec un diviseur commun, choisir entre diviseur commun et multiple commun dans un problème sans modèle, avant le retour au TD.

À la maison, ignorer les cases « STOP ». Faire le ticket de sortie seul, à la fin, puis l'apporter au cours suivant pour le faire vérifier.
<!-- PARCOURS-GUIDE:END -->

<!-- AUTO-EVAL:START -->
- 🎯 Évaluée au DS1 du mardi 24 novembre : [voir le devoir blanc](../preparer-evaluation/index.md#ds1-2026-2027)
<!-- AUTO-EVAL:END -->

## Notions essentielles

!!! essentiel ""

    Dire que `a` est un multiple de `b` signifie qu'il existe un entier `k` tel que `a = b × k`.

    Dans une division euclidienne, un nombre est divisible par un autre lorsque le reste est nul.

    Un nombre pair peut s'écrire `2k`. Un nombre impair peut s'écrire `2k + 1`.

    Une fraction est irréductible lorsque son numérateur et son dénominateur n'ont aucun diviseur commun autre que 1.

    Pour démontrer une propriété sur les entiers, on utilise souvent une écriture générale comme `dk`, `2k` ou `2k + 1`.

## Exemple

!!! exemple ""

    `42 = 6 × 7`, donc 42 est un multiple de 6 et 6 est un diviseur de 42.

    En revanche, `44 = 6 × 7 + 2` : le reste n'est pas nul, donc 44 n'est pas divisible par 6.

## Repère historique — Euclide : pourquoi la liste des nombres premiers ne s’arrête pas

!!! historique ""

    Euclide, *Éléments*, Alexandrie, vers −300
    {: .frise data-annee="-300" data-etiquette="v. −300" }

    Dans le livre IX des *Éléments*, la proposition 20 établit qu’aucune liste finie ne peut contenir tous les nombres premiers. Le problème dépasse une simple recherche de grands nombres : il s’agit de démontrer une propriété valable quelle que soit la liste choisie. Euclide raisonne à partir d’un multiple commun des nombres proposés, auquel il ajoute une unité.

    Voici une illustration moderne, avec 2, 3 et 5. Leur produit vaut 30 ; le nombre `30 + 1 = 31` laisse un reste de 1 lorsqu’on le divise par chacun d’eux. Aucun des trois ne le divise. Dans cet exemple, 31 est premier. Plus généralement, le nombre construit pourrait être composé : on chercherait alors un de ses diviseurs premiers, forcément absent de la liste initiale. Le raisonnement relie donc multiples, restes et diviseurs. Il rappelle aussi qu’observer quelques exemples ne suffit pas à démontrer une affirmation générale sur les entiers.

    Source : [Euclide, *Éléments*, IX.20, édition commentée de David E. Joyce, université Clark](https://mathcs.clarku.edu/~djoyce/elements/bookIX/propIX20.html).
