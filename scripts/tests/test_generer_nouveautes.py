#!/usr/bin/env python3
"""Tests de la rubrique « Nouveautés » (scripts/generer_nouveautes.py).

Les tests travaillent sur des dates et des chemins fictifs : aucun vrai site
n'est touché.
"""

from __future__ import annotations

import datetime as dt
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import generer_nouveautes as g

J = dt.date(2026, 11, 15)
PAGES = {
    "N01": ("notions/N01-a/", "Logique"),
    "N02": ("notions/N02-b/", "Nombres"),
    "N05": ("notions/N05-c/", "Équations"),
}


class ClasserTest(unittest.TestCase):
    def test_types(self):
        self.assertEqual(g.classer("parcours-guide/PARCOURS_GUIDE_N05_FICHE_2.pdf"), ("parcours", "N05"))
        self.assertEqual(
            g.classer("parcours-guide/PARCOURS_GUIDE_N06_PARTIE_1_FICHE_1_CORRIGE.pdf"),
            ("corrige_parcours", "N06"),
        )
        self.assertEqual(g.classer("cours/COURS_N04_CALCUL.pdf"), ("cours", "N04"))
        self.assertEqual(g.classer("corriges/CORRIGE_TD_N04_CALCUL.pdf"), ("corrige_td", "N04"))
        self.assertEqual(g.classer("automatismes/qcm-N12-variations.md"), ("automatismes", "N12"))
        self.assertEqual(
            g.classer("preparer-evaluation/2026-2027/DEVOIR_BLANC_MT2_P14_N03.pdf"), ("devoir_blanc", "MT2")
        )
        self.assertEqual(
            g.classer("preparer-evaluation/2026-2027/CORRIGE_DEVOIR_BLANC_DS1_1S.pdf"),
            ("corrige_devoir_blanc", "DS1"),
        )
        self.assertEqual(
            g.classer("preparer-evaluation/2026-2027/apres-mt2/MT2_N04_SUJET_A.pdf"),
            ("apres_evaluation", "MT2"),
        )

    def test_ignores(self):
        for chemin in (
            "assets/images/hero.png",
            "automatismes/figures/N03-fonctions-e787a0b33f.svg",
            "notions/N05-second-degre-i.md",
            "preparer-evaluation/index.md",
            "stylesheets/extra.css",
        ):
            self.assertIsNone(g.classer(chemin), chemin)


class RegrouperTest(unittest.TestCase):
    def test_fiches_et_corriges_le_meme_jour_font_une_ligne(self):
        dates = {
            "docs/parcours-guide/PARCOURS_GUIDE_N05_FICHE_1.pdf": J,
            "docs/parcours-guide/PARCOURS_GUIDE_N05_FICHE_1_CORRIGE.pdf": J,
        }
        lignes = g.regrouper(dates, J)
        self.assertEqual(len(lignes), 1)
        self.assertIn("avec corrigés", g.rendre_ligne(lignes[0], PAGES))
        self.assertIn("#parcours-guide", g.rendre_ligne(lignes[0], PAGES))

    def test_corriges_ajoutes_plus_tard_sont_annonces(self):
        veille = J - dt.timedelta(days=3)
        dates = {
            "docs/parcours-guide/PARCOURS_GUIDE_N05_FICHE_1.pdf": veille,
            "docs/parcours-guide/PARCOURS_GUIDE_N05_FICHE_1_CORRIGE.pdf": J,
        }
        lignes = g.regrouper(dates, J)
        self.assertEqual([l.type for l in lignes], ["corrige_parcours", "parcours"])

    def test_fenetre_et_plafond(self):
        dates = {"docs/cours/COURS_N01_X.pdf": J - dt.timedelta(days=g.JOURS_FENETRE)}
        self.assertEqual(g.regrouper(dates, J), [])
        dates = {
            f"docs/cours/COURS_N0{i}_X.pdf": J - dt.timedelta(days=i) for i in range(1, 8)
        }
        self.assertEqual(len(g.regrouper(dates, J)), g.MAX_LIGNES)

    def test_plages(self):
        self.assertEqual(
            g.plages(["N01", "N02", "N03", "N05"]), [["N01", "N02", "N03"], ["N05"]]
        )


class ZoneTest(unittest.TestCase):
    def test_remplacer_zone(self):
        texte = f"avant\n{g.ZONE_START}\nvieux\n{g.ZONE_END}\naprès\n"
        nouveau = g.remplacer_zone(texte, f"{g.ZONE_START}\nneuf\n{g.ZONE_END}")
        self.assertEqual(nouveau, f"avant\n{g.ZONE_START}\nneuf\n{g.ZONE_END}\naprès\n")

    def test_zone_mal_formee(self):
        with self.assertRaises(ValueError):
            g.remplacer_zone(f"{g.ZONE_START}\n{g.ZONE_START}\n{g.ZONE_END}", "x")


if __name__ == "__main__":
    unittest.main()
