---
title: Logique, ensembles et raisonnement
description: Cours et exercices de Seconde pour utiliser le vocabulaire des ensembles, changer de registre et rédiger des justifications courtes.
---

# N01 — Logique, ensembles et raisonnement

<!-- NOTION-NAV:START -->
<nav class="notion-nav" aria-label="Navigation entre notions">
<a class="notion-nav__btn notion-nav__btn--next" href="../N02-nombres-reels-intervalles/"><span class="notion-nav__text"><small>Notion suivante</small><span class="notion-nav__title">N02 — Nombres réels, intervalles et valeur absolue</span></span><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M8 6v12l10-6z" fill="currentColor"/></svg></span></a>
</nav>
<!-- NOTION-NAV:END -->

Les notations d'ensembles aident à nommer précisément les objets manipulés en mathématiques. Le travail porte sur l'appartenance, l'inclusion, les changements de représentation et les justifications courtes. Ces repères rendent les raisonnements plus lisibles avant les intervalles, les équations et les problèmes où il faut conclure avec précision.

## Objectifs

!!! objectifs ""

    - Nommer des objets avec le vocabulaire des ensembles.
    - Passer d'une phrase à une notation ou un schéma.
    - Rédiger une justification courte.

## Documents

<!-- AUTO-DOCS:START -->
- [Cours N01 — Logique, ensembles et raisonnement](../cours/COURS_N01_LOGIQUE_ENSEMBLES.pdf)
- [TD N01 — Logique, ensembles et raisonnement](../td/TD_N01_LOGIQUE_ENSEMBLES.pdf)
- [Corrigé TD N01](../corriges/CORRIGE_TD_N01_LOGIQUE_ENSEMBLES.pdf)
<!-- AUTO-DOCS:END -->

<!-- AUTOMATISMES-WEB:START -->
- ⚡ [Automatismes N01 en ligne : énoncés, corrigés et QCM interactif](../automatismes/automatismes-N01-logique-ensembles.md)
<!-- AUTOMATISMES-WEB:END -->

## Notions essentielles

!!! essentiel ""

    `x ∈ A` signifie que `x` est un élément de l'ensemble `A`.

    `A ⊂ B` signifie que tout élément de `A` est aussi un élément de `B` : l'ensemble `A` est inclus dans l'ensemble `B`.

    `A ∩ B` contient les éléments communs à `A` et `B`. `A ∪ B` contient les éléments qui sont dans `A` ou dans `B`.

    Pour montrer qu'une phrase générale est fausse, un seul contre-exemple suffit.

    Une implication peut être vraie même si sa réciproque est fausse.

## Exemple

!!! exemple ""

    Si `A = {1 ; 2 ; 4}` et `B = {2 ; 3 ; 4}`, alors `A ∩ B = {2 ; 4}`.

    Les nombres 2 et 4 sont les éléments communs aux deux ensembles.

## Repère historique — Venn : représenter les relations logiques

!!! historique ""

    John Venn, Angleterre, 1880
    {: .frise data-annee="1880" }

    En 1880, John Venn publie des diagrammes pour représenter des relations logiques. Des dessins apparentés existaient déjà, notamment chez Euler : Venn ne part donc pas de rien. Son dispositif permet de distinguer les différentes combinaisons d’appartenance à des ensembles, y compris celles qui ne contiennent aucun élément dans une situation donnée.

    Dans une lecture actuelle, deux ensembles sont représentés par deux régions qui se chevauchent. Leur partie commune figure l’intersection ; l’ensemble des deux régions figure l’union. Prenons un exemple moderne : parmi les entiers de 1 à 12, on appelle `A` l’ensemble des multiples de 2 et `B` celui des multiples de 3. L’intersection contient 6 et 12. Mais 2 appartient à `A` sans appartenir à `B` : il suffit à réfuter l’affirmation « tout multiple de 2 est multiple de 3 ». Le dessin aide ainsi à chercher un contre-exemple ; la justification repose sur les propriétés des nombres.

    Source : [NIST, *Venn diagram*, notice de Paul E. Black](https://xlinux.nist.gov/dads/HTML/venndiagram.html).

## Voir aussi

- PROLONGEMENT : [N02](N02-nombres-reels-intervalles.md) (Les intervalles réutilisent le langage des ensembles.)
