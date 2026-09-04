#!/usr/bin/env python3
"""État de publication du site : le manifeste et son application.

Ce module porte le nouveau modèle mental de l'outil de publication : les
cases à cocher (GUI) ou le manifeste (CLI) ne décrivent plus « que
publier maintenant » mais « quel doit être l'état final publié ». Une
ressource absente de la sélection courante n'est retirée du catalogue que
si elle était auparavant publiée ET n'est plus demandée explicitement —
jamais parce qu'elle n'a simplement pas été proposée cette fois-ci.

Aucune fonction ici ne dépend d'un niveau scolaire particulier : tous les
chemins sont reçus en paramètre (project_root, source_root, docs_root,
manifest_path), jamais recalculés depuis un module global. Un même
appelant peut donc réutiliser ce module pour n'importe quel site tant
qu'il lui fournit un ``config_site.yaml`` cohérent.
"""

from __future__ import annotations

import json
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from publier_ressources_site import (
    DESTINATION_DIRS,
    KIND_ORDER,
    PublicationReport,
    Resource,
    classify_pdf,
    commit_publication,
    copy_resources,
    ensure_inside_docs,
    update_index_quick_access,
    update_mkdocs_nav_if_safe,
    update_notion_pages,
    update_section_indexes,
)

MANIFEST_VERSION = 1

# Ordre canonique des clés dans le manifeste : stable, pour ne jamais
# produire de diff Git parasite entre deux exécutions équivalentes.
MANIFEST_KEY_ORDER = (
    "cours",
    "td",
    "automatismes",
    "minitest",
    "ds",
    "corrige",
    "corrige_td",
)
KIND_TO_MANIFEST_KEY = {
    "COURS": "cours",
    "TD": "td",
    "AUTOMATISMES": "automatismes",
    "MINITEST": "minitest",
    "DS": "ds",
    "CORRIGE": "corrige",
    "CORRIGE_TD": "corrige_td",
}
MANIFEST_KEY_TO_KIND = {value: key for key, value in KIND_TO_MANIFEST_KEY.items()}

ResourceKey = tuple[str, str, str]  # (notion, kind, filename)

STATUS_PUBLISHED_AVAILABLE = "published_available"  # CAS A
STATUS_NEW_AVAILABLE = "new_available"  # CAS B
STATUS_PUBLISHED_MISSING_SOURCE = "published_missing_source"  # CAS C

STATUS_LABELS = {
    STATUS_PUBLISHED_AVAILABLE: "publié",
    STATUS_NEW_AVAILABLE: "nouveau",
    STATUS_PUBLISHED_MISSING_SOURCE: "absent de la source ⚠",
}


class ManifestError(ValueError):
    """Le manifeste sur disque est illisible ou mal formé."""


class PublicationStateError(ValueError):
    """L'état de publication demandé est incohérent (fichier introuvable)."""


class ConcurrencyError(RuntimeError):
    """Le dépôt a changé depuis le chargement de l'écran/de l'état."""


@dataclass(frozen=True)
class PublicationItem:
    notion: str
    kind: str
    filename: str
    resource: Resource | None  # None si la source a disparu de CLAUDE (CAS C)
    published: bool  # présent dans le manifeste chargé
    docs_file_exists: bool
    status: str

    @property
    def key(self) -> ResourceKey:
        return (self.notion, self.kind, self.filename)


@dataclass(frozen=True)
class OrphanFile:
    """CAS D : présent dans docs/, ni publié, ni disponible dans la source."""

    kind: str | None
    notion: str | None
    path: Path


@dataclass(frozen=True)
class PublicationState:
    items: list[PublicationItem]
    orphans: list[OrphanFile]


@dataclass(frozen=True)
class PublicationDiff:
    added: list[PublicationItem]
    removed: list[PublicationItem]
    unchanged_published: list[PublicationItem]

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed)


@dataclass(frozen=True)
class BuildResult:
    ok: bool
    output: str


@dataclass
class ApplyResult:
    report: PublicationReport | None = None
    diff: PublicationDiff | None = None
    manifest_changed: bool = False
    build: BuildResult | None = None
    commit_sha: str | None = None
    blocked_reason: str | None = None


def _item_sort_key(item: PublicationItem) -> tuple:
    return (item.notion, KIND_ORDER[item.kind], item.filename.casefold())


# ---------------------------------------------------------------------------
# Manifeste : lecture, écriture, (dé)sérialisation
# ---------------------------------------------------------------------------


