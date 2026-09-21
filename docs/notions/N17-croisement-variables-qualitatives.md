---
title: Tableaux croisés et variables qualitatives
description: Cours et exercices de Seconde pour lire un tableau croisé, interpréter des effectifs et contrôler la population de référence.
---

# N17 — Tableaux croisés et variables qualitatives

Un tableau croisé organise deux variables qualitatives dans une même lecture. Les documents font compléter des tableaux, interpréter des effectifs croisés et garder la population de référence sous contrôle. Cette rigueur prépare les raisonnements de probabilités conditionnelles simples, où le choix de la ligne ou de la colonne devient décisif.

## Objectifs

- Lire et compléter un tableau croisé.
- Interpréter des effectifs croisés.
- Identifier la population de référence.

<!-- NOTION-NAV:START -->
<nav class="notion-nav" aria-label="Navigation entre notions">
<a class="notion-nav__btn notion-nav__btn--prev" href="../N16-information-chiffree-statistiques/"><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M16 6v12L6 12z" fill="currentColor"/></svg></span><span class="notion-nav__text"><small>Notion précédente</small><span class="notion-nav__title">N16 — Information chiffrée et statistiques</span></span></a>
<a class="notion-nav__btn notion-nav__btn--next" href="../N18-probabilites-echantillonnage/"><span class="notion-nav__text"><small>Notion suivante</small><span class="notion-nav__title">N18 — Probabilités et échantillonnage</span></span><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M8 6v12l10-6z" fill="currentColor"/></svg></span></a>
</nav>
<!-- NOTION-NAV:END -->

## Objectifs

- Lire et compléter un tableau croisé.
- Interpréter des effectifs croisés.
- Garder la population de référence sous contrôle.

## Documents

<!-- AUTO-DOCS:START -->
- [Cours N17 — Tableaux croisés et variables qualitatives](../cours/COURS_N17_CROISEMENT_VARIABLES_QUALITATIVES.pdf)
- [TD N17 — Tableaux croisés et variables qualitatives](../td/TD_N17_CROISEMENT_VARIABLES_QUALITATIVES.pdf)
- [Automatismes N17 — Tableaux croisés et variables qualitatives](../automatismes/AUTOMATISMES_N17_CROISEMENT_VARIABLES_QUALITATIVES.pdf)
<!-- AUTO-DOCS:END -->

## Notions essentielles

Un tableau croisé d'effectifs présente les effectifs d'une population selon deux variables qualitatives ; les totaux de lignes et de colonnes sont appelés des marges. Une fréquence marginale utilise le total de la population comme référence. Une fréquence conditionnelle utilise un sous-groupe comme référence : si `A` et `B` sont deux caractères, la fréquence de `A` parmi les individus de `B` est `f_B(A) = effectif(A∩B) / effectif(B)`.

Avant tout calcul de pourcentage, il faut écrire une phrase du type « on se place parmi les… » : le dénominateur est alors l'effectif de ce groupe. En général, `f_B(A) ≠ f_A(B)` : ces deux fréquences répondent à des questions différentes.

Les filtres ET, OU, NON permettent de traduire des critères sur une liste d'individus : « A ET B » garde les individus vérifiant les deux conditions, « A OU B » garde ceux qui en vérifient au moins une, « NON A » garde ceux qui ne vérifient pas A.

## Exemple

Dans une enquête sur 120 élèves, 30 viennent à vélo, dont 20 pratiquent un sport en club. La fréquence des sportifs parmi les cyclistes est `f_vélo(sport) = 20/30 ≈ 66,7 %`.

Ce n'est pas la même chose que la fréquence des cyclistes parmi les sportifs, qui se calcule avec un dénominateur différent.

## Voir aussi

- PRÉREQUIS : [N16](N16-information-chiffree-statistiques.md) (Les populations de référence sont déjà travaillées.)
- PROLONGEMENT : [N18](N18-probabilites-echantillonnage.md) (Les probabilités réutilisent ces lectures.)
