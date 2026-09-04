#!/usr/bin/env python3
"""Publier les PDF de travail dans la documentation MkDocs."""

from __future__ import annotations

import argparse
import filecmp
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote


sys.path.insert(0, str(Path(__file__).resolve().parent))
from synchronisation.config import charger_configuration  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = PROJECT_ROOT / "docs"
_CONFIG = charger_configuration(PROJECT_ROOT / "config_site.yaml")
SOURCE_ROOT = _CONFIG.source
NIVEAU = _CONFIG.niveau
MANIFEST_PATH = PROJECT_ROOT / "publication_manifest.json"

AUTO_DOCS_START = "<!-- AUTO-DOCS:START -->"
AUTO_DOCS_END = "<!-- AUTO-DOCS:END -->"

DESTINATION_DIRS = {
    "COURS": "cours",
    "TD": "td",
    "CORRIGE_TD": "corriges",
    "CORRIGE": "corriges",
    "AUTOMATISMES": "automatismes",
    "MINITEST": "automatismes",
    "DS": "ds",
}

LABELS = {
    "COURS": "Cours",
    "TD": "TD",
    "CORRIGE_TD": "Corrigé TD",
    "CORRIGE": "Corrigé",
    "AUTOMATISMES": "Automatismes",
    "MINITEST": "Mini-test",
    "DS": "DS",
}

# Formulations pédagogiques des thèmes actuellement publiés. Si un nouveau
# thème n'est pas encore répertorié ici, le titre de la page Markdown sert de
# repli afin de ne jamais afficher le nom technique du fichier en majuscules.
TOPIC_TITLES = {
    "RENTREE_DIAGNOSTIC_LOGIQUE_INTERVALLES": (
        "Rentrée : diagnostic, logique et intervalles"
    ),
    "SECOND_DEGRE_FONCTION_CARRE_FORME_CANONIQUE": (
        "Second degré : fonction carré et forme canonique"
    ),
    "PARTIE_1_FORMES_RACINES_SIGNE_DISCRIMINANT": (
        "Second degré (partie 1) : formes, racines, signe et discriminant"
    ),
    "PARTIE_2_INEQUATIONS_OPTIMISATION_PROBLEMES": (
        "Second degré (partie 2) : inéquations, optimisation et problèmes"
    ),
    "PRODUIT_SCALAIRE_DEFINITION_PROJECTION_COORDONNEES": (
        "Produit scalaire : définition, projection et coordonnées"
    ),
    "PRODUIT_SCALAIRE_IDENTITES_AL_KASHI_LIEUX_POINTS": (
        "Produit scalaire : identités, Al-Kashi et lieux de points"
    ),
}

KIND_ORDER = {
    "COURS": 0,
    "TD": 1,
    "AUTOMATISMES": 2,
    "MINITEST": 3,
    "DS": 4,
    "CORRIGE": 5,
    "CORRIGE_TD": 6,
}

SAFE_DEFAULT_KINDS = frozenset({"COURS", "TD"})

# Dossiers non publiables à ignorer partout sous source_root, quel que soit
# le niveau d'imbrication (archives et sauvegardes locales de travail).
IGNORED_DIR_NAME_PATTERN = re.compile(
    r"^_(ANCIEN|ARCHIVE|SAUVEGARDE)", re.IGNORECASE
)

# CORRIGE_TD doit être testé avant CORRIGE afin de conserver deux choix
# distincts dans l'interface, tout en envoyant les deux vers docs/corriges.
RESOURCE_PATTERNS = (
    (
        "CORRIGE_TD",
        re.compile(
            r"^CORRIG(?:E|É)_TD_N(?P<number>\d{2})(?:_|$)",
            re.IGNORECASE,
        ),
    ),
    (
        "CORRIGE",
        re.compile(
            r"^CORRIG(?:E|É)_N(?P<number>\d{2})(?:_|$)",
            re.IGNORECASE,
        ),
    ),
    (
        "COURS",
        re.compile(r"^COURS_N(?P<number>\d{2})(?:_|$)", re.IGNORECASE),
    ),
    (
        "TD",
        re.compile(r"^TD_N(?P<number>\d{2})(?:_|$)", re.IGNORECASE),
    ),
    (
        "AUTOMATISMES",
        re.compile(
            r"^AUTOMATISMES_N(?P<number>\d{2})(?:_|$)",
            re.IGNORECASE,
        ),
    ),
    (
        "MINITEST",
        re.compile(r"^MINITEST_N(?P<number>\d{2})(?:_|$)", re.IGNORECASE),
    ),
    (
        "DS",
        re.compile(r"^DS_N(?P<number>\d{2})(?:_|$)", re.IGNORECASE),
    ),
)


@dataclass(frozen=True)
class Resource:
    source: Path
    destination: Path
    kind: str
    notion: str


@dataclass
class PublicationReport:
    pdf_count: int = 0
    ignored_pdf_count: int = 0
    resources: list[Resource] = field(default_factory=list)
    selected_resources: list[Resource] = field(default_factory=list)
    ignored_resources: list[Resource] = field(default_factory=list)
    copied_files: list[Path] = field(default_factory=list)
    unchanged_files: list[Path] = field(default_factory=list)
    modified_pages: list[Path] = field(default_factory=list)
    unchanged_pages: list[Path] = field(default_factory=list)
    present_unselected_files: list[Path] = field(default_factory=list)
    missing_pages: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    dry_run: bool = False


