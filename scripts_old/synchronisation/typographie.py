"""Construction du titre lisible et du slug d'une notion.

Le nom technique d'un dossier (ex. ``TAUX_DE_VARIATION``) ne porte ni
accents ni typographie française. Cette fonction est le seul endroit du
projet où l'on décide comment l'habiller pour l'affichage.

Deux niveaux :

1. ``TITRES_PERSONNALISES`` : cas particuliers écrits en dur (pluriels,
   reformulations pédagogiques) — à compléter au fil de l'eau.
2. Algorithme générique : découpage sur ``_``, minuscules, majuscule au
   premier mot, chiffres romains et mots accentués corrigés via
   ``CORRECTIONS_ORTHOGRAPHIQUES``.
"""

from __future__ import annotations

import re
import unicodedata

# Cas particuliers où l'algorithme générique ne suffit pas (reformulation,
# pluriel pédagogique, etc.). Clé = nom_machine exact du dossier Nxx_XXXX.
TITRES_PERSONNALISES: dict[str, str] = {
    "TAUX_DE_VARIATION": "Taux de variation",
    "FONCTION_EXPONENTIELLE": "Fonctions exponentielles",
    "SUITES_ARITHMETIQUES_GEOMETRIIQUES": "Suites arithmétiques et géométriques",
}

# Corrections orthographiques mot à mot, appliquées après mise en minuscules.
# Complète l'algorithme générique pour les mots accentués les plus fréquents.
CORRECTIONS_ORTHOGRAPHIQUES: dict[str, str] = {
    "degre": "degré",
    "equations": "équations",
    "inequations": "inéquations",
    "derive": "dérivé",
    "derivee": "dérivée",
    "derivees": "dérivées",
    "reperages": "repérages",
    "reperage": "repérage",
    "reperee": "repérée",
    "reperees": "repérées",
    "geometrie": "géométrie",
    "trigonometrie": "trigonométrie",
    "arithmetiques": "arithmétiques",
    "aleatoires": "aléatoires",
    "probabilites": "probabilités",
    "independance": "indépendance",
    "esperance": "espérance",
    "problemes": "problèmes",
    "generalisees": "généralisées",
}

# Chiffres romains à préserver en majuscules quelle que soit leur position.
CHIFFRES_ROMAINS = frozenset({"I", "II", "III", "IV", "V", "VI"})


def construire_titre(nom_machine: str) -> str:
    """Transformer un nom technique de dossier en titre lisible.

    Exemple : ``SECOND_DEGRE_I`` -> ``Second degré I``.
    """
    if nom_machine in TITRES_PERSONNALISES:
        return TITRES_PERSONNALISES[nom_machine]

    mots = [mot for mot in nom_machine.split("_") if mot]
    mots_habilles = []
    for indice, mot in enumerate(mots):
        if mot.upper() in CHIFFRES_ROMAINS:
            mots_habilles.append(mot.upper())
            continue

        mot_minuscule = mot.lower()
        mot_corrige = CORRECTIONS_ORTHOGRAPHIQUES.get(mot_minuscule, mot_minuscule)
        if indice == 0:
            mot_corrige = mot_corrige[:1].upper() + mot_corrige[1:]
        mots_habilles.append(mot_corrige)

    return " ".join(mots_habilles)


def construire_slug(texte: str) -> str:
    """Transformer un intitulé en fragment d'URL sûr (sans accent, en kebab-case)."""
    normalise = unicodedata.normalize("NFKD", texte.casefold())
    sans_accents = "".join(
        caractere for caractere in normalise if not unicodedata.combining(caractere)
    )
    slug = re.sub(r"[\W_]+", "-", sans_accents).strip("-")
    return slug or "notion"