def empty_manifest() -> dict:
    return {"version": MANIFEST_VERSION, "notions": {}}


def load_publication_manifest(manifest_path: Path) -> dict:
    """Charger le manifeste, ou un manifeste vide s'il n'existe pas encore."""
    if not manifest_path.is_file():
        return empty_manifest()

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ManifestError(f"{manifest_path} : JSON invalide ({error})") from error

    if not isinstance(data, dict) or "notions" not in data:
        raise ManifestError(f"{manifest_path} : structure invalide (clé « notions » absente)")
    return data


def manifest_entries(manifest: dict) -> set[ResourceKey]:
    """Aplatir le manifeste en un ensemble de clés (notion, kind, filename)."""
    entries: set[ResourceKey] = set()
    for notion, kinds in manifest.get("notions", {}).items():
        for manifest_key, filenames in kinds.items():
            kind = MANIFEST_KEY_TO_KIND.get(manifest_key)
            if kind is None:
                raise ManifestError(f"Type de document inconnu dans le manifeste : {manifest_key}")
            for filename in filenames:
                entries.add((notion, kind, filename))
    return entries


def manifest_from_keys(keys: set[ResourceKey]) -> dict:
    """Construire un manifeste canonique (ordre stable) depuis un ensemble de clés."""
    by_notion: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for notion, kind, filename in keys:
        by_notion[notion][KIND_TO_MANIFEST_KEY[kind]].append(filename)

    notions: dict[str, dict[str, list[str]]] = {}
    for notion in sorted(by_notion):
        kinds: dict[str, list[str]] = {}
        for manifest_key in MANIFEST_KEY_ORDER:
            filenames = by_notion[notion].get(manifest_key)
            if filenames:
                kinds[manifest_key] = sorted(set(filenames), key=str.casefold)
        notions[notion] = kinds

    return {"version": MANIFEST_VERSION, "notions": notions}


def save_publication_manifest(manifest_path: Path, manifest: dict) -> bytes:
    """Sérialiser en JSON déterministe (clés triées, indentation stable)."""
    text = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    return text.encode("utf-8")


def write_publication_manifest_if_changed(
    manifest_path: Path, manifest: dict, dry_run: bool
) -> bool:
    new_bytes = save_publication_manifest(manifest_path, manifest)
    old_bytes = manifest_path.read_bytes() if manifest_path.is_file() else None
    if new_bytes == old_bytes:
        return False
    if not dry_run:
        manifest_path.write_bytes(new_bytes)
    return True


# ---------------------------------------------------------------------------
# État de publication : CAS A/B/C/D
# ---------------------------------------------------------------------------


def find_orphan_files(
    resources: list[Resource],
    manifest: dict,
    docs_root: Path,
) -> list[OrphanFile]:
    """CAS D : PDF présents dans docs/, ni publiés, ni découverts dans la source."""
    known_keys = manifest_entries(manifest) | {
        (resource.notion, resource.kind, resource.source.name) for resource in resources
    }
    known_destinations = {
        docs_root / DESTINATION_DIRS[kind] / filename for (_, kind, filename) in known_keys
    }

    orphans: list[OrphanFile] = []
    for directory_name in sorted(set(DESTINATION_DIRS.values())):
        directory = docs_root / directory_name
        if not directory.is_dir():
            continue
        ensure_inside_docs(directory, docs_root)
        for path in sorted(directory.rglob("*.pdf"), key=lambda item: str(item).casefold()):
            if not path.is_file() or path in known_destinations:
                continue
            classification = classify_pdf(path)
            kind, notion = classification if classification else (None, None)
            orphans.append(OrphanFile(kind=kind, notion=notion, path=path))
    return orphans


def compute_publication_state(
    resources: list[Resource],
    manifest: dict,
    docs_root: Path,
) -> PublicationState:
    """Croiser ressources disponibles (source) et manifeste (état publié)."""
    entries = manifest_entries(manifest)
    by_key: dict[ResourceKey, Resource] = {
        (resource.notion, resource.kind, resource.source.name): resource
        for resource in resources
    }

    items: list[PublicationItem] = []
    for key, resource in by_key.items():
        notion, kind, filename = key
        published = key in entries
        docs_path = docs_root / DESTINATION_DIRS[kind] / filename
        items.append(
            PublicationItem(
                notion=notion,
                kind=kind,
                filename=filename,
                resource=resource,
                published=published,
                docs_file_exists=docs_path.is_file(),
                status=(
                    STATUS_PUBLISHED_AVAILABLE if published else STATUS_NEW_AVAILABLE
                ),
            )
        )

    for key in entries - set(by_key):
        notion, kind, filename = key
        docs_path = docs_root / DESTINATION_DIRS[kind] / filename
        items.append(
            PublicationItem(
                notion=notion,
                kind=kind,
                filename=filename,
                resource=None,
                published=True,
                docs_file_exists=docs_path.is_file(),
                status=STATUS_PUBLISHED_MISSING_SOURCE,
            )
        )

    items.sort(key=_item_sort_key)
    orphans = find_orphan_files(resources, manifest, docs_root)
    return PublicationState(items=items, orphans=orphans)