def classify_pdf(path: Path) -> tuple[str, str] | None:
    """Retourner (type, notion) si le nom du PDF est reconnu."""
    if path.suffix.casefold() != ".pdf":
        return None

    for kind, pattern in RESOURCE_PATTERNS:
        match = pattern.match(path.stem)
        if match:
            return kind, f"N{match.group('number')}"
    return None


def ensure_inside_docs(path: Path, docs_root: Path) -> None:
    """Interdire toute destination qui sortirait de docs/, même par symlink."""
    resolved_docs = docs_root.resolve()
    resolved_path = path.resolve(strict=False)
    if not resolved_path.is_relative_to(resolved_docs):
        raise ValueError(f"Destination interdite hors de docs/ : {path}")


def discover_resources(
    source_root: Path, docs_root: Path
) -> tuple[list[Resource], int, int]:
    """Rechercher récursivement les PDF et construire leurs destinations."""
    resources: list[Resource] = []
    pdf_count = 0
    ignored_pdf_count = 0

    for path in sorted(source_root.rglob("*"), key=lambda item: str(item).casefold()):
        if not path.is_file() or path.suffix.casefold() != ".pdf":
            continue

        relative_dirs = path.relative_to(source_root).parent.parts
        if any(IGNORED_DIR_NAME_PATTERN.match(part) for part in relative_dirs):
            continue

        pdf_count += 1
        classification = classify_pdf(path)
        if classification is None:
            ignored_pdf_count += 1
            continue

        kind, notion = classification
        destination = docs_root / DESTINATION_DIRS[kind] / path.name
        ensure_inside_docs(destination, docs_root)
        resources.append(Resource(path, destination, kind, notion))

    destinations: dict[Path, Path] = {}
    for resource in resources:
        previous_source = destinations.setdefault(
            resource.destination, resource.source
        )
        if previous_source != resource.source:
            raise ValueError(
                "Deux PDF auraient la même destination : "
                f"{previous_source} et {resource.source}"
            )

    return resources, pdf_count, ignored_pdf_count


def copy_resources(resources: list[Resource], report: PublicationReport) -> None:
    """Copier uniquement les PDF absents ou dont le contenu diffère."""
    for resource in resources:
        destination = resource.destination

        if (
            destination.exists()
            and destination.is_file()
            and filecmp.cmp(resource.source, destination, shallow=False)
        ):
            report.unchanged_files.append(destination)
            continue

        if not report.dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(resource.source, destination)
        report.copied_files.append(destination)


def find_notion_page(docs_root: Path, notion: str) -> Path | None:
    """Trouver l'unique page docs/notions/Nxx-*.md."""
    matches = sorted((docs_root / "notions").glob(f"{notion}-*.md"))
    if not matches:
        return None
    if len(matches) > 1:
        names = ", ".join(str(path) for path in matches)
        raise ValueError(f"Plusieurs pages correspondent à {notion} : {names}")
    return matches[0]


def slugify(text: str) -> str:
    """Transformer un intitulé lisible en fragment sûr pour une URL."""
    normalized = unicodedata.normalize("NFKD", text.casefold())
    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
    slug = re.sub(r"[\W_]+", "-", without_accents).strip("-")
    return slug or "ressources"


def humanize_topic_slug(topic_slug: str | None) -> str | None:
    """Transformer un identifiant technique en intitulé lisible."""
    if topic_slug is None:
        return None

    normalized_slug = topic_slug.strip().upper()
    known_topics = {
        "SECOND_DEGRE_I": "Second degré I",
        "SECOND_DEGRE_II": "Second degré II",
        "PRODUIT_SCALAIRE_I": "Produit scalaire I",
        "PRODUIT_SCALAIRE_II": "Produit scalaire II",
    }
    if normalized_slug in known_topics:
        return known_topics[normalized_slug]

    words = topic_slug.replace("_", " ").split()
    if not words:
        return None
    return " ".join(word.capitalize() for word in words)


