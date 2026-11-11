---
title: Probabilités et échantillonnage
description: Cours et exercices de Seconde pour modéliser une situation probabiliste, interpréter un conditionnement et lire une simulation.
---

# N18 — Probabilités et échantillonnage

Les probabilités transforment une situation aléatoire en modèle calculable. Les ressources font passer d’un contexte à un modèle, interpréter une probabilité conditionnelle et lire une simulation. Le vocabulaire des données reste important pour éviter de confondre effectifs, fréquences et probabilités.

<!-- NOTION-NAV:START -->
<nav class="notion-nav" aria-label="Navigation entre notions">
<a class="notion-nav__btn notion-nav__btn--prev" href="../N17-croisement-variables-qualitatives/"><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M16 6v12L6 12z" fill="currentColor"/></svg></span><span class="notion-nav__text"><small>Notion précédente</small><span class="notion-nav__title">N17 — Tableaux croisés et variables qualitatives</span></span></a>
<a class="notion-nav__btn notion-nav__btn--next" href="../N19-synthese-statistiques-probabilites/"><span class="notion-nav__text"><small>Notion suivante</small><span class="notion-nav__title">N19 — Synthèse statistiques et probabilités</span></span><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M8 6v12l10-6z" fill="currentColor"/></svg></span></a>
</nav>
<!-- NOTION-NAV:END -->

## Objectifs

!!! objectifs ""

    - Passer d'une situation à un modèle probabiliste.
    - Interpréter une probabilité conditionnelle.
    - Lire une simulation.

## Documents

<!-- AUTO-DOCS:START -->
- [Cours N18 — Probabilités et échantillonnage](../cours/COURS_N18_PROBABILITES_ECHANTILLONNAGE.pdf)
- [TD N18 — Probabilités et échantillonnage](../td/TD_N18_PROBABILITES_ECHANTILLONNAGE.pdf)
- [Automatismes N18 — Probabilités et échantillonnage](../automatismes/AUTOMATISMES_N18_PROBABILITES_ECHANTILLONNAGE.pdf)
<!-- AUTO-DOCS:END -->

<!-- AUTOMATISMES-WEB:START -->
- ⚡ [Automatismes N18 en ligne : énoncés, corrigés et QCM interactif](../automatismes/automatismes-N18-probabilites-echantillonnage.md)
<!-- AUTOMATISMES-WEB:END -->

## Notions essentielles

!!! essentiel ""

    Dans une expérience aléatoire, l'univers `Ω` est l'ensemble des issues possibles et un événement est une partie de `Ω`. Une loi de probabilité associe à chaque issue un nombre compris entre 0 et 1, de sorte que la somme des probabilités de toutes les issues vaut 1. En cas d'équiprobabilité, `P(A) = Card(A) / Card(Ω)`. Si `Ā` désigne l'événement contraire de `A`, alors `P(Ā) = 1 - P(A)`.

    La probabilité de `B` sachant `A`, notée `P_A(B)`, mesure la probabilité de `B` lorsqu'on se place dans la situation où `A` est réalisé : `P_A(B) = P(A∩B) / P(A)`. En général, `P_A(B) ≠ P_B(A)` : le dénominateur n'est pas le même. Dans un arbre pondéré, les branches portent des probabilités, souvent conditionnelles à partir du deuxième niveau, et la probabilité d'un chemin est le produit des probabilités portées par ses branches.

    Un échantillon est un ensemble d'observations obtenu en répétant une expérience. La fréquence observée peut varier d'un échantillon à l'autre : c'est la fluctuation d'échantillonnage. Lorsque le nombre d'essais est grand, la fréquence observée est en général proche de la probabilité, mais une simulation ne démontre pas une valeur exacte.

## Exemple

!!! exemple ""

    Une population de 200 pièces contient 30 pièces défectueuses. La probabilité de tirer une pièce défectueuse au hasard est `P = 30/200 = 0,15`.

    Sur 50 tirages simulés, on n'obtient pas nécessairement exactement `50 × 0,15 = 7,5` pièces défectueuses : le résultat fluctue d'une simulation à l'autre autour de cette valeur attendue.

## Repère historique — Bernoulli : relier la fréquence au modèle probabiliste

!!! historique ""

    Jacques Bernoulli, *Ars conjectandi*, 1713
    {: .frise data-annee="1713" }

    Dans l’*Ars conjectandi*, publié en 1713 après sa mort, Jacques Bernoulli développe un résultat fondateur de la loi des grands nombres. Il s’intéresse au lien entre une probabilité et la fréquence observée lors d’expériences répétées. Dans le cadre actuel d’essais indépendants ayant la même probabilité de succès, augmenter le nombre d’essais rend très probable une fréquence proche de cette probabilité. Cela ne garantit ni une égalité exacte ni un rapprochement régulier à chaque nouvel essai.

    Prenons un exemple moderne : une simulation répète des lancers indépendants d’un dé équilibré et compte les six. La probabilité théorique est `1/6`, mais dix lancers peuvent donner zéro, un ou plusieurs six. Même sur 600 lancers, obtenir exactement 100 six n’est pas obligatoire. Une série plus longue aide à étudier la stabilisation des fréquences ; elle ne prouve pas à elle seule que le dé est équilibré. Le modèle, ses hypothèses et les résultats observés jouent donc des rôles distincts. Cette distinction permet de lire une simulation sans confondre fluctuation et erreur de calcul.

    Source : [MacTutor, université de St Andrews, biographie de Jacques Bernoulli](https://mathshistory.st-andrews.ac.uk/Biographies/Bernoulli_Jacob/).

## Voir aussi

- PRÉREQUIS : [N17](N17-croisement-variables-qualitatives.md) (Les tableaux croisés aident à organiser les informations.)
