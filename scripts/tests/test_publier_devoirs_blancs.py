#!/usr/bin/env python3
"""Tests du bloc « Après l'évaluation » de publier_devoirs_blancs.py.

Aucun test ne touche au vrai site : chaque test écrit sa propre déclaration
et sa propre source dans un répertoire temporaire.
"""

from __future__ import annotations

import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import publier_devoirs_blancs as pdb

ENTREE = """devoirs_blancs:
  - id: MT2
    date: 2026-11-05
    duree: 30 min
    calculatrice: interdite
    notions: [N04]
    dossier: Eval/MT2
    sujet: DEVOIR_BLANC_MT2.pdf
    corrige: CORRIGE_DEVOIR_BLANC_MT2.pdf
    etat: sujet_et_corrige
    apres_evaluation:
      etat: {etat}
      rattrapages_termines: {rattrapages}
      dossier: Eval/MT2/{dossier_apres}
      rubriques:
        - titre: Le mini-test
          documents:
            - {{fichier: {fichier}, libelle: sujet A}}
"""


class ApresEvaluationTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.racine = Path(self._tmp.name)
        self.source = self.racine / "source"
        eval_dir = self.source / "Eval" / "MT2"
        for nom in ("DEVOIR_BLANC_MT2.pdf", "CORRIGE_DEVOIR_BLANC_MT2.pdf"):
            (eval_dir / nom).parent.mkdir(parents=True, exist_ok=True)
            (eval_dir / nom).write_bytes(b"%PDF")
        for nom in ("MT2_SUJET_A.pdf", "CORRIGE_MT2_A_PROF.pdf"):
            (eval_dir / "apres_evaluation" / nom).parent.mkdir(parents=True, exist_ok=True)
            (eval_dir / "apres_evaluation" / nom).write_bytes(b"%PDF")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def charger(self, etat="publie", rattrapages="true", dossier_apres="apres_evaluation", fichier="MT2_SUJET_A.pdf"):
        chemin = self.racine / "devoirs_blancs.yaml"
        chemin.write_text(
            ENTREE.format(etat=etat, rattrapages=rattrapages, dossier_apres=dossier_apres, fichier=fichier),
            encoding="utf-8",
        )
        return pdb.charger_declarations(chemin, self.source)

    def test_publication_valide(self) -> None:
        devoirs = self.charger()
        pdb.controler_apres(devoirs, dt.date(2026, 11, 10))
        self.assertTrue(devoirs[0].apres_publie)
        lignes = "\n".join(pdb.lignes_entree(devoirs[0], dt.date(2026, 11, 10)))
        self.assertIn("**Après l'évaluation**", lignes)
        self.assertIn("(2026-2027/apres-mt2/MT2_SUJET_A.pdf)", lignes)

    def test_fichier_prof_refuse(self) -> None:
        with self.assertRaisesRegex(pdb.DeclarationError, "document professeur"):
            self.charger(fichier="CORRIGE_MT2_A_PROF.pdf")

    def test_dossier_hors_apres_evaluation_refuse(self) -> None:
        with self.assertRaisesRegex(pdb.DeclarationError, "apres_evaluation"):
            self.charger(dossier_apres=".")

    def test_avant_la_date_refuse(self) -> None:
        devoirs = self.charger()
        with self.assertRaisesRegex(pdb.DeclarationError, "avant la date"):
            pdb.controler_apres(devoirs, dt.date(2026, 11, 5))

    def test_rattrapages_non_termines_refuse(self) -> None:
        devoirs = self.charger(rattrapages="false")
        with self.assertRaisesRegex(pdb.DeclarationError, "rattrapages_termines"):
            pdb.controler_apres(devoirs, dt.date(2026, 11, 10))

    def test_non_publie_rien_affiche(self) -> None:
        devoirs = self.charger(etat="non_publie", rattrapages="false")
        pdb.controler_apres(devoirs, dt.date(2026, 11, 10))
        lignes = "\n".join(pdb.lignes_entree(devoirs[0], dt.date(2026, 11, 10)))
        self.assertNotIn("Après l'évaluation", lignes)


