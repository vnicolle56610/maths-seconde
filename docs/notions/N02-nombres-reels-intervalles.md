---
title: Nombres réels, intervalles et valeur absolue
description: Cours et exercices de Seconde sur les nombres réels, les intervalles, les inégalités, la valeur absolue et les encadrements.
---

# N02 — Nombres réels, intervalles et valeur absolue

<!-- NOTION-NAV:START -->
<nav class="notion-nav" aria-label="Navigation entre notions">
<a class="notion-nav__btn notion-nav__btn--prev" href="../N01-logique-ensembles/"><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M16 6v12L6 12z" fill="currentColor"/></svg></span><span class="notion-nav__text"><small>Notion précédente</small><span class="notion-nav__title">N01 — Logique, ensembles et raisonnement</span></span></a>
<a class="notion-nav__btn notion-nav__btn--next" href="../N03-arithmetique/"><span class="notion-nav__text"><small>Notion suivante</small><span class="notion-nav__title">N03 — Arithmétique</span></span><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M8 6v12l10-6z" fill="currentColor"/></svg></span></a>
</nav>
<!-- NOTION-NAV:END -->

Les nombres réels se représentent sur une droite graduée et se décrivent avec des inégalités ou des intervalles. Les ressources font travailler la lecture des bornes, le passage entre écriture symbolique et représentation graphique, la valeur absolue comme distance et les encadrements décimaux fiables.

## Objectifs

!!! objectifs ""

    - Passer d'une inégalité à un intervalle.
    - Interpréter une valeur absolue comme une distance.
    - Produire un encadrement décimal fiable.

## Documents

<!-- AUTO-DOCS:START -->
- [Cours N02 — Nombres réels, intervalles et valeur absolue](../cours/COURS_N02_NOMBRES_REELS_INTERVALLES.pdf)
- [TD N02 — Nombres réels, intervalles et valeur absolue](../td/TD_N02_NOMBRES_REELS_INTERVALLES.pdf)
- [Corrigé TD N02](../corriges/CORRIGE_TD_N02_NOMBRES_REELS_INTERVALLES.pdf)
<!-- AUTO-DOCS:END -->

<!-- AUTOMATISMES-WEB:START -->
- ⚡ [Automatismes N02 en ligne : énoncés, corrigés et QCM interactif](../automatismes/automatismes-N02-nombres-reels-intervalles.md)
<!-- AUTOMATISMES-WEB:END -->

<!-- PARCOURS-GUIDE:START -->
### Parcours guidé

Des fiches pour reprendre la notion en autonomie : à la maison, après une absence ou avant une évaluation. Chaque bloc commence par un **exemple résolu**. Les réponses sont imprimées **à l'envers** dans les cadres « Je vérifie » : répondre d'abord, retourner la feuille ensuite.

- 📝 [Fiche 1 — Les nombres réels](../parcours-guide/PARCOURS_GUIDE_N02_FICHE_1.pdf) · ✔️ [corrigé](../parcours-guide/PARCOURS_GUIDE_N02_FICHE_1_CORRIGE.pdf) : trouver le plus petit ensemble d'un nombre (N, Z, D, Q, R), reconnaître un rationnel, placer, ranger et comparer sur une droite graduée, encadrer un nombre au dixième et au centième.
- 📝 [Fiche 2 — Les intervalles](../parcours-guide/PARCOURS_GUIDE_N02_FICHE_2.pdf) · ✔️ [corrigé](../parcours-guide/PARCOURS_GUIDE_N02_FICHE_2_CORRIGE.pdf) : passer d'une phrase à une inégalité puis à un intervalle, choisir les crochets, représenter et lire un intervalle sur une droite graduée, dire si un nombre appartient à un intervalle, trouver l'intersection et la réunion de deux intervalles.
- 📝 [Fiche 3 — Valeur absolue et distance](../parcours-guide/PARCOURS_GUIDE_N02_FICHE_3.pdf) · ✔️ [corrigé](../parcours-guide/PARCOURS_GUIDE_N02_FICHE_3_CORRIGE.pdf) : calculer une valeur absolue et une distance entre deux nombres, résoudre |x − a| ≤ r avec le centre et le rayon, lire |x + b| comme une distance à −b, écrire un intervalle sous la forme |x − c| ≤ r.
- 📝 [Fiche passerelle — Combiner deux contraintes](../parcours-guide/PARCOURS_GUIDE_N02_FICHE_4.pdf) · ✔️ [corrigé](../parcours-guide/PARCOURS_GUIDE_N02_FICHE_4_CORRIGE.pdf) : fiche passerelle : traduire une phrase de distance par une valeur absolue puis par un intervalle, garder les nombres qui vérifient deux contraintes à la fois, puis un problème sans modèle avant le retour au TD.

À la maison, ignorer les cases « STOP ». Faire le ticket de sortie seul, à la fin, puis l'apporter au cours suivant pour le faire vérifier. Ne lire le corrigé qu'après avoir cherché.
<!-- PARCOURS-GUIDE:END -->

<!-- AUTO-EVAL:START -->
- 🎯 Évaluée au DS1 du mardi 24 novembre : [voir le devoir blanc](../preparer-evaluation/index.md#ds1-2026-2027)
<!-- AUTO-EVAL:END -->

## Notions essentielles

!!! essentiel ""

    Les nombres réels sont les nombres que l'on peut placer sur une droite graduée.

    Un intervalle traduit une inégalité : par exemple `x ∈ [−2 ; 3[` signifie `−2 ≤ x < 3`.

    La valeur absolue se lit comme une distance : `|a|` est la distance entre `a` et 0, et `|a - b|` est la distance entre `a` et `b`.

    Un encadrement décimal donne deux valeurs entre lesquelles le nombre se trouve.

## Exemple

!!! exemple ""

    L'écriture `x ∈ [−2 ; 3[` signifie que `x` est au moins égal à −2 et strictement inférieur à 3.

    On peut donc écrire : `−2 ≤ x < 3`.

## Repère historique — La diagonale du carré dépasse les fractions

!!! historique ""

    Mathématiques grecques, Antiquité
    {: .frise data-annee="-400" data-etiquette="Grèce antique" }

    Dans les mathématiques grecques antiques, l’étude des longueurs fait apparaître une difficulté : le côté d’un carré et sa diagonale n’ont pas de commune mesure. Cela signifie qu’aucune petite longueur ne permet de mesurer exactement les deux par des nombres entiers de reports. L’identité précise du premier auteur de cette découverte reste incertaine ; il faut éviter de l’attribuer sans réserve à Pythagore.

    Avec nos notations actuelles, un carré de côté 1 a une diagonale de longueur `√2`. Ce nombre n’est pas une fraction de deux entiers, mais c’est bien un réel que l’on peut placer sur une droite graduée. Un exemple moderne d’encadrement donne `1,41² = 1,9881` et `1,42² = 2,0164`, donc `1,41 < √2 < 1,42`. Les décimaux approchent ici une longueur exacte sans la remplacer. Cette distinction éclaire le chapitre : appartenir à un intervalle fournit une information sur un nombre, sans nécessairement donner sa valeur exacte.

    Source : [MacTutor, université de St Andrews, *The real numbers: Pythagoras to Stevin*](https://mathshistory.st-andrews.ac.uk/HistTopics/Real_numbers_1/).

## Voir aussi

- PRÉREQUIS : [N01](N01-logique-ensembles.md) (Le vocabulaire des ensembles facilite l’écriture des intervalles.)
- RÉINVESTISSEMENT : [N05](N05-equations-inequations.md) (Les ensembles de solutions utilisent les intervalles.)