def compute_publication_diff(
    items: list[PublicationItem],
    desired_keys: set[ResourceKey],
) -> PublicationDiff:
    """CAS déjà publié vs CAS souhaité : ajouts / retraits / inchangés."""
    added = sorted(
        (item for item in items if item.key in desired_keys and not item.published),
        key=_item_sort_key,
    )
    removed = sorted(
        (item for item in items if item.key not in desired_keys and item.published),
        key=_item_sort_key,
    )
    unchanged = sorted(
        (item for item in items if item.key in desired_keys and item.published),
        key=_item_sort_key,
    )
    return PublicationDiff(added=added, removed=removed, unchanged_published=unchanged)


def validate_publication_state(
    items: list[PublicationItem],
    desired_keys: set[ResourceKey],
) -> None:
    """CAS C limite : bloquer si une ressource maintenue publiée n'existe nulle part."""
    by_key = {item.key: item for item in items}
    unresolved = [
        key
        for key in desired_keys
        if key in by_key
        and by_key[key].resource is None
        and not by_key[key].docs_file_exists
    ]
    missing_entirely = [key for key in desired_keys if key not in by_key]
    problems = unresolved + missing_entirely
    if problems:
        details = ", ".join(f"{notion}/{kind}/{filename}" for notion, kind, filename in sorted(problems))
        raise PublicationStateError(
            "Ressource(s) référencée(s) mais introuvable(s) (ni dans la source, "
            f"ni dans docs/) : {details}"
        )


# ---------------------------------------------------------------------------
# Git : garde-fous de concurrence (#18, #19)
# ---------------------------------------------------------------------------


def _run_git(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )


def _git_output(completed: subprocess.CompletedProcess[str]) -> str:
    return "\n".join(
        part.strip() for part in (completed.stdout, completed.stderr) if part.strip()
    )


def fetch_origin_main_sha(project_root: Path, branch: str = "main") -> str:
    """``git fetch origin`` puis renvoyer le SHA d'``origin/<branch>``."""
    fetch = _run_git(project_root, "fetch", "origin")
    if fetch.returncode != 0:
        raise ConcurrencyError(f"git fetch origin a échoué :\n{_git_output(fetch)}")
    rev = _run_git(project_root, "rev-parse", "--verify", f"origin/{branch}")
    if rev.returncode != 0:
        raise ConcurrencyError(f"origin/{branch} introuvable :\n{_git_output(rev)}")
    return rev.stdout.strip()


def ensure_origin_unchanged(
    project_root: Path, expected_sha: str, branch: str = "main"
) -> None:
    """#18 : refuser d'écrire si origin/<branch> a bougé depuis le chargement."""
    current_sha = fetch_origin_main_sha(project_root, branch)
    if current_sha != expected_sha:
        raise ConcurrencyError(
            f"origin/{branch} a changé depuis l'ouverture "
            f"({expected_sha[:12]} → {current_sha[:12]}) : actualisez avant "
            "d'appliquer les changements."
        )


def foreign_conflict_paths(project_root: Path, candidate_paths: set[Path]) -> list[Path]:
    """#19 : fichiers déjà modifiés (hors de cette exécution) parmi les cibles."""
    if not candidate_paths:
        return []
    status = _run_git(
        project_root, "status", "--porcelain", "--", *[str(path) for path in candidate_paths]
    )
    if status.returncode != 0:
        raise ConcurrencyError(f"git status a échoué :\n{_git_output(status)}")

    conflicts: list[Path] = []
    for line in status.stdout.splitlines():
        if not line.strip():
            continue
        raw_path = line[3:].split(" -> ")[-1].strip().strip('"')
        conflicts.append((project_root / raw_path).resolve())
    return sorted(conflicts)


