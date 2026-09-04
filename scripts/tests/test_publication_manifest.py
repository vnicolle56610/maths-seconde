#!/usr/bin/env python3
"""Tests du nouveau modèle « état de publication » (publication_manifest.py).

Aucun test ici ne touche à un vrai site (maths-seconde ou autre) : chaque
test construit son propre site jetable dans un répertoire temporaire, y
compris un site totalement fictif (test_genericity) démontrant que le
moteur ne dépend d'aucun nom de niveau codé en dur.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import publier_ressources_site as publisher
import publication_manifest as pm


def make_pdf(path: Path, content: bytes = b"%PDF-1.4 test\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def make_notion_page(
    path: Path,
    notion: str,
    topic: str,
    documents: str = "",
    extra_after: str = "",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (
        f"# {notion} — {topic}\n\n"
        f"Texte de présentation de {notion}.\n\n"
        "## Documents\n\n"
        f"{publisher.AUTO_DOCS_START}\n{documents}\n{publisher.AUTO_DOCS_END}\n"
    )
    if extra_after:
        text += f"\n{extra_after}\n"
    path.write_text(text, encoding="utf-8")


def make_section_index(path: Path, heading: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (
        f"# {heading}\n\n"
        f"{publisher.AUTO_DOCS_START}\n{publisher.AUTO_DOCS_END}\n"
    )
    path.write_text(text, encoding="utf-8")


def modified_pages_of_interest(result, *ignored: Path) -> set:
    """Filtrer les pages dont la mise à jour est un mécanisme déjà testé
    ailleurs (accès rapide de l'accueil, section vide pour une notion dont
    une ressource existe mais n'est pas publiée) et non ce que le test
    vérifie explicitement.
    """
    return set(result.report.modified_pages) - set(ignored)


class FakeSite:
    """Un site MkDocs jetable, avec sa propre source et son propre docs/."""

    def __init__(self, root: Path):
        self.project_root = root
        self.source_root = root / "SOURCE"
        self.docs_root = root / "docs"
        self.manifest_path = root / "publication_manifest.json"
        for directory in ("cours", "td", "automatismes", "corriges", "notions"):
            (self.docs_root / directory).mkdir(parents=True, exist_ok=True)
        make_section_index(self.docs_root / "td" / "index.md", "TD")
        make_section_index(self.docs_root / "automatismes" / "index.md", "Automatismes")
        make_section_index(self.docs_root / "corriges" / "index.md", "Corrigés")
        (self.docs_root / "index.md").write_text("# Accueil\n", encoding="utf-8")

    def discover(self):
        resources, pdf_count, ignored = publisher.discover_resources(
            self.source_root, self.docs_root
        )
        return resources


class ComputeStateTests(unittest.TestCase):
    """CAS A/B/C/D (section 3 et 6 de la demande)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.site = FakeSite(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_cas_a_publie_et_disponible(self):
        make_pdf(self.site.source_root / "N01_X" / "COURS_N01_X.pdf")
        make_notion_page(
            self.site.docs_root / "notions" / "N01-x.md", "N01", "X"
        )
        resources = self.site.discover()
        manifest = pm.manifest_from_keys({("N01", "COURS", "COURS_N01_X.pdf")})
        state = pm.compute_publication_state(resources, manifest, self.site.docs_root)
        item = state.items[0]
        self.assertEqual(item.status, pm.STATUS_PUBLISHED_AVAILABLE)
        self.assertTrue(item.published)
        self.assertIsNotNone(item.resource)

    def test_cas_b_nouveau_non_publie(self):
        make_pdf(self.site.source_root / "N05_Y" / "TD_N05_Y.pdf")
        resources = self.site.discover()
        manifest = pm.empty_manifest()
        state = pm.compute_publication_state(resources, manifest, self.site.docs_root)
        item = state.items[0]
        self.assertEqual(item.status, pm.STATUS_NEW_AVAILABLE)
        self.assertFalse(item.published)

    def test_cas_c_publie_mais_absent_de_la_source(self):
        # Publié dans le manifeste, physiquement dans docs/, mais plus dans
        # la source : ne doit jamais disparaître silencieusement.
        make_pdf(self.site.docs_root / "cours" / "COURS_N09_Z.pdf")
        manifest = pm.manifest_from_keys({("N09", "COURS", "COURS_N09_Z.pdf")})
        state = pm.compute_publication_state([], manifest, self.site.docs_root)
        item = state.items[0]
        self.assertEqual(item.status, pm.STATUS_PUBLISHED_MISSING_SOURCE)
        self.assertIsNone(item.resource)
        self.assertTrue(item.docs_file_exists)
        self.assertTrue(item.published)

    def test_cas_d_orphelin_jamais_publie_automatiquement(self):
        make_pdf(self.site.docs_root / "td" / "TD_N02_ORPHAN.pdf")
        # Ni dans le manifeste, ni dans la source : orphelin.
        state = pm.compute_publication_state([], pm.empty_manifest(), self.site.docs_root)
        self.assertEqual(state.items, [])
        self.assertEqual(len(state.orphans), 1)
        self.assertEqual(state.orphans[0].notion, "N02")


class DiffAndValidationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.site = FakeSite(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_diff_ajout_retrait_inchange(self):
        make_pdf(self.site.source_root / "N01_X" / "COURS_N01_X.pdf")
        make_pdf(self.site.source_root / "N01_X" / "TD_N01_X.pdf")
        resources = self.site.discover()
        manifest = pm.manifest_from_keys({("N01", "COURS", "COURS_N01_X.pdf")})
        state = pm.compute_publication_state(resources, manifest, self.site.docs_root)
        desired = {("N01", "TD", "TD_N01_X.pdf")}  # on décoche Cours, coche TD
        diff = pm.compute_publication_diff(state.items, desired)
        self.assertEqual([item.filename for item in diff.added], ["TD_N01_X.pdf"])
        self.assertEqual([item.filename for item in diff.removed], ["COURS_N01_X.pdf"])
        self.assertEqual(diff.unchanged_published, [])

    def test_validate_bloque_ressource_introuvable_partout(self):
        manifest = pm.manifest_from_keys({("N01", "COURS", "FANTOME.pdf")})
        state = pm.compute_publication_state([], manifest, self.site.docs_root)
        with self.assertRaises(pm.PublicationStateError):
            pm.validate_publication_state(state.items, {("N01", "COURS", "FANTOME.pdf")})


class ApplyPublicationStateTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.site = FakeSite(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_cas_6_run_sans_changement_zero_ecriture_zero_commit(self):
        make_pdf(self.site.source_root / "N01_X" / "COURS_N01_X.pdf")
        make_pdf(self.site.docs_root / "cours" / "COURS_N01_X.pdf")
        make_notion_page(
            self.site.docs_root / "notions" / "N01-x.md",
            "N01",
            "X",
            documents="- [Cours N01 — X](../cours/COURS_N01_X.pdf)",
        )
        resources = self.site.discover()
        manifest = pm.manifest_from_keys({("N01", "COURS", "COURS_N01_X.pdf")})
        self.site.manifest_path.write_bytes(
            pm.save_publication_manifest(self.site.manifest_path, manifest)
        )
        state = pm.compute_publication_state(resources, manifest, self.site.docs_root)
        desired = {item.key for item in state.items if item.published}

        result = pm.apply_publication_state(
            state.items,
            desired,
            self.site.docs_root,
            self.site.project_root,
            self.site.manifest_path,
            dry_run=False,
            skip_git_guards=True,
        )
        self.assertEqual(result.report.copied_files, [])
        self.assertEqual(
            modified_pages_of_interest(result, self.site.docs_root / "index.md"),
            set(),
        )
        self.assertFalse(result.manifest_changed)
        self.assertIsNone(result.commit_sha)

    def test_cas_4_ajout_ressource_regenere_autodocs_et_manifeste(self):
        make_pdf(self.site.source_root / "N01_X" / "COURS_N01_X.pdf")
        make_pdf(self.site.source_root / "N01_X" / "TD_N01_X.pdf")
        # Cours déjà publié = déjà copié physiquement (même contenu que la
        # source, sinon copy_resources le recopierait aussi).
        make_pdf(self.site.docs_root / "cours" / "COURS_N01_X.pdf")
        make_notion_page(
            self.site.docs_root / "notions" / "N01-x.md",
            "N01",
            "X",
            documents="- [Cours N01 — X](../cours/COURS_N01_X.pdf)",
        )
        resources = self.site.discover()
        manifest = pm.manifest_from_keys({("N01", "COURS", "COURS_N01_X.pdf")})
        state = pm.compute_publication_state(resources, manifest, self.site.docs_root)
        desired = {item.key for item in state.items}  # coche tout, dont le TD nouveau

        result = pm.apply_publication_state(
            state.items,
            desired,
            self.site.docs_root,
            self.site.project_root,
            self.site.manifest_path,
            dry_run=False,
            skip_git_guards=True,
        )
        self.assertEqual(len(result.report.copied_files), 1)
        self.assertTrue((self.site.docs_root / "td" / "TD_N01_X.pdf").is_file())
        saved_manifest = json.loads(self.site.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(
            saved_manifest["notions"]["N01"]["td"], ["TD_N01_X.pdf"]
        )

    def test_cas_3_ressource_absente_de_la_source_reste_publiee(self):
        make_pdf(self.site.docs_root / "cours" / "COURS_N09_Z.pdf")
        make_notion_page(
            self.site.docs_root / "notions" / "N09-z.md",
            "N09",
            "Z",
            documents="- [Cours N09 — Z](../cours/COURS_N09_Z.pdf)",
        )
        manifest = pm.manifest_from_keys({("N09", "COURS", "COURS_N09_Z.pdf")})
        state = pm.compute_publication_state([], manifest, self.site.docs_root)
        desired = {item.key for item in state.items if item.published}  # rien décoché

        result = pm.apply_publication_state(
            state.items,
            desired,
            self.site.docs_root,
            self.site.project_root,
            self.site.manifest_path,
            dry_run=False,
            skip_git_guards=True,
        )
        page_text = (self.site.docs_root / "notions" / "N09-z.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("COURS_N09_Z.pdf", page_text)
        self.assertEqual(
            modified_pages_of_interest(result, self.site.docs_root / "index.md"),
            set(),
        )  # la page de notion N09 est déjà à jour, rien réécrit

    def test_cas_10_retrait_explicite_preserve_texte_et_voir_aussi(self):
        make_pdf(self.site.source_root / "N01_X" / "COURS_N01_X.pdf")
        make_pdf(self.site.source_root / "N01_X" / "TD_N01_X.pdf")
        # Les deux sont déjà publiés : déjà copiés physiquement au préalable.
        make_pdf(self.site.docs_root / "cours" / "COURS_N01_X.pdf")
        make_pdf(self.site.docs_root / "td" / "TD_N01_X.pdf")
        make_notion_page(
            self.site.docs_root / "notions" / "N01-x.md",
            "N01",
            "X",
            documents=(
                "- [Cours N01 — X](../cours/COURS_N01_X.pdf)\n"
                "- [TD N01 — X](../td/TD_N01_X.pdf)"
            ),
            extra_after=(
                "## Voir aussi\n\n"
                "- PROLONGEMENT : [N02](N02-y.md) (lien vers la suite.)"
            ),
        )
        resources = self.site.discover()
        manifest = pm.manifest_from_keys(
            {("N01", "COURS", "COURS_N01_X.pdf"), ("N01", "TD", "TD_N01_X.pdf")}
        )
        state = pm.compute_publication_state(resources, manifest, self.site.docs_root)
        # Retrait explicite du TD.
        desired = {("N01", "COURS", "COURS_N01_X.pdf")}

        pm.apply_publication_state(
            state.items,
            desired,
            self.site.docs_root,
            self.site.project_root,
            self.site.manifest_path,
            dry_run=False,
            skip_git_guards=True,
        )
        page_text = (self.site.docs_root / "notions" / "N01-x.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Texte de présentation de N01.", page_text)
        self.assertIn("## Voir aussi", page_text)
        self.assertIn("PROLONGEMENT : [N02]", page_text)
        self.assertIn("COURS_N01_X.pdf", page_text)
        self.assertNotIn("TD_N01_X.pdf", page_text)
        # Le PDF physique n'est jamais supprimé par un simple retrait.
        self.assertTrue((self.site.docs_root / "td" / "TD_N01_X.pdf").is_file())

    def test_cas_13_echec_build_bloque_le_commit(self):
        make_pdf(self.site.source_root / "N01_X" / "COURS_N01_X.pdf")
        resources = self.site.discover()
        state = pm.compute_publication_state(resources, pm.empty_manifest(), self.site.docs_root)
        desired = {item.key for item in state.items}

        def failing_build(_project_root: Path) -> pm.BuildResult:
            return pm.BuildResult(ok=False, output="erreur simulée")

        result = pm.apply_publication_state(
            state.items,
            desired,
            self.site.docs_root,
            self.site.project_root,
            self.site.manifest_path,
            dry_run=False,
            build_runner=failing_build,
            skip_git_guards=True,
        )
        self.assertIsNone(result.commit_sha)
        self.assertIsNotNone(result.blocked_reason)


class ManifestDeterminismTests(unittest.TestCase):
    def test_ordre_stable_independant_de_l_ordre_d_entree(self):
        keys_a = {("N02", "TD", "b.pdf"), ("N01", "COURS", "a.pdf")}
        keys_b = {("N01", "COURS", "a.pdf"), ("N02", "TD", "b.pdf")}
        self.assertEqual(
            pm.save_publication_manifest(Path("x.json"), pm.manifest_from_keys(keys_a)),
            pm.save_publication_manifest(Path("x.json"), pm.manifest_from_keys(keys_b)),
        )

    def test_migration_bootstrap_reproduit_l_etat_deja_publie(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = FakeSite(Path(tmp))
            make_pdf(site.source_root / "N01_X" / "COURS_N01_X.pdf")
            make_pdf(site.source_root / "N01_X" / "TD_N01_X.pdf")
            make_pdf(site.docs_root / "cours" / "COURS_N01_X.pdf")
            # TD_N01_X n'est PAS listé dans le bloc AUTO-DOCS : orphelin
            # de fait, ne doit pas être considéré publié par la migration.
            make_notion_page(
                site.docs_root / "notions" / "N01-x.md",
                "N01",
                "X",
                documents="- [Cours N01 — X](../cours/COURS_N01_X.pdf)",
            )
            resources = site.discover()
            manifest = pm.bootstrap_manifest_from_auto_docs(resources, site.docs_root)
            self.assertEqual(
                manifest["notions"]["N01"], {"cours": ["COURS_N01_X.pdf"]}
            )

            # Rejouer l'état ainsi migré ne doit produire aucun changement.
            state = pm.compute_publication_state(resources, manifest, site.docs_root)
            desired = {item.key for item in state.items if item.published}
            result = pm.apply_publication_state(
                state.items,
                desired,
                site.docs_root,
                site.project_root,
                site.manifest_path,
                dry_run=True,
                skip_git_guards=True,
            )
            self.assertEqual(
                modified_pages_of_interest(
                    result,
                    site.docs_root / "index.md",
                    site.docs_root / "td" / "index.md",
                ),
                set(),
            )
            self.assertEqual(result.report.copied_files, [])


def run_git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, text=True, capture_output=True, check=True
    )


class GitGuardTests(unittest.TestCase):
    """CAS 9 et 12 : concurrence (working tree étranger, origin/main déplacé)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.remote = root / "remote.git"
        self.project_root = root / "site"
        self.remote.mkdir()
        run_git(self.remote, "init", "--bare", "-b", "main")
        run_git(root, "clone", str(self.remote), str(self.project_root))
        run_git(self.project_root, "config", "user.email", "test@example.invalid")
        run_git(self.project_root, "config", "user.name", "Test")
        (self.project_root / "README.md").write_text("init\n", encoding="utf-8")
        run_git(self.project_root, "add", "README.md")
        run_git(self.project_root, "commit", "-m", "init")
        run_git(self.project_root, "push", "-u", "origin", "main")

    def tearDown(self):
        self._tmp.cleanup()

    def test_cas_9_modification_etrangere_bloque(self):
        target = self.project_root / "docs_page.md"
        target.write_text("contenu étranger non commité\n", encoding="utf-8")
        conflicts = pm.foreign_conflict_paths(self.project_root, {target})
        self.assertEqual(conflicts, [target.resolve()])

    def test_cas_9_aucune_intersection_ne_bloque_pas(self):
        (self.project_root / "autre_fichier.md").write_text("étranger\n", encoding="utf-8")
        cible = self.project_root / "docs_page.md"
        conflicts = pm.foreign_conflict_paths(self.project_root, {cible})
        self.assertEqual(conflicts, [])

    def test_cas_12_origin_change_bloque(self):
        baseline_sha = pm.fetch_origin_main_sha(self.project_root)

        # Simuler un push externe pendant que le GUI était ouvert.
        other_clone = Path(self._tmp.name) / "other_clone"
        run_git(Path(self._tmp.name), "clone", str(self.remote), str(other_clone))
        run_git(other_clone, "config", "user.email", "test@example.invalid")
        run_git(other_clone, "config", "user.name", "Test")
        (other_clone / "ailleurs.md").write_text("changement externe\n", encoding="utf-8")
        run_git(other_clone, "add", "ailleurs.md")
        run_git(other_clone, "commit", "-m", "changement externe")
        run_git(other_clone, "push")

        with self.assertRaises(pm.ConcurrencyError):
            pm.ensure_origin_unchanged(self.project_root, baseline_sha)

    def test_cas_12_origin_inchange_ne_bloque_pas(self):
        baseline_sha = pm.fetch_origin_main_sha(self.project_root)
        pm.ensure_origin_unchanged(self.project_root, baseline_sha)  # ne lève pas


class GenericityTests(unittest.TestCase):
    """Section 7 de la demande : aucune dépendance à un nom de niveau."""

    FORBIDDEN_WORDS = ("seconde", "premiere", "première", "1stmg", "niveau_2nde")

    def test_moteur_fonctionne_sur_un_site_totalement_fictif(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "site-fictif-zeta"
            site = FakeSite(root)
            make_pdf(site.source_root / "N42_ZETA" / "COURS_N42_ZETA.pdf")
            make_notion_page(
                site.docs_root / "notions" / "N42-zeta.md", "N42", "Zeta"
            )
            resources = site.discover()
            self.assertEqual(len(resources), 1)

            manifest = pm.empty_manifest()
            state = pm.compute_publication_state(resources, manifest, site.docs_root)
            desired = {item.key for item in state.items}
            result = pm.apply_publication_state(
                state.items,
                desired,
                site.docs_root,
                site.project_root,
                site.manifest_path,
                dry_run=False,
                skip_git_guards=True,
            )
            self.assertEqual(len(result.report.copied_files), 1)
            self.assertTrue(site.manifest_path.is_file())

    def test_aucun_nom_de_niveau_code_en_dur_dans_le_moteur(self):
        source = Path(pm.__file__).read_text(encoding="utf-8").casefold()
        for word in self.FORBIDDEN_WORDS:
            self.assertNotIn(word, source, f"« {word} » ne doit pas apparaître dans {pm.__file__}")


if __name__ == "__main__":
    unittest.main()