def topic_from_parent_directory(resource: Resource) -> str | None:
    """Déduire le sujet depuis un dossier tel que N05_SECOND_DEGRE_I."""
    match = re.fullmatch(
        r"N\d{2}_(.+)",
        resource.source.parent.name,
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    return humanize_topic_slug(match.group(1))


def topic_slug_from_filename(path: Path) -> str | None:
    """Extraire la partie descriptive située après Nxx dans le nom."""
    match = re.search(r"(?:^|_)N\d{2}(?:_|$)", path.stem, re.IGNORECASE)
    if match is None or match.end() == len(path.stem):
        return None
    return path.stem[match.end():].upper()


def notion_topic_from_heading(text: str, notion: str) -> str | None:
    """Extraire le sujet lisible depuis un titre « # Nxx — Sujet »."""
    heading = re.search(
        rf"^#[ \t]+{re.escape(notion)}[ \t]+(?:—|-)[ \t]+(.+?)[ \t]*\r?$",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    return heading.group(1).strip() if heading else None


def topic_title_for_resource(
    resource: Resource,
    fallback_topic: str | None = None,
) -> str | None:
    topic_slug = topic_slug_from_filename(resource.source)
    return TOPIC_TITLES.get(topic_slug or "", fallback_topic)


def topic_for_new_notion_page(
    notion: str,
    resources: list[Resource],
) -> str:
    """Choisir le meilleur intitulé disponible pour une nouvelle page."""
    notion_resources = [
        resource for resource in resources if resource.notion == notion
    ]
    for resource in notion_resources:
        topic = topic_title_for_resource(resource)
        if topic:
            return topic
    for resource in notion_resources:
        topic = topic_from_parent_directory(resource)
        if topic:
            return topic
    return "Ressources"


def default_notion_page_path(
    docs_root: Path,
    notion: str,
    resources: list[Resource],
) -> Path:
    """Construire le chemin par défaut d'une nouvelle page de notion."""
    topic = topic_for_new_notion_page(notion, resources)
    return docs_root / "notions" / f"{notion}-{slugify(topic)}.md"


def notion_page_title(path: Path) -> str:
    """Lire le premier titre principal, ou reprendre le nom du fichier."""
    if not path.is_file():
        return path.stem

    text = path.read_bytes().decode("utf-8")
    heading = re.search(
        r"^#[ \t]+(.+?)[ \t]*\r?$",
        text,
        flags=re.MULTILINE,
    )
    return heading.group(1).strip() if heading else path.stem


def notion_number_from_page(path: Path) -> int:
    """Extraire le numéro de notion depuis un nom Nxx-*.md."""
    match = re.match(r"^N(?P<number>\d{2})-", path.name, re.IGNORECASE)
    if match is None:
        raise ValueError(f"Nom de page de notion invalide : {path}")
    return int(match.group("number"))


def list_notion_pages(docs_root: Path) -> list[Path]:
    """Lister les pages de notions dans leur ordre numérique."""
    pages = [
        path
        for path in (docs_root / "notions").glob("N[0-9][0-9]-*.md")
        if path.is_file()
    ]
    for path in pages:
        ensure_inside_docs(path, docs_root)
    return sorted(
        pages,
        key=lambda path: (
            notion_number_from_page(path),
            path.name.casefold(),
        ),
    )


def notion_pages_for_update(
    docs_root: Path,
    report: PublicationReport,
) -> list[Path]:
    """Inclure les pages qui seraient créées pendant un dry-run."""
    pages = set(list_notion_pages(docs_root))
    notions_dir = docs_root / "notions"
    for path in report.modified_pages:
        try:
            relative_path = path.relative_to(notions_dir)
        except ValueError:
            continue
        if (
            relative_path.parent == Path(".")
            and re.fullmatch(
                r"N\d{2}-.+\.md",
                relative_path.name,
                flags=re.IGNORECASE,
            )
        ):
            ensure_inside_docs(path, docs_root)
            pages.add(path)
    return sorted(
        pages,
        key=lambda path: (
            notion_number_from_page(path),
            path.name.casefold(),
        ),
    )


def add_modified_page(report: PublicationReport, path: Path) -> None:
    """Ajouter une modification au rapport sans doublon."""
    if path not in report.modified_pages:
        report.modified_pages.append(path)


def markdown_link_targets(text: str) -> set[str]:
    """Extraire les destinations simples des liens Markdown."""
    return {
        match.group("target").strip("<>")
        for match in re.finditer(
            r"\]\(\s*(?P<target><?[^)\s>]+>?)",
            text,
        )
    }


def update_index_quick_access(
    docs_root: Path,
    report: PublicationReport,
) -> None:
    """Ajouter les pages de notions manquantes à l'accès rapide."""
    index_path = docs_root / "index.md"
    ensure_inside_docs(index_path, docs_root)
    original_bytes = index_path.read_bytes()
    original_text = original_bytes.decode("utf-8")
    newline = detect_newline(original_text)

    existing_targets = markdown_link_targets(original_text)
    missing_links = []
    for page in notion_pages_for_update(docs_root, report):
        relative_path = page.relative_to(docs_root).as_posix()
        if relative_path not in existing_targets:
            missing_links.append(
                f"- [{notion_page_title(page)}]({relative_path})"
            )

    headings = list(
        re.finditer(
            r"^##[ \t]+Accès rapide[ \t]*\r?$",
            original_text,
            flags=re.MULTILINE | re.IGNORECASE,
        )
    )
    if headings and not missing_links:
        return

    if not headings:
        block = "## Accès rapide"
        if missing_links:
            block += f"{newline}{newline}{newline.join(missing_links)}"

        if not original_text:
            updated_text = block
        else:
            had_final_newline = original_text.endswith(("\n", "\r"))
            separator = newline if had_final_newline else newline * 2
            updated_text = f"{original_text}{separator}{block}"
            if had_final_newline:
                updated_text += newline
    else:
        heading = headings[0]
        heading_line_end = original_text.find(newline, heading.end())
        content_start = (
            len(original_text)
            if heading_line_end == -1
            else heading_line_end + len(newline)
        )
        next_heading = re.search(
            r"^#{1,2}[ \t]+",
            original_text[content_start:],
            flags=re.MULTILINE,
        )
        section_end = (
            len(original_text)
            if next_heading is None
            else content_start + next_heading.start()
        )

        section_text = original_text[content_start:section_end]
        section_core = section_text.rstrip("\r\n")
        trailing_newlines = section_text[len(section_core):]
        links_text = newline.join(missing_links)
        if section_core:
            replacement = f"{section_core}{newline}{links_text}"
        else:
            replacement = f"{newline}{links_text}"

        # Garder une ligne vide avant la section Markdown suivante.
        if section_end < len(original_text):
            newline_count = len(trailing_newlines) // len(newline)
            if newline_count < 2:
                trailing_newlines = newline * 2
        replacement += trailing_newlines
        updated_text = (
            original_text[:content_start]
            + replacement
            + original_text[section_end:]
        )

    updated_bytes = updated_text.encode("utf-8")
    if updated_bytes == original_bytes:
        return
    if not report.dry_run:
        index_path.write_bytes(updated_bytes)
    add_modified_page(report, index_path)


def mkdocs_nav_warning(
    report: PublicationReport,
    mkdocs_path: Path,
    reason: str,
) -> None:
    report.warnings.append(
        f"{mkdocs_path}: menu « Notions » non modifié ({reason})"
    )


def yaml_nav_label(title: str, quote_style: str) -> str:
    """Reprendre le style de citation des clés YAML déjà présentes."""
    if quote_style == "double":
        escaped = title.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if quote_style == "single":
        escaped = title.replace("'", "''")
        return f"'{escaped}'"
    if ":" not in title and not title.startswith(("-", "?", ":")):
        return title
    escaped = title.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def update_mkdocs_nav_if_safe(
    docs_root: Path,
    project_root: Path,
    report: PublicationReport,
) -> None:
    """Compléter un menu Notions plat uniquement s'il est non ambigu."""
    mkdocs_path = project_root / "mkdocs.yml"
    if not mkdocs_path.is_file():
        mkdocs_nav_warning(report, mkdocs_path, "fichier introuvable")
        return
    if not mkdocs_path.resolve().is_relative_to(project_root.resolve()):
        mkdocs_nav_warning(report, mkdocs_path, "chemin hors du projet")
        return

    original_bytes = mkdocs_path.read_bytes()
    original_text = original_bytes.decode("utf-8")
    newline = detect_newline(original_text)
    lines = original_text.splitlines(keepends=True)

    nav_indexes = [
        index
        for index, line in enumerate(lines)
        if re.fullmatch(
            r"(?P<indent> *)nav:[ \t]*(?:#.*)?(?:\r?\n)?",
            line,
        )
    ]
    if len(nav_indexes) != 1:
        mkdocs_nav_warning(report, mkdocs_path, "bloc nav ambigu ou absent")
        return

    nav_index = nav_indexes[0]
    nav_indent = len(lines[nav_index]) - len(lines[nav_index].lstrip(" "))
    nav_end = len(lines)
    for index in range(nav_index + 1, len(lines)):
        stripped = lines[index].strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(lines[index]) - len(lines[index].lstrip(" "))
        if indent <= nav_indent:
            nav_end = index
            break

    notion_header_pattern = re.compile(
        r'(?P<indent> *)-[ \t]+(?:"Notions"|\'Notions\'|Notions)'
        r':[ \t]*(?:#.*)?(?:\r?\n)?'
    )
    notion_indexes = [
        index
        for index in range(nav_index + 1, nav_end)
        if notion_header_pattern.fullmatch(lines[index])
    ]
    if len(notion_indexes) != 1:
        mkdocs_nav_warning(
            report,
            mkdocs_path,
            "bloc Notions ambigu ou absent",
        )
        return

    notion_index = notion_indexes[0]
    notion_indent = (
        len(lines[notion_index])
        - len(lines[notion_index].lstrip(" "))
    )
    if notion_indent <= nav_indent:
        mkdocs_nav_warning(report, mkdocs_path, "indentation incohérente")
        return

    block_end = nav_end
    for index in range(notion_index + 1, nav_end):
        stripped = lines[index].strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(lines[index]) - len(lines[index].lstrip(" "))
        if indent <= notion_indent:
            block_end = index
            break

    entry_indexes = []
    entry_indents = set()
    for index in range(notion_index + 1, block_end):
        stripped = lines[index].strip()
        if not stripped or stripped.startswith("#"):
            continue
        if lines[index][: len(lines[index]) - len(lines[index].lstrip())].find(
            "\t"
        ) != -1:
            mkdocs_nav_warning(report, mkdocs_path, "tabulation YAML")
            return
        indent = len(lines[index]) - len(lines[index].lstrip(" "))
        if (
            indent <= notion_indent
            or not re.fullmatch(r"-[ \t]+.+:[ \t]+\S+.*", stripped)
        ):
            mkdocs_nav_warning(report, mkdocs_path, "contenu imbriqué")
            return
        entry_indexes.append(index)
        entry_indents.add(indent)

    if len(entry_indents) > 1:
        mkdocs_nav_warning(report, mkdocs_path, "indentation imbriquée")
        return
    entry_indent = (
        next(iter(entry_indents))
        if entry_indents
        else notion_indent + 4
    )

    notion_pages = notion_pages_for_update(docs_root, report)
    missing_pages = [
        page
        for page in notion_pages
        if page.relative_to(docs_root).as_posix() not in original_text
    ]
    if not missing_pages:
        return

    quote_style = "plain"
    if entry_indexes:
        first_entry = lines[entry_indexes[0]].lstrip()
        label_start = first_entry[1:].lstrip()
        if label_start.startswith('"'):
            quote_style = "double"
        elif label_start.startswith("'"):
            quote_style = "single"

    new_lines = []
    for page in missing_pages:
        relative_path = page.relative_to(docs_root).as_posix()
        label = yaml_nav_label(notion_page_title(page), quote_style)
        new_lines.append(
            f"{' ' * entry_indent}- {label}: {relative_path}{newline}"
        )

    insertion_index = block_end
    while (
        insertion_index > notion_index + 1
        and not lines[insertion_index - 1].strip()
    ):
        insertion_index -= 1

    if (
        insertion_index > 0
        and not lines[insertion_index - 1].endswith(("\n", "\r"))
    ):
        lines[insertion_index - 1] += newline

    had_final_newline = original_text.endswith(("\n", "\r"))
    if insertion_index == len(lines) and not had_final_newline:
        new_lines[-1] = new_lines[-1].removesuffix(newline)
    lines[insertion_index:insertion_index] = new_lines
    updated_bytes = "".join(lines).encode("utf-8")
    if updated_bytes == original_bytes:
        return
    if not report.dry_run:
        mkdocs_path.write_bytes(updated_bytes)
    add_modified_page(report, mkdocs_path)


def student_link_title(
    resource: Resource,
    fallback_topic: str | None = None,
) -> str:
    """Construire uniquement le texte visible du lien destiné aux élèves."""
    notion = resource.notion

    if resource.kind in {
        "MINITEST",
        "DS",
        "CORRIGE",
        "CORRIGE_TD",
    }:
        return f"{LABELS[resource.kind]} {notion}"

    topic = topic_title_for_resource(resource, fallback_topic)
    title = f"{LABELS[resource.kind]} {notion}"
    return f"{title} — {topic}" if topic else title


def relative_link(markdown_page: Path, target: Path) -> str:
    relative_path = Path(os.path.relpath(target, start=markdown_page.parent))
    return quote(relative_path.as_posix(), safe="/")


def render_document_lines(
    markdown_page: Path,
    resources: list[Resource],
    fallback_topic: str | None = None,
) -> str:
    lines = []
    for resource in sorted(
        resources,
        key=lambda item: (
            KIND_ORDER[item.kind],
            item.destination.name.casefold(),
        ),
    ):
        title = student_link_title(resource, fallback_topic)
        link = relative_link(markdown_page, resource.destination)
        lines.append(f"- [{title}]({link})")
    return "\n".join(lines)


def notion_display_topic(
    notion: str,
    resources: list[Resource],
    docs_root: Path,
) -> str | None:
    """Trouver le meilleur intitulé disponible pour le menu de sélection."""
    for resource in sorted(
        resources,
        key=lambda item: (
            KIND_ORDER[item.kind],
            item.source.name.casefold(),
        ),
    ):
        topic = topic_title_for_resource(resource)
        if topic:
            return topic

    try:
        markdown_page = find_notion_page(docs_root, notion)
    except ValueError:
        return None
    if markdown_page is None:
        return None

    ensure_inside_docs(markdown_page, docs_root)
    text = markdown_page.read_bytes().decode("utf-8")
    return notion_topic_from_heading(text, notion)


def detect_newline(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def add_auto_docs_zone(text: str, content: str, newline: str) -> str:
    """Ajouter une zone sans supprimer le contenu manuel déjà présent."""
    block = (
        f"{AUTO_DOCS_START}{newline}"
        f"{content}{newline}"
        f"{AUTO_DOCS_END}"
    )
    documents_heading = re.search(
        r"^##[ \t]+Documents[ \t]*\r?$",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    if documents_heading:
        line_end = text.find(newline, documents_heading.end())
        if line_end == -1:
            return f"{text}{newline}{newline}{block}{newline}"

        insertion_point = line_end + len(newline)
        insertion = f"{newline}{block}{newline}"
        return (
            text[:insertion_point]
            + insertion
            + text[insertion_point:]
        )

    if not text:
        prefix = ""
    elif text.endswith(("\n", "\r")):
        prefix = newline
    else:
        prefix = newline * 2

    return (
        f"{text}{prefix}"
        f"## Documents{newline}{newline}"
        f"{block}{newline}"
    )


def replace_auto_docs_zone(text: str, content: str, newline: str) -> str:
    """Remplacer strictement le contenu situé entre les deux marqueurs."""
    start_count = text.count(AUTO_DOCS_START)
    end_count = text.count(AUTO_DOCS_END)

    if start_count == 0 and end_count == 0:
        return add_auto_docs_zone(text, content, newline)
    if start_count != 1 or end_count != 1:
        raise ValueError(
            "Zone AUTO-DOCS mal formée : il faut exactement un marqueur "
            "START et un marqueur END"
        )

    content_start = text.index(AUTO_DOCS_START) + len(AUTO_DOCS_START)
    content_end = text.index(AUTO_DOCS_END)
    if content_end < content_start:
        raise ValueError("Zone AUTO-DOCS mal formée : END précède START")

    return (
        text[:content_start]
        + newline
        + content
        + newline
        + text[content_end:]
    )


def resource_in_scope(kind: str, considered_kinds: frozenset[str] | None) -> bool:
    """Un type est "considéré" si cette exécution a pu en décider le sort.

    En mode interactif, tous les types sont proposés à la sélection :
    ``considered_kinds`` vaut ``None`` et une désélection vaut suppression.
    En mode non interactif, seuls les types de ``SAFE_DEFAULT_KINDS`` sont
    proposés ; les autres n'ont pas été soumis à décision et doivent donc
    être conservés tels quels plutôt qu'effacés.
    """
    return considered_kinds is None or kind in considered_kinds


def carry_forward_resources(
    resources: list[Resource],
    selected_resources: list[Resource],
    considered_kinds: frozenset[str] | None,
) -> dict[str, list[Resource]]:
    """Grouper par notion les ressources à afficher dans une zone AUTO-DOCS.

    Pour un type considéré cette exécution, on applique la sélection telle
    quelle (cocher/décocher fait foi). Pour un type hors champ de cette
    exécution (ex. AUTOMATISMES en mode non interactif), on conserve les
    documents déjà publiés au lieu de les faire disparaître.
    """
    selected_set = set(selected_resources)
    by_notion: dict[str, list[Resource]] = defaultdict(list)
    for resource in resources:
        if resource_in_scope(resource.kind, considered_kinds):
            if resource in selected_set:
                by_notion[resource.notion].append(resource)
        elif resource.destination.is_file():
            by_notion[resource.notion].append(resource)
    return by_notion


def update_notion_pages(
    resources: list[Resource],
    selected_resources: list[Resource],
    docs_root: Path,
    report: PublicationReport,
    considered_kinds: frozenset[str] | None = None,
) -> None:
    resources_by_notion: dict[str, list[Resource]] = defaultdict(list)
    for resource in resources:
        resources_by_notion[resource.notion].append(resource)
    selected_by_notion = carry_forward_resources(
        resources, selected_resources, considered_kinds
    )

    for notion in sorted(resources_by_notion):
        try:
            markdown_page = find_notion_page(docs_root, notion)
        except ValueError as error:
            report.warnings.append(str(error))
            continue

        if markdown_page is None:
            notion_resources = resources_by_notion[notion]
            if not selected_by_notion[notion]:
                continue
            markdown_page = default_notion_page_path(
                docs_root,
                notion,
                notion_resources,
            )
            ensure_inside_docs(markdown_page, docs_root)
            topic = topic_for_new_notion_page(notion, notion_resources)
            original_text = (
                f"# {notion} — {topic}\n\n"
                "## Documents\n\n"
                f"{AUTO_DOCS_START}\n"
                f"{AUTO_DOCS_END}\n"
            )
            original_bytes = b""
        else:
            ensure_inside_docs(markdown_page, docs_root)
            original_bytes = markdown_page.read_bytes()
            original_text = original_bytes.decode("utf-8")

        newline = detect_newline(original_text)
        fallback_topic = notion_topic_from_heading(original_text, notion)
        content = render_document_lines(
            markdown_page,
            selected_by_notion[notion],
            fallback_topic,
        ).replace("\n", newline)

        try:
            updated_text = replace_auto_docs_zone(
                original_text, content, newline
            )
        except ValueError as error:
            report.warnings.append(f"{markdown_page}: {error}")
            continue

        updated_bytes = updated_text.encode("utf-8")
        if updated_bytes == original_bytes:
            report.unchanged_pages.append(markdown_page)
            continue

        if not report.dry_run:
            markdown_page.parent.mkdir(parents=True, exist_ok=True)
            markdown_page.write_bytes(updated_bytes)
        report.modified_pages.append(markdown_page)


# Pages d'index régénérées à chaque publication, sur le modèle des pages
# de notions : (sous-dossier de docs/, types de documents listés).
SECTION_INDEX_PAGES = (
    ("td", frozenset({"TD"})),
    ("automatismes", frozenset({"AUTOMATISMES", "MINITEST"})),
    ("corriges", frozenset({"CORRIGE", "CORRIGE_TD"})),
)


def update_section_index(
    directory_name: str,
    kinds: frozenset[str],
    resources: list[Resource],
    selected_resources: list[Resource],
    docs_root: Path,
    report: PublicationReport,
    considered_kinds: frozenset[str] | None = None,
) -> None:
    """Régénérer docs/<section>/index.md, comme les pages de notions."""
    all_by_notion: dict[str, list[Resource]] = defaultdict(list)
    for resource in resources:
        all_by_notion[resource.notion].append(resource)

    section_resources = [
        resource for resource in resources if resource.kind in kinds
    ]
    selected_by_notion = carry_forward_resources(
        section_resources, selected_resources, considered_kinds
    )

    notions_with_documents = {
        notion
        for notion, notion_resources in all_by_notion.items()
        if any(item.kind in kinds for item in notion_resources)
    }
    if not notions_with_documents:
        return

    markdown_page = docs_root / directory_name / "index.md"
    if not markdown_page.is_file():
        report.warnings.append(
            f"{markdown_page} : page introuvable, index non régénéré"
        )
        return
    ensure_inside_docs(markdown_page, docs_root)

    original_bytes = markdown_page.read_bytes()
    original_text = original_bytes.decode("utf-8")
    newline = detect_newline(original_text)

    sections = []
    for notion in sorted(notions_with_documents):
        try:
            notion_page = find_notion_page(docs_root, notion)
        except ValueError as error:
            report.warnings.append(str(error))
            notion_page = None
        heading_text = notion_page_title(notion_page) if notion_page else notion
        document_lines = render_document_lines(
            markdown_page, selected_by_notion[notion]
        )
        sections.append(f"## {heading_text}\n\n{document_lines}")

    content = "\n\n".join(sections).replace("\n", newline)

    try:
        updated_text = replace_auto_docs_zone(original_text, content, newline)
    except ValueError as error:
        report.warnings.append(f"{markdown_page}: {error}")
        return

    updated_bytes = updated_text.encode("utf-8")
    if updated_bytes == original_bytes:
        report.unchanged_pages.append(markdown_page)
        return

    if not report.dry_run:
        markdown_page.write_bytes(updated_bytes)
    report.modified_pages.append(markdown_page)


def update_section_indexes(
    resources: list[Resource],
    selected_resources: list[Resource],
    docs_root: Path,
    report: PublicationReport,
    considered_kinds: frozenset[str] | None = None,
) -> None:
    for directory_name, kinds in SECTION_INDEX_PAGES:
        update_section_index(
            directory_name,
            kinds,
            resources,
            selected_resources,
            docs_root,
            report,
            considered_kinds=considered_kinds,
        )


class CommitError(RuntimeError):
    """Une étape Git a échoué pendant commit_publication."""


def _run_git(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )


def git_output(completed: subprocess.CompletedProcess[str]) -> str:
    return "\n".join(
        part.strip()
        for part in (completed.stdout, completed.stderr)
        if part.strip()
    )


def commit_publication(
    report: PublicationReport,
    project_root: Path,
    extra_paths: tuple[Path, ...] = (),
) -> str | None:
    """Committer, à la fin d'une publication réelle, uniquement ce qu'elle a écrit.

    Le but est que suivre le protocole de publication (GUI ou CLI) laisse
    toujours l'arbre de travail propre, prêt pour le pré-vol de
    déploiement. On ne fait donc jamais un ``git add -A`` : seuls les
    fichiers copiés, les pages modifiées par CETTE exécution, et
    ``extra_paths`` (ex. le manifeste de publication) sont ajoutés, pour
    ne jamais embarquer une modification étrangère déjà présente dans
    l'arbre de travail. Renvoie le SHA du commit créé, ou ``None`` si
    rien n'a changé (simulation, ou publication sans écriture réelle).
    """
    if report.dry_run:
        return None

    changed_paths = [*report.copied_files, *report.modified_pages, *extra_paths]
    if not changed_paths:
        return None

    added = _run_git(project_root, "add", "--", *[str(path) for path in changed_paths])
    if added.returncode != 0:
        raise CommitError(f"git add a échoué :\n{git_output(added)}")

    staged = _run_git(project_root, "diff", "--cached", "--quiet")
    if staged.returncode == 0:
        # Les fichiers copiés étaient déjà identiques à la version suivie
        # par Git : rien à committer.
        return None

    def displayed(path: Path) -> str:
        try:
            return str(path.relative_to(project_root))
        except ValueError:
            return str(path)

    message_lines = [
        "Publication automatique : "
        f"{len(report.copied_files)} fichier(s) copié(s), "
        f"{len(report.modified_pages)} page(s) mise(s) à jour",
        "",
    ]
    if report.copied_files:
        message_lines.append("Fichiers copiés :")
        message_lines.extend(
            f"  - {displayed(path)}"
            for path in sorted(report.copied_files, key=displayed)
        )
        message_lines.append("")
    if report.modified_pages:
        message_lines.append("Pages mises à jour :")
        message_lines.extend(
            f"  - {displayed(path)}"
            for path in sorted(report.modified_pages, key=displayed)
        )
        message_lines.append("")
    if extra_paths:
        message_lines.append("Autres fichiers :")
        message_lines.extend(
            f"  - {displayed(path)}"
            for path in sorted(extra_paths, key=displayed)
        )
        message_lines.append("")
    message_lines.append(
        "Généré par le protocole de publication (publier_ressources_site.py "
        "/ publier_ressources_gui.py)."
    )

    committed = _run_git(project_root, "commit", "-m", "\n".join(message_lines))
    if committed.returncode != 0:
        raise CommitError(f"git commit a échoué :\n{git_output(committed)}")

    sha = _run_git(project_root, "rev-parse", "HEAD")
    return sha.stdout.strip() if sha.returncode == 0 else None


def display_paths(title: str, paths: list[Path], project_root: Path) -> None:
    print(f"{title} : {len(paths)}")
    for path in sorted(paths, key=lambda item: str(item).casefold()):
        try:
            displayed_path = path.relative_to(project_root)
        except ValueError:
            displayed_path = path
        print(f"  - {displayed_path}")


def display_resources(
    title: str,
    resources: list[Resource],
    source_root: Path,
) -> None:
    print(f"{title} : {len(resources)}")
    for resource in resources:
        try:
            source = resource.source.relative_to(source_root)
        except ValueError:
            source = resource.source
        print(
            f"  - {resource.notion} — {LABELS[resource.kind]} : "
            f"{source}"
        )


def display_report(report: PublicationReport, project_root: Path) -> None:
    heading = (
        "=== Bilan de la simulation ==="
        if report.dry_run
        else "=== Bilan de la publication ==="
    )
    print(f"\n{heading}")
    print(f"PDF trouvés       : {report.pdf_count}")
    print(f"PDF reconnus      : {len(report.resources)}")
    print(f"PDF non reconnus  : {report.ignored_pdf_count}")
    display_resources(
        "Fichiers sélectionnés",
        report.selected_resources,
        SOURCE_ROOT,
    )
    display_resources(
        "Fichiers ignorés (non sélectionnés)",
        report.ignored_resources,
        SOURCE_ROOT,
    )

    copied_title = (
        "Fichiers qui seraient copiés"
        if report.dry_run
        else "Fichiers copiés"
    )
    display_paths(copied_title, report.copied_files, project_root)
    print(f"Fichiers sélectionnés déjà à jour : {len(report.unchanged_files)}")

    pages_title = (
        "Pages Markdown qui seraient modifiées"
        if report.dry_run
        else "Pages Markdown modifiées"
    )
    display_paths(pages_title, report.modified_pages, project_root)
    print(f"Pages déjà à jour : {len(report.unchanged_pages)}")

    if report.missing_pages:
        notions = ", ".join(sorted(report.missing_pages))
        print(f"Pages introuvables : {notions}")

    if report.warnings:
        print(f"Avertissements : {len(report.warnings)}")
        for warning in report.warnings:
            print(f"  - {warning}")

    display_paths(
        "Fichiers déjà présents mais non sélectionnés",
        report.present_unselected_files,
        project_root,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Régénère docs/ pour qu'il corresponde exactement à l'état "
            "enregistré dans publication_manifest.json. Ne change jamais "
            "ce qui est publié : seul --gui permet de cocher/décocher des "
            "ressources."
        )
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help=(
            "conservé pour compatibilité avec lancer_publication.sh ; "
            "sans effet, le CLI ne propose plus de sélection interactive"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="simule la régénération sans écrire aucun fichier",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="lance « mkdocs serve » après la régénération",
    )
    parser.add_argument(
        "--bootstrap-manifest",
        action="store_true",
        help=(
            "reconstruire publication_manifest.json depuis les blocs "
            "AUTO-DOCS déjà publiés (n'écrit que le manifeste ; "
            "opération de migration, à ne pas relancer à chaque exécution)"
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="avec --bootstrap-manifest, écraser un manifeste déjà existant",
    )
    return parser.parse_args()


def _bootstrap_manifest_command(pm, resources: list[Resource], args) -> int:
    """Reconstruire publication_manifest.json depuis les blocs AUTO-DOCS.

    Opération de migration explicite (§5/§23) : ne modifie que le
    manifeste, jamais docs/. À ne relancer qu'en connaissance de cause
    (--force pour écraser un manifeste existant).
    """
    if MANIFEST_PATH.is_file() and not args.force:
        print(
            f"\nERREUR : {MANIFEST_PATH} existe déjà. "
            "Utilisez --force pour le reconstruire quand même."
        )
        return 1

    new_manifest = pm.bootstrap_manifest_from_auto_docs(resources, DOCS_ROOT)
    new_keys = pm.manifest_entries(new_manifest)

    existing_manifest = pm.load_publication_manifest(MANIFEST_PATH)
    state_before = pm.compute_publication_state(resources, existing_manifest, DOCS_ROOT)
    diff = pm.compute_publication_diff(state_before.items, new_keys)

    print(f"\n=== Reconstruction du manifeste depuis l'état publié ===")
    print(f"Ressources retenues comme déjà publiées : {len(new_keys)}")
    if diff.added or diff.removed:
        print(
            "\nÉcart avec le manifeste actuellement enregistré "
            f"({MANIFEST_PATH.name if MANIFEST_PATH.is_file() else 'inexistant'}) :"
        )
        for item in diff.added:
            print(f"  + {item.notion} {LABELS[item.kind]} : {item.filename}")
        for item in diff.removed:
            print(f"  - {item.notion} {LABELS[item.kind]} : {item.filename}")
    else:
        print("Aucun écart avec le manifeste actuellement enregistré.")

    if args.dry_run:
        print("\n--dry-run : manifeste non écrit.")
        return 0

    MANIFEST_PATH.write_bytes(pm.save_publication_manifest(MANIFEST_PATH, new_manifest))
    print(f"\nManifeste écrit : {MANIFEST_PATH}")
    print(
        "Ce fichier n'est pas commité automatiquement : committez-le "
        "vous-même après relecture."
    )
    return 0


def main() -> int:
    import publication_manifest as pm

    args = parse_args()
    print(f"Source     : {SOURCE_ROOT}")
    print(f"Docs       : {DOCS_ROOT}")
    print(f"Manifeste  : {MANIFEST_PATH}")

    try:
        if not SOURCE_ROOT.is_dir():
            raise FileNotFoundError(
                f"Dossier source introuvable : {SOURCE_ROOT}"
            )
        if not DOCS_ROOT.is_dir():
            raise FileNotFoundError(
                f"Dossier MkDocs introuvable : {DOCS_ROOT}"
            )

        resources, pdf_count, ignored_pdf_count = discover_resources(
            SOURCE_ROOT, DOCS_ROOT
        )

        if args.bootstrap_manifest:
            return _bootstrap_manifest_command(pm, resources, args)

        if not MANIFEST_PATH.is_file():
            print(
                f"\nERREUR : aucun manifeste à {MANIFEST_PATH}.\n"
                "Lancez d'abord : python3 scripts/publier_ressources_site.py "
                "--bootstrap-manifest"
            )
            return 1

        manifest = pm.load_publication_manifest(MANIFEST_PATH)
        state = pm.compute_publication_state(resources, manifest, DOCS_ROOT)
        desired_keys = {item.key for item in state.items if item.published}

        if state.orphans:
            print(
                f"\n{len(state.orphans)} fichier(s) orphelin(s) dans docs/ "
                "(ni publiés, ni disponibles dans la source) :"
            )
            for orphan in state.orphans:
                print(f"  - {orphan.path.relative_to(PROJECT_ROOT)}")

        result = pm.apply_publication_state(
            state.items,
            desired_keys,
            DOCS_ROOT,
            PROJECT_ROOT,
            MANIFEST_PATH,
            dry_run=args.dry_run,
            pdf_count=pdf_count,
            ignored_pdf_count=ignored_pdf_count,
        )
    except (
        FileNotFoundError,
        OSError,
        ValueError,
        pm.ManifestError,
        pm.PublicationStateError,
        pm.ConcurrencyError,
    ) as error:
        print(f"\nERREUR : {error}")
        return 1

    display_report(result.report, PROJECT_ROOT)

    if result.blocked_reason:
        print(f"\nERREUR : {result.blocked_reason}")
        return 1
    if result.commit_sha:
        print(f"\nCommit créé : {result.commit_sha[:12]}")
    elif not args.dry_run:
        print("\nAucun changement à committer (rien de nouveau à publier).")

    if args.dry_run:
        if args.serve:
            print(
                "\nmkdocs serve n’est pas lancé en mode --dry-run, "
                "afin de conserver une simulation sans écriture."
            )
        return 0

    if not args.serve:
        return 0

    print("\nLancement de mkdocs serve…")
    try:
        completed = subprocess.run(
            ["mkdocs", "serve"],
            cwd=PROJECT_ROOT,
            check=False,
        )
    except FileNotFoundError:
        print("ERREUR : la commande « mkdocs » est introuvable.")
        return 127
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