# ---------------------------------------------------------------------------
# Application de l'état demandé
# ---------------------------------------------------------------------------


def build_apply_report(
    items: list[PublicationItem],
    desired_keys: set[ResourceKey],
    docs_root: Path,
) -> tuple[list[Resource], list[Resource]]:
    """Renvoyer (ressources pertinentes, ressources à publier).

    Un CAS C maintenu publié (source disparue de CLAUDE) n'a plus de
    fichier source réel : on synthétise un ``Resource`` dont la source ET
    la destination pointent vers le PDF déjà présent dans docs/, pour que
    le rendu des blocs AUTO-DOCS (qui ne lit que kind/notion/destination)
    fonctionne sans avoir à distinguer ce cas.
    """
    by_key = {item.key: item for item in items}
    all_relevant: list[Resource] = []
    selected: list[Resource] = []
    for key in desired_keys:
        item = by_key[key]
        if item.resource is not None:
            resource = item.resource
        else:
            docs_path = docs_root / DESTINATION_DIRS[item.kind] / item.filename
            resource = Resource(
                source=docs_path,
                destination=docs_path,
                kind=item.kind,
                notion=item.notion,
            )
        selected.append(resource)
        all_relevant.append(resource)
    for item in items:
        if item.resource is not None and item.key not in desired_keys:
            all_relevant.append(item.resource)
    return all_relevant, selected


def apply_publication_state(
    items: list[PublicationItem],
    desired_keys: set[ResourceKey],
    docs_root: Path,
    project_root: Path,
    manifest_path: Path,
    dry_run: bool,
    build_runner: Callable[[Path], BuildResult] | None = None,
    skip_git_guards: bool = False,
    origin_sha_at_load: str | None = None,
    pdf_count: int = 0,
    ignored_pdf_count: int = 0,
) -> ApplyResult:
    """Appliquer l'état demandé : copie, AUTO-DOCS, manifeste, build, commit."""
    validate_publication_state(items, desired_keys)
    diff = compute_publication_diff(items, desired_keys)

    all_relevant_resources, selected_resources = build_apply_report(
        items, desired_keys, docs_root
    )

    touched_notions = {item.notion for item in (*diff.added, *diff.removed)}
    new_manifest = manifest_from_keys(desired_keys)
    manifest_will_change = save_publication_manifest(
        manifest_path, new_manifest
    ) != (manifest_path.read_bytes() if manifest_path.is_file() else None)

    if not skip_git_guards and (touched_notions or manifest_will_change):
        if origin_sha_at_load is not None:
            ensure_origin_unchanged(project_root, origin_sha_at_load)

        candidate_paths: set[Path] = {manifest_path}
        for resource in diff_target_resources(diff, docs_root):
            candidate_paths.add(resource)
        candidate_paths |= notion_page_candidates(touched_notions, docs_root)

        conflicts = foreign_conflict_paths(project_root, candidate_paths)
        if conflicts:
            displayed = ", ".join(
                str(path.relative_to(project_root)) if path.is_relative_to(project_root) else str(path)
                for path in conflicts
            )
            return ApplyResult(
                diff=diff,
                blocked_reason=(
                    "Modification(s) étrangère(s) déjà présente(s) sur des fichiers "
                    f"que cette publication doit modifier : {displayed}. "
                    "Réglez la situation Git avant de continuer."
                ),
            )

    report = PublicationReport(
        pdf_count=pdf_count or len(all_relevant_resources),
        ignored_pdf_count=ignored_pdf_count,
        resources=all_relevant_resources,
        selected_resources=selected_resources,
        dry_run=dry_run,
    )

    copy_resources(
        [resource for resource in selected_resources if resource.source != resource.destination],
        report,
    )
    update_notion_pages(
        all_relevant_resources, selected_resources, docs_root, report, considered_kinds=None
    )
    update_section_indexes(
        all_relevant_resources, selected_resources, docs_root, report, considered_kinds=None
    )
    update_index_quick_access(docs_root, report)
    update_mkdocs_nav_if_safe(docs_root, project_root, report)

    manifest_changed = write_publication_manifest_if_changed(
        manifest_path, new_manifest, dry_run
    )

    if dry_run:
        return ApplyResult(report=report, diff=diff, manifest_changed=manifest_changed)

    runner = build_runner or default_mkdocs_build_runner
    build_result = runner(project_root)
    if not build_result.ok:
        return ApplyResult(
            report=report,
            diff=diff,
            manifest_changed=manifest_changed,
            build=build_result,
            blocked_reason="mkdocs build --strict a échoué : aucun commit n'a été créé.",
        )

    commit_sha = commit_publication(
        report, project_root, extra_paths=(manifest_path,) if manifest_changed else ()
    )

    return ApplyResult(
        report=report,
        diff=diff,
        manifest_changed=manifest_changed,
        build=build_result,
        commit_sha=commit_sha,
    )


