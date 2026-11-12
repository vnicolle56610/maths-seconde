#!/usr/bin/env python3
"""Tests des types « Parcours guidé » / « Corrigé parcours guidé » et du
retrait du lien PDF d'automatismes quand la page propose la version en ligne.

Chaque test construit son propre site jetable : aucun vrai site n'est touché.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import publier_ressources_site as publisher
import publication_manifest as pm

TEX_FICHE = (
    "% fiche\n"
    "\\newcommand{\\nomFiche}{Fiche 2 : résoudre sans discriminant}\n"
    "\\newcommand{\\resumeFiche}{facteur commun, x² = k.}\n"
    "\\input{preambule_parcours.tex}\n"
)

PAGE = """# N06 — Second degré

## Documents

<!-- AUTO-DOCS:START -->
<!-- AUTO-DOCS:END -->

<!-- AUTOMATISMES-WEB:START -->
- ⚡ [Automatismes N06 en ligne](../automatismes/automatismes-N06-x.md)
<!-- AUTOMATISMES-WEB:END -->

## Notions essentielles
"""


def make(path: Path, text: str = "%PDF-1.4 test\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class ClassificationTests(unittest.TestCase):
    def test_fiche_et_corrige(self) -> None:
        self.assertEqual(
            publisher.classify_pdf(Path("PARCOURS_GUIDE_N06_FICHE_1.pdf")),
            ("PARCOURS", "N06"),
        )
        self.assertEqual(
            publisher.classify_pdf(Path("PARCOURS_GUIDE_N06_PARTIE_1_FICHE_3_CORRIGE.pdf")),
            ("CORRIGE_PARCOURS", "N06"),
        )

    def test_autres_noms_inchanges(self) -> None:
        self.assertEqual(
            publisher.classify_pdf(Path("CORRIGE_TD_N06_X.pdf")), ("CORRIGE_TD", "N06")
        )
        self.assertIsNone(publisher.classify_pdf(Path("FICHE_1_N06_X.pdf")))
        self.assertIsNone(publisher.classify_pdf(Path("PARCOURS_SAGACES_N06_X.pdf")))

    def test_types_connus_du_manifeste(self) -> None:
        for kind in ("PARCOURS", "CORRIGE_PARCOURS"):
            self.assertIn(kind, pm.KIND_TO_MANIFEST_KEY)
            self.assertIn(pm.KIND_TO_MANIFEST_KEY[kind], pm.MANIFEST_KEY_ORDER)
            self.assertEqual(publisher.DESTINATION_DIRS[kind], "parcours-guide")
        self.assertIn("PARCOURS", publisher.SAFE_DEFAULT_KINDS)
        self.assertNotIn("CORRIGE_PARCOURS", publisher.SAFE_DEFAULT_KINDS)


class SiteJetable(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.source = root / "source"
        self.docs = root / "docs"
        self.page = make(self.docs / "notions" / "N06-second-degre.md", PAGE)
        dossier = self.source / "N06_SECOND_DEGRE" / "PARCOURS_GUIDE_PARTIE_1"
        make(dossier / "PARCOURS_GUIDE_N06_PARTIE_1_FICHE_2.tex", TEX_FICHE)
        make(dossier / "PARCOURS_GUIDE_N06_PARTIE_1_FICHE_2.pdf")
        make(dossier / "PARCOURS_GUIDE_N06_PARTIE_1_FICHE_2_CORRIGE.pdf")
        make(self.source / "N06_SECOND_DEGRE" / "TD_N06_SECOND_DEGRE.pdf")
        make(self.source / "N06_SECOND_DEGRE" / "AUTOMATISMES_N06_SECOND_DEGRE.pdf")
        self.resources, _, _ = publisher.discover_resources(self.source, self.docs)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def by_kind(self, *kinds: str) -> list:
        return [r for r in self.resources if r.kind in kinds]

    def publier(self, selection: list) -> str:
        report = publisher.PublicationReport()
        publisher.update_notion_pages(self.resources, selection, self.docs, report)
        self.assertEqual(report.warnings, [])
        return self.page.read_text(encoding="utf-8")

    def test_titre_et_resume_lus_dans_le_tex(self) -> None:
        fiche = self.by_kind("PARCOURS")[0]
        titre, resume, partie, numero = publisher.parcours_fiche_info(fiche)
        self.assertEqual(titre, "Fiche 2 — Résoudre sans discriminant")
        self.assertEqual(resume, "facteur commun, x² = k.")
        self.assertEqual((partie, numero), ("1", 2))
        corrige = self.by_kind("CORRIGE_PARCOURS")[0]
        self.assertEqual(
            publisher.student_link_title(corrige),
            "Corrigé parcours guidé N06 (partie 1) — Fiche 2 — Résoudre sans discriminant",
        )

    def test_fiche_seule_puis_corrige(self) -> None:
        texte = self.publier(self.by_kind("TD", "AUTOMATISMES", "PARCOURS"))
        self.assertIn("### Parcours guidé (partie 1)", texte)
        self.assertIn(
            "- 📝 [Fiche 2 — Résoudre sans discriminant]"
            "(../parcours-guide/PARCOURS_GUIDE_N06_PARTIE_1_FICHE_2.pdf) : facteur commun, x² = k.",
            texte,
        )
        self.assertNotIn("corrigé", texte.split("PARCOURS-GUIDE:START")[1])
        # zone placée après les automatismes en ligne, avant la suite de la page
        self.assertLess(texte.index("AUTOMATISMES-WEB:END"), texte.index("PARCOURS-GUIDE:START"))
        self.assertLess(texte.index("PARCOURS-GUIDE:END"), texte.index("## Notions essentielles"))

        texte = self.publier(self.by_kind("TD", "AUTOMATISMES", "PARCOURS", "CORRIGE_PARCOURS"))
        self.assertIn(
            " · ✔️ [corrigé](../parcours-guide/PARCOURS_GUIDE_N06_PARTIE_1_FICHE_2_CORRIGE.pdf)",
            texte,
        )
        self.assertIn(publisher.PARCOURS_OUTRO_CORRIGE, texte)
        self.assertEqual(texte.count("PARCOURS-GUIDE:START"), 1)

    def test_liste_documents_sans_automatismes_ni_parcours(self) -> None:
        texte = self.publier(self.by_kind("TD", "AUTOMATISMES", "PARCOURS"))
        zone = texte.split("AUTO-DOCS:START")[1].split("AUTO-DOCS:END")[0]
        self.assertIn("TD_N06_SECOND_DEGRE.pdf", zone)
        self.assertNotIn("AUTOMATISMES_N06", zone)
        self.assertNotIn("PARCOURS_GUIDE", zone)

    def test_automatismes_gardes_sans_version_en_ligne(self) -> None:
        self.page.write_text(
            PAGE.replace("- ⚡ [Automatismes N06 en ligne](../automatismes/automatismes-N06-x.md)\n", ""),
            encoding="utf-8",
        )
        texte = self.publier(self.by_kind("TD", "AUTOMATISMES"))
        zone = texte.split("AUTO-DOCS:START")[1].split("AUTO-DOCS:END")[0]
        self.assertIn("AUTOMATISMES_N06_SECOND_DEGRE.pdf", zone)

    def test_zone_retiree_si_plus_rien_de_publie(self) -> None:
        self.publier(self.by_kind("PARCOURS"))
        texte = self.publier(self.by_kind("TD"))
        self.assertNotIn("PARCOURS-GUIDE", texte)
        self.assertIn("<!-- AUTOMATISMES-WEB:END -->\n\n## Notions essentielles", texte)


if __name__ == "__main__":
    unittest.main()