SANS_DEVOIR_BLANC = """devoirs_blancs:
  - id: MT1
    date: 2026-10-07
    duree: 30 min
    calculatrice: interdite
    notions: [N01]
    dossier: Eval/MT1
    etat: sans_devoir_blanc
{apres}"""

APRES_MT1 = """    apres_evaluation:
      etat: {etat}
      rattrapages_termines: true
      dossier: Eval/MT1/apres_evaluation
      rubriques:
        - titre: Le mini-test
          documents:
            - {{fichier: MT1_SUJET_A.pdf, libelle: sujet A}}
"""


class SansDevoirBlancTest(unittest.TestCase):
    """MT1 de Première (octobre 2026) : évaluation passée sans devoir blanc."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.racine = Path(self._tmp.name)
        self.source = self.racine / "source"
        cible = self.source / "Eval" / "MT1" / "apres_evaluation" / "MT1_SUJET_A.pdf"
        cible.parent.mkdir(parents=True)
        cible.write_bytes(b"%PDF")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def charger(self, apres: str):
        chemin = self.racine / "devoirs_blancs.yaml"
        chemin.write_text(SANS_DEVOIR_BLANC.format(apres=apres), encoding="utf-8")
        return pdb.charger_declarations(chemin, self.source)

    def test_bloc_apres_seul(self) -> None:
        jour = dt.date(2026, 11, 16)
        devoirs = self.charger(APRES_MT1.format(etat="publie"))
        pdb.controler_apres(devoirs, jour)
        self.assertEqual(devoirs[0].fichiers_publies, ())
        index = pdb.contenu_index(devoirs, jour)
        self.assertIn("Pas de devoir blanc pour cette évaluation.", index)
        self.assertNotIn("DEVOIR_BLANC", index)
        self.assertIn("(2026-2027/apres-mt1/MT1_SUJET_A.pdf)", index)
        self.assertIn("**Après l'évaluation**", index)
        self.assertNotIn("MT1", pdb.contenu_accueil(devoirs, jour))

    def test_plus_recente_en_haut(self) -> None:
        jour = dt.date(2026, 11, 16)
        devoirs = self.charger(APRES_MT1.format(etat="publie"))
        mt2 = pdb.DevoirBlanc(
            id="MT2", date=dt.date(2026, 11, 9), duree="", calculatrice="", notions=("N01",),
            dossier=self.source, sujet="DEVOIR_BLANC_MT2.pdf", corrige="CORRIGE_DEVOIR_BLANC_MT2.pdf",
            sujet_prevu=None, corrige_prevu=None, etat="sujet",
        )
        index = pdb.contenu_index([*devoirs, mt2], jour)
        self.assertLess(index.index("### Mini-test 2"), index.index("### Mini-test 1"))

    def test_rien_tant_que_apres_non_publie(self) -> None:
        jour = dt.date(2026, 11, 16)
        devoirs = self.charger(APRES_MT1.format(etat="non_publie"))
        pdb.controler_apres(devoirs, jour)
        self.assertFalse(devoirs[0].affiche(jour))
        self.assertNotIn("Mini-test 1", pdb.contenu_index(devoirs, jour))

    def test_bloc_apres_obligatoire(self) -> None:
        devoirs = self.charger("")
        with self.assertRaisesRegex(pdb.DeclarationError, "exige un bloc apres_evaluation"):
            pdb.controler_apres(devoirs, dt.date(2026, 11, 16))

    def test_sujet_declare_refuse(self) -> None:
        chemin = self.racine / "devoirs_blancs.yaml"
        texte = SANS_DEVOIR_BLANC.format(apres=APRES_MT1.format(etat="publie"))
        chemin.write_text(texte.replace("    etat: sans", "    sujet: MT1_SUJET_A.pdf\n    etat: sans"), encoding="utf-8")
        with self.assertRaisesRegex(pdb.DeclarationError, "ni sujet ni corrigé"):
            pdb.charger_declarations(chemin, self.source)


if __name__ == "__main__":
    unittest.main()