def diff_target_resources(diff: PublicationDiff, docs_root: Path) -> set[Path]:
    paths: set[Path] = set()
    for item in (*diff.added, *diff.removed):
        paths.add(docs_root / DESTINATION_DIRS[item.kind] / item.filename)
    return paths


def notion_page_candidates(notions: set[str], docs_root: Path) -> set[Path]:
    from publier_ressources_site import find_notion_page

    paths: set[Path] = set()
    for notion in notions:
        try:
            page = find_notion_page(docs_root, notion)
        except ValueError:
            continue
        if page is not None:
            paths.add(page)
    for directory_name in ("td", "automatismes", "corriges"):
        candidate = docs_root / directory_name / "index.md"
        if candidate.is_file():
            paths.add(candidate)
    return paths


def default_mkdocs_build_runner(project_root: Path) -> BuildResult:
    import shutil

    executable = (
        str(project_root / ".venv" / "bin" / "mkdocs")
        if (project_root / ".venv" / "bin" / "mkdocs").is_file()
        else shutil.which("mkdocs")
    )
    if executable is None:
        return BuildResult(ok=False, output="mkdocs introuvable (ni .venv, ni PATH).")
    completed = subprocess.run(
        [executable, "build", "--strict"],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )
    output = "\n".join(
        part.strip() for part in (completed.stdout, completed.stderr) if part.strip()
    )
    return BuildResult(ok=completed.returncode == 0, output=output)


# ---------------------------------------------------------------------------
# Migration : reconstruire le manifeste depuis l'état publié actuel
# ---------------------------------------------------------------------------


def bootstrap_manifest_from_auto_docs(
    resources: list[Resource], docs_root: Path
) -> dict:
    """Reconstruire un manifeste à partir de ce qui est déjà référencé.

    Un document est considéré publié s'il apparaît dans un bloc AUTO-DOCS
    déjà en ligne — jamais simplement parce qu'un PDF homonyme existe dans
    docs/ (des orphelins y existent volontairement, cf. CAS D). On ne
    relit donc pas les fichiers, on réutilise le lien effectivement
    présent.

    Deux emplacements sont vérifiés, car selon le site un type de document
    peut n'apparaître que sur l'un des deux (certains sites ne listent
    les corrigés que sur docs/corriges/index.md, jamais sur la page de
    la notion elle-même) :
    - la page de SA notion (docs/notions/Nxx-*.md) ;
    - la page d'index de SA section (docs/<dossier>/index.md, le même
      dossier que sa destination), si elle existe.
    """
    from publier_ressources_site import (
        AUTO_DOCS_END,
        AUTO_DOCS_START,
        find_notion_page,
    )

    def contains_in_auto_docs_zone(text: str, filename: str) -> bool:
        if AUTO_DOCS_START not in text or AUTO_DOCS_END not in text:
            return False
        zone = text[
            text.index(AUTO_DOCS_START) + len(AUTO_DOCS_START) : text.index(AUTO_DOCS_END)
        ]
        return filename in zone

    keys: set[ResourceKey] = set()
    notion_pages_cache: dict[str, str] = {}
    section_pages_cache: dict[Path, str] = {}

    for resource in resources:
        notion = resource.notion
        if notion not in notion_pages_cache:
            try:
                page = find_notion_page(docs_root, notion)
            except ValueError:
                page = None
            notion_pages_cache[notion] = (
                page.read_text(encoding="utf-8") if page and page.is_file() else ""
            )

        published = contains_in_auto_docs_zone(
            notion_pages_cache[notion], resource.destination.name
        )

        if not published:
            section_page = resource.destination.parent / "index.md"
            if section_page not in section_pages_cache:
                section_pages_cache[section_page] = (
                    section_page.read_text(encoding="utf-8")
                    if section_page.is_file()
                    else ""
                )
            published = contains_in_auto_docs_zone(
                section_pages_cache[section_page], resource.destination.name
            )

        if published:
            keys.add((resource.notion, resource.kind, resource.source.name))

    return manifest_from_keys(keys)
