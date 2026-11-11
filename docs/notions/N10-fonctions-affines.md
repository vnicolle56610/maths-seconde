---
title: Fonctions affines
description: Cours et exercices de Seconde sur les fonctions affines, le coefficient directeur, l’ordonnée à l’origine, le signe et la modélisation.
---

# N10 — Fonctions affines

<!-- NOTION-NAV:START -->
<nav class="notion-nav" aria-label="Navigation entre notions">
<a class="notion-nav__btn notion-nav__btn--prev" href="../N09-fonctions-registres/"><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M16 6v12L6 12z" fill="currentColor"/></svg></span><span class="notion-nav__text"><small>Notion précédente</small><span class="notion-nav__title">N09 — Fonctions : images, antécédents et registres</span></span></a>
<a class="notion-nav__btn notion-nav__btn--next" href="../N11-fonctions-reference/"><span class="notion-nav__text"><small>Notion suivante</small><span class="notion-nav__title">N11 — Fonctions de référence</span></span><span class="notion-nav__icon"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M8 6v12l10-6z" fill="currentColor"/></svg></span></a>
</nav>
<!-- NOTION-NAV:END -->

Une fonction affine modélise une évolution à rythme constant. Les documents relient la formule f(x)=mx+p à sa droite représentative, au coefficient directeur et au signe de la fonction. Les exercices font aussi interpréter une situation affine, ce qui prolonge les lectures graphiques.

## Objectifs

!!! objectifs ""

    - Relier une formule affine à sa droite représentative.
    - Utiliser coefficient directeur et ordonnée à l’origine.
    - Modéliser une situation affine.

## Documents

<!-- AUTO-DOCS:START -->
- [Cours N10 — Fonctions affines](../cours/COURS_N10_FONCTIONS_AFFINES.pdf)
- [TD N10 — Fonctions affines](../td/TD_N10_FONCTIONS_AFFINES.pdf)
- [Automatismes N10 — Fonctions affines](../automatismes/AUTOMATISMES_N10_FONCTIONS_AFFINES.pdf)
<!-- AUTO-DOCS:END -->

<!-- AUTOMATISMES-WEB:START -->
- ⚡ [Automatismes N10 en ligne : énoncés, corrigés et QCM interactif](../automatismes/automatismes-N10-fonctions-affines.md)
<!-- AUTOMATISMES-WEB:END -->

## Notions essentielles

!!! essentiel ""

    Une fonction affine est une fonction qui peut s'écrire sous la forme `f(x) = mx + p`.

    Le nombre `m` est le coefficient directeur : il indique la pente de la droite représentative. Le nombre `p` est l'ordonnée à l'origine : c'est l'image de 0.

    La courbe représentative d'une fonction affine est une droite. Si `m > 0`, la fonction est croissante ; si `m < 0`, elle est décroissante ; si `m = 0`, elle est constante.

    Pour étudier le signe d'une fonction affine non constante, on commence par chercher sa racine, c'est-à-dire la valeur de `x` pour laquelle `f(x) = 0`.

    Dans une situation concrète, une fonction affine modélise une évolution à rythme constant : à chaque même augmentation de `x` correspond une même variation de `f(x)`.

## Exemple

!!! exemple ""

    Pour `f(x) = 2x - 3`, le coefficient directeur est 2 et l'ordonnée à l'origine est -3.

    Comme `2 > 0`, la fonction est croissante. Sa racine vérifie `2x - 3 = 0`, donc `x = 1,5`.

## Repère historique — Des échelles de température aux fonctions affines

!!! historique ""

    Fahrenheit (1724), puis Celsius, XVIIIe siècle
    {: .frise data-annee="1724" data-fin="1742" data-etiquette="XVIIIe s." }

    Au XVIIIe siècle, plusieurs échelles de température se développent pour rendre les mesures comparables. Fahrenheit présente la sienne en 1724 ; Celsius propose ensuite une échelle dont les repères sont initialement inversés par rapport à l’usage actuel. Ces choix historiques expliquent qu’une même température puisse recevoir des nombres différents. Convertir exige de tenir compte à la fois de la taille des graduations et du décalage des zéros.

    Avec les conventions actuelles, si `C` désigne la valeur en degrés Celsius et `F` celle en degrés Fahrenheit, la conversion s’écrit `F = 1,8C + 32`. C’est une relation affine. Dans cet exemple moderne, `0 °C` correspond à `32 °F` et `20 °C` à `68 °F`. Une hausse de `10 °C` correspond toujours à une hausse de `18 °F` : le coefficient 1,8 décrit le rapport des variations. Le terme 32 indique le décalage des origines. La conversion n’est donc pas proportionnelle : doubler la valeur en Celsius ne double généralement pas la valeur en Fahrenheit.

    Sources : NIST, [*Kelvin: History*](https://www.nist.gov/si-redefinition/kelvin/kelvin-history) et [*SI Units – Temperature*, conversions exactes](https://www.nist.gov/pml/owm/si-units-temperature).

## Voir aussi

- PRÉREQUIS : [N09](N09-fonctions-registres.md) (Les lectures de fonctions sont nécessaires.)
