#!/usr/bin/env python3
"""Interface Tkinter pour choisir et publier les ressources du site MkDocs."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk


# Permet aussi bien « python scripts/publier_ressources_gui.py » qu'un import
# du module depuis la racine du projet.
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import publier_ressources_site as publisher
import publication_manifest as pm


PUBLIC_SITE_URL = (
    f"https://vnicolle56610.github.io/{publisher.PROJECT_ROOT.name}/"
)

STATUS_BADGES = {
    pm.STATUS_NEW_AVAILABLE: "NOUVEAU",
    pm.STATUS_PUBLISHED_MISSING_SOURCE: "ABSENT DE LA SOURCE ⚠",
}


def find_mkdocs_executable() -> str | None:
    """Trouver MkDocs dans le projet avant de consulter le PATH."""
    candidates = (
        publisher.PROJECT_ROOT / ".venv" / "bin" / "mkdocs",
        publisher.PROJECT_ROOT / "venv" / "bin" / "mkdocs",
        publisher.PROJECT_ROOT / ".venv" / "Scripts" / "mkdocs.exe",
        publisher.PROJECT_ROOT / "venv" / "Scripts" / "mkdocs.exe",
    )
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return shutil.which("mkdocs")


def relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def path_description(path: Path) -> str:
    return relative_path(path, publisher.PROJECT_ROOT)


@dataclass(frozen=True)
class DeployPreflightResult:
    ok: bool
    user_message: str
    details: str


def run_git(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
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


def classify_git_status(porcelain: str) -> str:
    statuses = porcelain.splitlines()
    if any(line.startswith("??") for line in statuses):
        return "fichiers non suivis"
    if any("D" in line[:2] for line in statuses):
        return "fichiers supprimés localement"
    return "fichiers locaux non enregistrés dans Git"


def check_deploy_preflight(project_root: Path) -> DeployPreflightResult:
    technical_details: list[str] = []

    inside = run_git(project_root, "rev-parse", "--is-inside-work-tree")
    technical_details.append(f"$ git rev-parse --is-inside-work-tree\n{git_output(inside)}")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return DeployPreflightResult(
            False,
            "Déploiement bloqué : ce dossier n'est pas un dépôt Git.",
            "\n\n".join(technical_details),
        )

    branch = run_git(project_root, "branch", "--show-current")
    technical_details.append(f"$ git branch --show-current\n{git_output(branch)}")
    if branch.returncode != 0 or branch.stdout.strip() != "main":
        current = branch.stdout.strip() or "branche détachée ou inconnue"
        return DeployPreflightResult(
            False,
            f"Déploiement bloqué : la branche courante est « {current} », pas « main ».",
            "\n\n".join(technical_details),
        )

    status = run_git(project_root, "status", "--porcelain")
    technical_details.append(f"$ git status --porcelain\n{git_output(status)}")
    if status.returncode != 0:
        return DeployPreflightResult(
            False,
            "Déploiement bloqué : impossible de vérifier l'état Git local.",
            "\n\n".join(technical_details),
        )
    if status.stdout.strip():
        reason = classify_git_status(status.stdout)
        return DeployPreflightResult(
            False,
            (
                "Déploiement bloqué : les fichiers locaux ne correspondent pas "
                f"à la version enregistrée sur GitHub ({reason})."
            ),
            "\n\n".join(technical_details),
        )

    origin = run_git(project_root, "remote", "get-url", "origin")
    technical_details.append(f"$ git remote get-url origin\n{git_output(origin)}")
    if origin.returncode != 0:
        return DeployPreflightResult(
            False,
            "Déploiement bloqué : le remote Git « origin » est introuvable.",
            "\n\n".join(technical_details),
        )

    fetch = run_git(project_root, "fetch", "origin")
    technical_details.append(f"$ git fetch origin\n{git_output(fetch)}")
    if fetch.returncode != 0:
        return DeployPreflightResult(
            False,
            "Déploiement bloqué : impossible d'actualiser origin/main.",
            "\n\n".join(technical_details),
        )

    head = run_git(project_root, "rev-parse", "HEAD")
    technical_details.append(f"$ git rev-parse HEAD\n{git_output(head)}")
    origin_main = run_git(project_root, "rev-parse", "--verify", "origin/main")
    technical_details.append(f"$ git rev-parse --verify origin/main\n{git_output(origin_main)}")
    if head.returncode != 0 or origin_main.returncode != 0:
        return DeployPreflightResult(
            False,
            "Déploiement bloqué : origin/main est inaccessible.",
            "\n\n".join(technical_details),
        )

    if head.stdout.strip() != origin_main.stdout.strip():
        return DeployPreflightResult(
            False,
            (
                "Déploiement bloqué : le commit local main ne correspond pas "
                "exactement à origin/main."
            ),
            "\n\n".join(technical_details),
        )

    return DeployPreflightResult(
        True,
        "Pré-vol Git validé : main est propre et synchronisé avec origin/main.",
        "\n\n".join(technical_details),
    )


@dataclass(frozen=True)
class GitStateSummary:
    branch: str
    head_sha: str | None
    origin_sha: str | None
    ahead: int
    behind: int
    clean: bool
    error: str | None = None


def read_git_state(project_root: Path, fetch: bool = True) -> GitStateSummary:
    """État Git affichable dans le GUI (#17), sans jamais rien écrire."""
    branch = run_git(project_root, "branch", "--show-current").stdout.strip() or "?"
    if fetch:
        fetched = run_git(project_root, "fetch", "origin")
        if fetched.returncode != 0:
            return GitStateSummary(
                branch=branch,
                head_sha=None,
                origin_sha=None,
                ahead=0,
                behind=0,
                clean=False,
                error=f"git fetch a échoué :\n{git_output(fetched)}",
            )

    head = run_git(project_root, "rev-parse", "HEAD")
    origin = run_git(project_root, "rev-parse", "--verify", f"origin/{branch}")
    status = run_git(project_root, "status", "--porcelain")
    head_sha = head.stdout.strip() if head.returncode == 0 else None
    origin_sha = origin.stdout.strip() if origin.returncode == 0 else None
    clean = status.returncode == 0 and not status.stdout.strip()

    ahead = behind = 0
    if head_sha and origin_sha:
        counts = run_git(
            project_root, "rev-list", "--left-right", "--count", f"HEAD...origin/{branch}"
        )
        if counts.returncode == 0:
            parts = counts.stdout.split()
            if len(parts) == 2:
                ahead, behind = int(parts[0]), int(parts[1])

    return GitStateSummary(
        branch=branch,
        head_sha=head_sha,
        origin_sha=origin_sha,
        ahead=ahead,
        behind=behind,
        clean=clean,
    )


def format_git_state(state: GitStateSummary) -> str:
    if state.error:
        return f"Git : {state.error}"
    if state.head_sha is None or state.origin_sha is None:
        return f"Git : branche {state.branch}, état distant indisponible."
    local = state.head_sha[:12]
    remote = state.origin_sha[:12]
    if state.head_sha == state.origin_sha and state.clean:
        sync = "à jour avec origin"
    else:
        bits = []
        if state.ahead:
            bits.append(f"{state.ahead} commit(s) à pousser")
        if state.behind:
            bits.append(f"{state.behind} commit(s) en retard sur origin")
        if not state.clean:
            bits.append("modifications locales non commitées")
        sync = ", ".join(bits) if bits else "divergent"
    return (
        f"Git : branche {state.branch} — local {local} / origin {remote} — {sync}"
    )


def add_section(lines: list[str], title: str, items: list[str]) -> None:
    lines.append(f"{title} : {len(items)}")
    if items:
        lines.extend(f"  - {item}" for item in items)
    else:
        lines.append("  (aucun)")
    lines.append("")


def describe_item(item: pm.PublicationItem) -> str:
    label = publisher.LABELS[item.kind]
    badge = STATUS_BADGES.get(item.status)
    text = f"{item.notion} — {label} : {item.filename}"
    return f"{text}  [{badge}]" if badge else text


def format_diff_preview(
    diff: pm.PublicationDiff,
    result: "pm.ApplyResult | None",
    dry_run: bool,
    max_unchanged_shown: int = 12,
) -> str:
    """§9 : diff sémantique état actuel vs état demandé, avant toute écriture."""
    heading = (
        "PRÉVISUALISATION — état actuel vs état demandé"
        if dry_run
        else "BILAN DE L'APPLICATION"
    )
    lines = [heading, "=" * len(heading), ""]

    lines.append(f"AJOUTS ({len(diff.added)})")
    lines.append("-" * 20)
    lines.extend(f"+ {describe_item(item)}" for item in diff.added)
    if not diff.added:
        lines.append("  (aucun)")
    lines.append("")

    lines.append(f"RETRAITS ({len(diff.removed)})")
    lines.append("-" * 20)
    lines.extend(f"- {describe_item(item)}" for item in diff.removed)
    if not diff.removed:
        lines.append("  (aucun)")
    lines.append("")

    lines.append(f"INCHANGÉS ({len(diff.unchanged_published)})")
    lines.append("-" * 20)
    shown = diff.unchanged_published[:max_unchanged_shown]
    lines.extend(f"= {describe_item(item)}" for item in shown)
    remaining = len(diff.unchanged_published) - len(shown)
    if remaining > 0:
        lines.append(f"  … et {remaining} de plus")
    if not diff.unchanged_published:
        lines.append("  (aucun)")
    lines.append("")

    if result is not None:
        warnings = []
        if result.report and result.report.warnings:
            warnings.extend(result.report.warnings)
        if result.blocked_reason:
            warnings.append(result.blocked_reason)
        add_section(lines, "AVERTISSEMENTS", warnings)
        if not dry_run:
            copied = len(result.report.copied_files) if result.report else 0
            pages = len(result.report.modified_pages) if result.report else 0
            lines.append(
                f"Fichiers copiés : {copied} — Pages mises à jour : {pages} "
                f"— Manifeste modifié : {'oui' if result.manifest_changed else 'non'}"
            )
            if result.build is not None:
                lines.append(
                    f"mkdocs build --strict : {'OK' if result.build.ok else 'ÉCHEC'}"
                )
                if not result.build.ok:
                    lines.append(result.build.output)
            if result.commit_sha:
                lines.append(f"Commit créé : {result.commit_sha[:12]}")

    lines.append(
        "Les PDF déjà présents dans docs/ ne sont jamais supprimés "
        "automatiquement par un retrait."
    )
    return "\n".join(lines)


class PublicationApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.resources: list[publisher.Resource] = []
        self.pdf_count = 0
        self.ignored_pdf_count = 0
        self.state: pm.PublicationState | None = None
        self.variables: dict[pm.ResourceKey, tk.BooleanVar] = {}
        self.items_by_key: dict[pm.ResourceKey, pm.PublicationItem] = {}
        self.origin_sha_at_load: str | None = None
        self.mkdocs_process: subprocess.Popen[bytes] | None = None

        self.status = tk.StringVar(value="Analyse des ressources…")
        self.git_state_text = tk.StringVar(value="Git : …")
        self._build_interface()
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.after(0, self.scan_resources)

    def _build_interface(self) -> None:
        self.root.title(f"Publication des ressources — Maths {publisher.NIVEAU}")
        self.root.geometry("980x860")
        self.root.minsize(780, 640)

        main = ttk.Frame(self.root, padding=12)
        main.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(3, weight=3)
        main.rowconfigure(9, weight=2)

        ttk.Label(
            main,
            text="État de publication",
            font=("TkDefaultFont", 16, "bold"),
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            main,
            text=(
                f"Source : {publisher.SOURCE_ROOT}\n"
                f"Manifeste : {publisher.MANIFEST_PATH}\n"
                "Les cases cochées décrivent l'état final souhaité : ce qui "
                "sera visible sur le site après application."
            ),
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(2, 4))

        ttk.Label(main, textvariable=self.git_state_text).grid(
            row=2, column=0, sticky="w", pady=(0, 8)
        )

        documents_box = ttk.LabelFrame(main, text="Documents")
        documents_box.grid(row=3, column=0, sticky="nsew")
        documents_box.rowconfigure(0, weight=1)
        documents_box.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            documents_box,
            borderwidth=0,
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(
            documents_box,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.documents_frame = ttk.Frame(self.canvas, padding=8)
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.documents_frame,
            anchor="nw",
        )
        self.documents_frame.bind(
            "<Configure>",
            lambda _event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(
                self.canvas_window,
                width=event.width,
            ),
        )

        selection_buttons = ttk.Frame(main)
        selection_buttons.grid(row=4, column=0, sticky="ew", pady=(8, 4))
        self.safe_button = ttk.Button(
            selection_buttons,
            text="Ajouter les nouveautés Cours/TD",
            command=self.add_new_standard,
        )
        self.safe_button.pack(side="left", padx=(0, 6))
        self.clear_button = ttk.Button(
            selection_buttons,
            text="Tout décocher (retrait complet)",
            command=self.clear_all,
        )
        self.clear_button.pack(side="left", padx=6)
        self.all_button = ttk.Button(
            selection_buttons,
            text="Tout cocher",
            command=self.select_all,
        )
        self.all_button.pack(side="left", padx=6)

        action_buttons = ttk.Frame(main)
        action_buttons.grid(row=5, column=0, sticky="ew", pady=(4, 4))
        self.preview_button = ttk.Button(
            action_buttons,
            text="Prévisualiser",
            command=self.preview,
        )
        self.preview_button.pack(side="left", padx=(0, 6))
        self.publish_button = ttk.Button(
            action_buttons,
            text="Appliquer les changements",
            command=self.apply_changes,
        )
        self.publish_button.pack(side="left", padx=6)
        self.serve_button = ttk.Button(
            action_buttons,
            text="Aperçu local (mkdocs serve)",
            command=self.launch_mkdocs,
        )
        self.serve_button.pack(side="left", padx=6)
        ttk.Button(
            action_buttons,
            text="Quitter",
            command=self.quit,
        ).pack(side="right")

        deploy_buttons = ttk.Frame(main)
        deploy_buttons.grid(row=6, column=0, sticky="ew", pady=(0, 8))
        self.push_button = ttk.Button(
            deploy_buttons,
            text="Pousser vers GitHub",
            command=self.push_to_github,
            state="disabled",
        )
        self.push_button.pack(side="left", padx=(0, 6))
        self.deploy_button = ttk.Button(
            deploy_buttons,
            text="Déployer sur GitHub Pages",
            command=self.deploy_github_pages,
            state="disabled",
        )
        self.deploy_button.pack(side="left", padx=6)

        ttk.Label(
            main,
            text=(
                "Appliquer les changements met à jour les fichiers locaux "
                "et crée un commit ; pousser vers GitHub envoie ce commit "
                "sur origin/main ; déployer sur GitHub Pages met le site "
                "en ligne. Trois étapes distinctes, chacune sous contrôle."
            ),
            wraplength=920,
        ).grid(row=7, column=0, sticky="w", pady=(0, 8))

        ttk.Label(
            main,
            text="Prévisualisation et bilan",
            font=("TkDefaultFont", 11, "bold"),
        ).grid(row=8, column=0, sticky="w")

        self.output = scrolledtext.ScrolledText(
            main,
            height=14,
            wrap="word",
            font=("TkFixedFont", 10),
            state="disabled",
        )
        self.output.grid(row=9, column=0, sticky="nsew", pady=(4, 8))

        ttk.Separator(main).grid(row=10, column=0, sticky="ew")
        ttk.Label(main, textvariable=self.status).grid(
            row=11,
            column=0,
            sticky="w",
            pady=(6, 0),
        )

        self.resource_buttons = (
            self.safe_button,
            self.clear_button,
            self.all_button,
            self.preview_button,
            self.publish_button,
        )
        self._set_resource_buttons_state("disabled")

    def _set_resource_buttons_state(self, state: str) -> None:
        for button in self.resource_buttons:
            button.configure(state=state)

    def _set_output(self, text: str) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", text)
        self.output.configure(state="disabled")
        self.output.see("1.0")

    def _append_output(self, text: str) -> None:
        self.output.configure(state="normal")
        self.output.insert(tk.END, f"\n\n{text}")
        self.output.configure(state="disabled")
        self.output.see(tk.END)

    def _set_busy(self, busy: bool) -> None:
        self.root.configure(cursor="watch" if busy else "")
        self.root.update_idletasks()

    def _mkdocs_executable_or_error(self) -> str | None:
        executable = find_mkdocs_executable()
        if executable is not None:
            return executable

        messagebox.showerror(
            "MkDocs indisponible",
            "MkDocs est introuvable dans .venv, dans venv et dans le "
            "PATH.\n\nInstallez MkDocs dans l'environnement Python du "
            "projet.",
            parent=self.root,
        )
        self.status.set("MkDocs n'est pas disponible.")
        return None

    def scan_resources(self) -> None:
        self.status.set("Vérification de l'état Git (git fetch)…")
        self.root.update_idletasks()
        git_state = read_git_state(publisher.PROJECT_ROOT, fetch=True)
        self.git_state_text.set(format_git_state(git_state))
        self.origin_sha_at_load = git_state.origin_sha

        try:
            if not publisher.SOURCE_ROOT.is_dir():
                raise FileNotFoundError(
                    f"Dossier source introuvable : {publisher.SOURCE_ROOT}"
                )
            if not publisher.DOCS_ROOT.is_dir():
                raise FileNotFoundError(
                    f"Dossier MkDocs introuvable : {publisher.DOCS_ROOT}"
                )

            (
                self.resources,
                self.pdf_count,
                self.ignored_pdf_count,
            ) = publisher.discover_resources(
                publisher.SOURCE_ROOT,
                publisher.DOCS_ROOT,
            )
        except (OSError, ValueError) as error:
            self.status.set("Impossible d'analyser les ressources.")
            self._set_output(f"ERREUR\n\n{error}")
            messagebox.showerror("Erreur d'analyse", str(error), parent=self.root)
            return

        if not publisher.MANIFEST_PATH.is_file():
            if not self._offer_bootstrap_manifest():
                self.status.set("Aucun manifeste : ouverture annulée.")
                self._set_output(
                    f"Aucun {publisher.MANIFEST_PATH.name} et sa reconstruction "
                    "a été refusée. Relancez le GUI quand vous serez prêt."
                )
                return

        try:
            manifest = pm.load_publication_manifest(publisher.MANIFEST_PATH)
        except pm.ManifestError as error:
            self.status.set("Manifeste illisible.")
            self._set_output(f"ERREUR\n\n{error}")
            messagebox.showerror("Manifeste invalide", str(error), parent=self.root)
            return

        self.state = pm.compute_publication_state(
            self.resources, manifest, publisher.DOCS_ROOT
        )
        self.items_by_key = {item.key: item for item in self.state.items}

        self._display_resource_checkboxes()

        if self.pdf_count == 0:
            message = (
                "Aucun PDF trouvé dans le dossier source :\n"
                f"{publisher.SOURCE_ROOT}"
            )
            self.status.set("Aucun PDF trouvé.")
            self._set_output(message)
            messagebox.showwarning("Aucun PDF", message, parent=self.root)
            return

        self._set_resource_buttons_state("normal")
        self._update_selection_status()
        published_count = sum(1 for item in self.state.items if item.published)
        self._set_output(
            f"{len(self.state.items)} document(s) suivi(s) "
            f"({published_count} publié(s) actuellement), "
            f"{len(self.state.orphans)} orphelin(s) dans docs/.\n\n"
            "Cochez/décochez l'état final souhaité, puis « Prévisualiser » "
            "avant d'appliquer."
        )

    def _offer_bootstrap_manifest(self) -> bool:
        confirmed = messagebox.askyesno(
            "Manifeste de publication introuvable",
            f"Aucun {publisher.MANIFEST_PATH.name} n'existe encore pour ce "
            "site.\n\nLe reconstruire maintenant depuis ce qui est déjà "
            "publié (liens présents dans les blocs AUTO-DOCS) ? Cette "
            "opération n'écrit que le manifeste, jamais les pages.",
            parent=self.root,
        )
        if not confirmed:
            return False
        manifest = pm.bootstrap_manifest_from_auto_docs(
            self.resources, publisher.DOCS_ROOT
        )
        publisher.MANIFEST_PATH.write_bytes(
            pm.save_publication_manifest(publisher.MANIFEST_PATH, manifest)
        )
        return True

    def _display_resource_checkboxes(self) -> None:
        for child in self.documents_frame.winfo_children():
            child.destroy()
        self.variables.clear()

        if not self.state or not self.state.items:
            ttk.Label(
                self.documents_frame,
                text="Aucun document suivi.",
            ).grid(row=0, column=0, sticky="w")
            return

        items_by_notion: dict[str, list[pm.PublicationItem]] = defaultdict(list)
        for item in sorted(
            self.state.items,
            key=lambda i: (
                i.notion,
                publisher.KIND_ORDER[i.kind],
                i.filename.casefold(),
            ),
        ):
            items_by_notion[item.notion].append(item)

        self.documents_frame.columnconfigure(0, weight=1)
        row = 0
        for notion in sorted(items_by_notion):
            notion_items = items_by_notion[notion]
            try:
                topic = publisher.notion_display_topic(
                    notion,
                    [item.resource for item in notion_items if item.resource],
                    publisher.DOCS_ROOT,
                )
            except (OSError, ValueError):
                topic = None
            title = f"{notion} — {topic}" if topic else notion

            notion_frame = ttk.LabelFrame(
                self.documents_frame,
                text=title,
                padding=(10, 5),
            )
            notion_frame.grid(row=row, column=0, sticky="ew", pady=(0, 8))
            notion_frame.columnconfigure(0, weight=1)
            row += 1

            kind_counts = Counter(item.kind for item in notion_items)
            for item_row, item in enumerate(notion_items):
                variable = tk.BooleanVar(value=item.published)
                self.variables[item.key] = variable
                label = publisher.LABELS[item.kind]
                if kind_counts[item.kind] > 1:
                    label = f"{label} — {item.filename}"
                badge = STATUS_BADGES.get(item.status)
                if badge:
                    label = f"{label}  [{badge}]"
                ttk.Checkbutton(
                    notion_frame,
                    text=label,
                    variable=variable,
                    command=self._update_selection_status,
                ).grid(row=item_row, column=0, sticky="w", pady=2)

        if self.state.orphans:
            orphan_frame = ttk.LabelFrame(
                self.documents_frame,
                text=(
                    "Fichiers orphelins dans docs/ (ni publiés, ni dans la "
                    "source — maintenance uniquement)"
                ),
                padding=(10, 5),
            )
            orphan_frame.grid(row=row, column=0, sticky="ew", pady=(0, 8))
            orphan_frame.columnconfigure(0, weight=1)
            for orphan_row, orphan in enumerate(self.state.orphans):
                ttk.Label(
                    orphan_frame,
                    text=path_description(orphan.path),
                ).grid(row=orphan_row, column=0, sticky="w", pady=1)

    def selected_keys(self) -> set[pm.ResourceKey]:
        return {key for key, variable in self.variables.items() if variable.get()}

    def _update_selection_status(self) -> None:
        self.push_button.configure(state="disabled")
        self.deploy_button.configure(state="disabled")
        desired = self.selected_keys()
        published_count = sum(1 for item in self.state.items if item.published)
        self.status.set(
            f"{len(desired)} document(s) coché(s) sur {len(self.state.items)} "
            f"({published_count} publié(s) actuellement)."
        )

    def add_new_standard(self) -> None:
        """N'ajoute que les Cours/TD pas encore publiés ; ne décoche jamais rien."""
        added = 0
        for item in self.state.items:
            if (
                item.status == pm.STATUS_NEW_AVAILABLE
                and item.kind in publisher.SAFE_DEFAULT_KINDS
            ):
                variable = self.variables[item.key]
                if not variable.get():
                    variable.set(True)
                    added += 1
        self._update_selection_status()
        if added == 0:
            messagebox.showinfo(
                "Rien à ajouter",
                "Aucun nouveau Cours/TD non encore publié.",
                parent=self.root,
            )

    def clear_all(self) -> None:
        published_count = sum(1 for item in self.state.items if item.published)
        if not messagebox.askyesno(
            "Tout décocher : retrait complet",
            f"Cela demandera le RETRAIT des {published_count} ressource(s) "
            "actuellement publiée(s) du catalogue (les liens disparaîtront "
            "des pages ; les PDF resteront physiquement dans docs/).\n\n"
            "Continuer ?",
            parent=self.root,
        ):
            return
        for variable in self.variables.values():
            variable.set(False)
        self._update_selection_status()

    def select_all(self) -> None:
        confirmed = messagebox.askyesno(
            "Tout cocher",
            "Cette sélection inclura les mini-tests, les devoirs et tous "
            "les corrigés, y compris les ressources absentes de la source "
            "(à publier telles quelles).\n\nVoulez-vous vraiment tout "
            "cocher ?",
            parent=self.root,
        )
        if not confirmed:
            return
        for variable in self.variables.values():
            variable.set(True)
        self._update_selection_status()

    def preview(self) -> None:
        desired = self.selected_keys()
        self._set_busy(True)
        try:
            result = pm.apply_publication_state(
                self.state.items,
                desired,
                publisher.DOCS_ROOT,
                publisher.PROJECT_ROOT,
                publisher.MANIFEST_PATH,
                dry_run=True,
                skip_git_guards=True,
            )
        except (OSError, ValueError, pm.PublicationStateError) as error:
            self._set_output(f"ERREUR DE PRÉVISUALISATION\n\n{error}")
            messagebox.showerror(
                "Prévisualisation impossible",
                str(error),
                parent=self.root,
            )
            self.status.set("Échec de la prévisualisation.")
            return
        finally:
            self._set_busy(False)

        self._set_output(format_diff_preview(result.diff, result, dry_run=True))
        self.status.set(
            "Prévisualisation terminée : aucune écriture effectuée."
        )

    def apply_changes(self) -> None:
        desired = self.selected_keys()
        diff = pm.compute_publication_diff(self.state.items, desired)

        if not diff.has_changes:
            messagebox.showinfo(
                "Rien à appliquer",
                "L'état demandé est identique à l'état déjà publié.",
                parent=self.root,
            )
            return

        summary_lines = [
            f"{len(diff.added)} ajout(s), {len(diff.removed)} retrait(s).",
        ]
        if diff.added:
            summary_lines.append("")
            summary_lines.append("Ajouts :")
            summary_lines.extend(f"  + {describe_item(item)}" for item in diff.added)
        if diff.removed:
            summary_lines.append("")
            summary_lines.append("Retraits :")
            summary_lines.extend(f"  - {describe_item(item)}" for item in diff.removed)
            summary_lines.append("")
            summary_lines.append(
                "Les fichiers PDF physiques ne seront pas supprimés de docs/."
            )
        summary_lines.append("")
        summary_lines.append("Confirmer l'application de ces changements ?")
        if not messagebox.askyesno(
            "Confirmer l'application", "\n".join(summary_lines), parent=self.root
        ):
            return

        if diff.removed and not messagebox.askyesno(
            "Confirmer le retrait",
            f"Vous demandez le retrait de {len(diff.removed)} ressource(s) "
            "du catalogue. Cette confirmation est distincte de la "
            "précédente : le retrait est une action plus sensible qu'un "
            "ajout.\n\nConfirmer le retrait ?",
            parent=self.root,
        ):
            return

        self.push_button.configure(state="disabled")
        self.deploy_button.configure(state="disabled")
        self._set_busy(True)
        try:
            result = pm.apply_publication_state(
                self.state.items,
                desired,
                publisher.DOCS_ROOT,
                publisher.PROJECT_ROOT,
                publisher.MANIFEST_PATH,
                dry_run=False,
                origin_sha_at_load=self.origin_sha_at_load,
                pdf_count=self.pdf_count,
                ignored_pdf_count=self.ignored_pdf_count,
            )
        except pm.ConcurrencyError as error:
            self._set_output(f"ERREUR DE CONCURRENCE\n\n{error}")
            messagebox.showerror(
                "origin/main a changé",
                f"{error}\n\nFermez et rouvrez le GUI pour actualiser "
                "l'état avant de continuer.",
                parent=self.root,
            )
            self.status.set(
                "Application bloquée : origin/main a changé depuis l'ouverture."
            )
            return
        except (OSError, ValueError, pm.PublicationStateError) as error:
            message = (
                f"{error}\n\nL'application a été interrompue. Certains "
                "fichiers ont éventuellement été copiés avant l'erreur ; "
                "aucun PDF existant n'a été supprimé."
            )
            self._set_output(f"ERREUR\n\n{message}")
            messagebox.showerror("Application impossible", message, parent=self.root)
            self.status.set("Application interrompue.")
            return
        finally:
            self._set_busy(False)

        self._set_output(format_diff_preview(result.diff, result, dry_run=False))

        if result.blocked_reason:
            messagebox.showerror(
                "Application bloquée", result.blocked_reason, parent=self.root
            )
            self.status.set("Application bloquée : voir le détail ci-dessus.")
            return

        manifest = pm.load_publication_manifest(publisher.MANIFEST_PATH)
        self.state = pm.compute_publication_state(
            self.resources, manifest, publisher.DOCS_ROOT
        )
        self.items_by_key = {item.key: item for item in self.state.items}
        self._display_resource_checkboxes()

        git_state = read_git_state(publisher.PROJECT_ROOT, fetch=False)
        self.git_state_text.set(format_git_state(git_state))
        if git_state.ahead > 0:
            self.push_button.configure(state="normal")
        if git_state.clean and git_state.head_sha == git_state.origin_sha:
            self.deploy_button.configure(state="normal")

        if result.commit_sha:
            self.status.set(
                f"Changements appliqués et commités ({result.commit_sha[:12]}). "
                "Vous pouvez maintenant pousser vers GitHub."
            )
            messagebox.showinfo(
                "Changements appliqués",
                f"Commit créé : {result.commit_sha[:12]}\n\n"
                "Cliquez sur « Pousser vers GitHub » pour l'envoyer vers "
                "origin/main.",
                parent=self.root,
            )
        else:
            self.status.set(
                "Application terminée : rien de nouveau à committer."
            )

    def push_to_github(self) -> None:
        if not messagebox.askyesno(
            "Pousser vers GitHub",
            "Pousser la branche main locale vers origin/main ?",
            parent=self.root,
        ):
            return

        self._set_busy(True)
        try:
            pushed = run_git(publisher.PROJECT_ROOT, "push", "origin", "main")
        finally:
            self._set_busy(False)

        self._append_output(
            "PUSH VERS GITHUB\n=================\n\n" + git_output(pushed)
        )
        if pushed.returncode != 0:
            messagebox.showerror(
                "Échec du push",
                git_output(pushed) or "Le push a échoué.",
                parent=self.root,
            )
            self.status.set("Le push a échoué.")
            return

        git_state = read_git_state(publisher.PROJECT_ROOT, fetch=False)
        self.git_state_text.set(format_git_state(git_state))
        self.push_button.configure(state="disabled")
        if git_state.clean and git_state.head_sha == git_state.origin_sha:
            self.deploy_button.configure(state="normal")
            self.status.set("Poussé vers GitHub. Vous pouvez maintenant déployer.")
        else:
            self.status.set("Poussé vers GitHub.")
        messagebox.showinfo(
            "Push terminé",
            "main est maintenant aligné avec origin/main.",
            parent=self.root,
        )

    def deploy_github_pages(self) -> None:
        executable = self._mkdocs_executable_or_error()
        if executable is None:
            return

        preflight = check_deploy_preflight(publisher.PROJECT_ROOT)
        self._append_output(
            "PRÉ-VOL GIT AVANT DÉPLOIEMENT\n"
            "==============================\n\n"
            f"{preflight.user_message}\n\n"
            f"{preflight.details}"
        )
        if not preflight.ok:
            messagebox.showerror(
                "Déploiement bloqué",
                preflight.user_message,
                parent=self.root,
            )
            self.status.set("Déploiement bloqué par le pré-vol Git.")
            return

        confirmed = messagebox.askyesno(
            "Déployer le site public",
            "Cette opération va reconstruire le site avec le contenu actuel "
            "de docs/ puis le publier sur GitHub Pages.\n\n"
            f"Adresse publique :\n{PUBLIC_SITE_URL}\n\n"
            "Continuer ?",
            parent=self.root,
        )
        if not confirmed:
            return

        self._set_busy(True)
        try:
            with tempfile.TemporaryDirectory(
                prefix=f"{publisher.PROJECT_ROOT.name}-gh-pages-"
            ) as site_directory:
                completed = subprocess.run(
                    [
                        executable,
                        "gh-deploy",
                        "--strict",
                        "--force",
                        "--site-dir",
                        site_directory,
                    ],
                    cwd=publisher.PROJECT_ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
        except OSError as error:
            messagebox.showerror(
                "Déploiement impossible",
                str(error),
                parent=self.root,
            )
            self.status.set("Échec du déploiement GitHub Pages.")
            return
        finally:
            self._set_busy(False)

        command_output = "\n".join(
            part.strip()
            for part in (completed.stdout, completed.stderr)
            if part.strip()
        )
        if completed.returncode != 0:
            details = command_output or (
                f"mkdocs gh-deploy a renvoyé le code "
                f"{completed.returncode}."
            )
            self._append_output(
                "ERREUR DE DÉPLOIEMENT GITHUB PAGES\n"
                "===================================\n\n"
                + details
            )
            messagebox.showerror(
                "Déploiement GitHub Pages impossible",
                "Le site public n'a pas été actualisé.\n\n"
                "Consultez le bilan pour connaître l'erreur Git ou MkDocs.",
                parent=self.root,
            )
            self.status.set("Le déploiement GitHub Pages a échoué.")
            return

        self._append_output(
            "DÉPLOIEMENT GITHUB PAGES\n"
            "========================\n\n"
            f"Site public actualisé : {PUBLIC_SITE_URL}\n\n"
            "Le dossier site/ du projet n'a pas été modifié."
        )
        self.status.set(
            "Déploiement terminé. GitHub Pages peut demander quelques "
            "secondes pour actualiser le site public."
        )
        messagebox.showinfo(
            "Site public déployé",
            "Le déploiement GitHub Pages est terminé.\n\n"
            f"{PUBLIC_SITE_URL}\n\n"
            "L'actualisation publique peut prendre quelques secondes.",
            parent=self.root,
        )

    def launch_mkdocs(self) -> None:
        if (
            self.mkdocs_process is not None
            and self.mkdocs_process.poll() is None
        ):
            messagebox.showinfo(
                "Serveur déjà lancé",
                "mkdocs serve est déjà en cours d'exécution.",
                parent=self.root,
            )
            return

        executable = self._mkdocs_executable_or_error()
        if executable is None:
            return

        try:
            self.mkdocs_process = subprocess.Popen(
                [executable, "serve"],
                cwd=publisher.PROJECT_ROOT,
            )
        except OSError as error:
            messagebox.showerror(
                "Impossible de lancer MkDocs",
                str(error),
                parent=self.root,
            )
            self.status.set("Échec du lancement de MkDocs.")
            return

        self.status.set(
            "Aperçu local disponible sur http://127.0.0.1:8000/ — "
            "il ne modifie pas le site public."
        )
        self.root.after(750, self._poll_mkdocs)

    def _poll_mkdocs(self) -> None:
        if self.mkdocs_process is None:
            return
        return_code = self.mkdocs_process.poll()
        if return_code is None:
            self.root.after(750, self._poll_mkdocs)
            return

        self.status.set(
            f"mkdocs serve s'est arrêté avec le code {return_code}."
        )
        self.mkdocs_process = None

    def quit(self) -> None:
        if (
            self.mkdocs_process is not None
            and self.mkdocs_process.poll() is None
        ):
            self.mkdocs_process.terminate()
            try:
                self.mkdocs_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.mkdocs_process.kill()
        self.root.destroy()


def main() -> int:
    try:
        root = tk.Tk()
    except tk.TclError as error:
        print(
            "Impossible d'ouvrir l'interface Tkinter "
            f"(affichage graphique indisponible) : {error}",
            file=sys.stderr,
        )
        return 1

    PublicationApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
