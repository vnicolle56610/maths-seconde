---
title: Synthèse fonctions et modélisation
description: Révisions de Seconde pour choisir un registre de fonction, modéliser une situation, résoudre un problème et interpréter le résultat.
---

# N14 — Synthèse fonctions et modélisation

Cette synthèse regroupe les outils de fonctions travaillés jusque-là : lectures graphiques, formules, tableaux, variations, équations et inéquations. Les exercices demandent de choisir un registre adapté, de modéliser une situation, puis d’interpréter le résultat obtenu. La page reste large car elle sert de carrefour entre calcul, graphique et raisonnement.

<!-- NOTION-NAV:START -->
<nav class="notion-nav" aria-label="Navigation entre notions">
<a class="notion-nav__btn notion-nav__btn--prev" href="../N13-equations-inequations-fonctions/"><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M16 6v12L6 12z" fill="currentColor"/></svg></span><span class="notion-nav__text"><small>Notion précédente</small><span class="notion-nav__title">N13 — Équations et inéquations avec fonctions</span></span></a>
<a class="notion-nav__btn notion-nav__btn--next" href="../N15-geometrie-plane-problemes/"><span class="notion-nav__text"><small>Notion suivante</small><span class="notion-nav__title">N15 — Géométrie plane : problèmes et méthodes</span></span><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M8 6v12l10-6z" fill="currentColor"/></svg></span></a>
</nav>
<!-- NOTION-NAV:END -->

## Objectifs

!!! objectifs ""

    - Choisir le registre adapté à une fonction.
    - Modéliser une situation.
    - Résoudre puis interpréter.

## Documents

<!-- AUTO-DOCS:START -->
- [Cours N14 — Synthèse fonctions et modélisation](../cours/COURS_N14_SYNTHESE_FONCTIONS_MODELISATION.pdf)
- [TD N14 — Synthèse fonctions et modélisation](../td/TD_N14_SYNTHESE_FONCTIONS_MODELISATION.pdf)
<!-- AUTO-DOCS:END -->

<!-- AUTOMATISMES-WEB:START -->
- ⚡ [Automatismes N14 en ligne : énoncés, corrigés et QCM interactif](../automatismes/automatismes-N14-synthese-fonctions-modelisation.md)
<!-- AUTOMATISMES-WEB:END -->

## Notions essentielles

!!! essentiel ""

    Modéliser une situation par une fonction, c'est choisir une variable `x`, préciser son domaine de valeurs possibles, puis associer à chaque valeur de `x` une grandeur `f(x)` qui en dépend. Une fonction se lit alors de plusieurs façons : `f(x)` est la grandeur associée, `f(x) = k` traduit une valeur atteinte, `f(x) ≤ k` traduit une contrainte, un maximum ou un minimum traduit une situation optimale.

    Une même fonction peut être étudiée avec plusieurs représentations : une formule pour calculer exactement, un graphique pour lire et comparer, un tableau de valeurs pour organiser des essais, un tableau de signes ou de variations pour justifier. Comparer deux grandeurs `f(x)` et `g(x)` revient souvent à étudier le signe de `f(x) - g(x)`.

    Une solution mathématique doit toujours être interprétée dans le contexte : il faut vérifier qu'elle appartient au domaine du problème, puis répondre avec les mots de la situation. Une rédaction complète introduit la variable, écrit le modèle, résout, confronte le résultat au domaine, puis conclut.

## Exemple

!!! exemple ""

    Un club propose un tarif A à 14 € par personne et un tarif B à 50 € de forfait puis 8 € par personne, pour `x` participants entiers.

    Comparer les tarifs revient à résoudre `B(x) < A(x)`, soit `50 + 8x < 14x`, donc `50 < 6x`, donc `x > 25/3`. Comme `x` est un entier, le tarif B devient avantageux à partir de 9 participants.

## Repère historique — Galilée : choisir un modèle pour décrire un mouvement

!!! historique ""

    Galilée, *Discours*, 1638
    {: .frise data-annee="1638" }

    Dans ses travaux sur le mouvement, exposés notamment dans les *Discours* de 1638, Galilée établit qu’un mouvement uniformément accéléré à partir du repos conduit à une distance parcourue proportionnelle au carré du temps. Cette relation donne un exemple historique de mathématisation : choisir des grandeurs mesurables, formuler des hypothèses et chercher une loi qui relie les mesures. Elle ne signifie pas que tous les mouvements suivent cette règle.

    Dans un exemple moderne simplifié, on modélise une distance par `d(t) = 2t²`, en mètres, avec `t` en secondes et `0 ≤ t ≤ 3`. Le coefficient 2 est choisi pour l’exercice, sans prétendre reproduire une expérience de Galilée. Un tableau donne 2 mètres à 1 seconde et 8 mètres à 2 secondes : doubler le temps multiplie ici la distance par quatre. Chercher quand la distance atteint 8 mètres revient à résoudre `2t² = 8`. Le calcul donne −2 et 2, mais seul `t = 2` appartient au domaine. Interpréter le résultat fait ainsi partie intégrante de la modélisation.

    Source : [MacTutor, université de St Andrews, biographie de Galilée](https://mathshistory.st-andrews.ac.uk/Biographies/Galileo/).

## Voir aussi

- PRÉREQUIS : [N09](N09-fonctions-registres.md) (Les registres de fonctions sont réinvestis.)
- PRÉREQUIS : [N13](N13-equations-inequations-fonctions.md) (Les résolutions avec fonctions sont mobilisées.)
