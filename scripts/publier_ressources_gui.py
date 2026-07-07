#!/usr/bin/env python3
"""Interface Tkinter pour choisir et publier les ressources du site MkDocs."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from collections import Counter, defaultdict
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk


# Permet aussi bien « python scripts/publier_ressources_gui.py » qu'un import
# du module depuis la racine du projet.
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import publier_ressources_site as publisher


PUBLIC_SITE_URL = (
    f"https://vnicolle56610.github.io/{publisher.PROJECT_ROOT.name}/"
)


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


def resource_description(resource: publisher.Resource) -> str:
    source = relative_path(resource.source, publisher.SOURCE_ROOT)
    label = publisher.LABELS[resource.kind]
    return f"{resource.notion} — {label} : {source}"


def path_description(path: Path) -> str:
    return relative_path(path, publisher.PROJECT_ROOT)


def add_section(lines: list[str], title: str, items: list[str]) -> None:
    lines.append(f"{title} : {len(items)}")
    if items:
        lines.extend(f"  - {item}" for item in items)
    else:
        lines.append("  (aucun)")
    lines.append("")


def format_report(report: publisher.PublicationReport) -> str:
    """Produire un bilan adapté à la zone de texte de l'interface."""
    if report.dry_run:
        heading = "PRÉVISUALISATION — aucune écriture effectuée"
        copied_title = "Fichiers qui seraient copiés"
        pages_title = "Pages Markdown qui seraient modifiées"
    else:
        heading = "BILAN DE LA PUBLICATION"
        copied_title = "Fichiers copiés"
        pages_title = "Pages Markdown modifiées"

    lines = [
        heading,
        "=" * len(heading),
        "",
        f"PDF trouvés : {report.pdf_count}",
        f"PDF reconnus : {len(report.resources)}",
        f"PDF non reconnus : {report.ignored_pdf_count}",
        "",
    ]

    add_section(
        lines,
        "Fichiers sélectionnés",
        [
            resource_description(resource)
            for resource in report.selected_resources
        ],
    )
    add_section(
        lines,
        copied_title,
        [path_description(path) for path in report.copied_files],
    )
    add_section(
        lines,
        "Fichiers sélectionnés déjà à jour",
        [path_description(path) for path in report.unchanged_files],
    )
    add_section(
        lines,
        pages_title,
        [path_description(path) for path in report.modified_pages],
    )
    add_section(
        lines,
        "Pages Markdown déjà à jour",
        [path_description(path) for path in report.unchanged_pages],
    )
    add_section(
        lines,
        "Fichiers ignorés car non sélectionnés",
        [
            resource_description(resource)
            for resource in report.ignored_resources
        ],
    )
    add_section(
        lines,
        "Fichiers déjà présents dans docs/ mais non sélectionnés",
        [
            path_description(path)
            for path in report.present_unselected_files
        ],
    )
    add_section(
        lines,
        "Pages Markdown introuvables",
        list(report.missing_pages),
    )
    add_section(lines, "Avertissements", list(report.warnings))

    lines.append(
        "Aucun fichier PDF déjà présent dans docs/ n'est supprimé "
        "automatiquement."
    )
    return "\n".join(lines)


class PublicationApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.resources: list[publisher.Resource] = []
        self.pdf_count = 0
        self.ignored_pdf_count = 0
        self.variables: dict[publisher.Resource, tk.BooleanVar] = {}
        self.mkdocs_process: subprocess.Popen[bytes] | None = None

        self.status = tk.StringVar(value="Analyse des ressources…")
        self._build_interface()
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.after(0, self.scan_resources)

    def _build_interface(self) -> None:
        self.root.title(f"Publication des ressources — Maths {publisher.NIVEAU}")
        self.root.geometry("980x820")
        self.root.minsize(780, 620)

        main = ttk.Frame(self.root, padding=12)
        main.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=3)
        main.rowconfigure(7, weight=2)

        ttk.Label(
            main,
            text="Choisir les documents à publier",
            font=("TkDefaultFont", 16, "bold"),
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            main,
            text=f"Source : {publisher.SOURCE_ROOT}",
        ).grid(row=1, column=0, sticky="w", pady=(2, 8))

        documents_box = ttk.LabelFrame(main, text="Documents disponibles")
        documents_box.grid(row=2, column=0, sticky="nsew")
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
        selection_buttons.grid(row=3, column=0, sticky="ew", pady=(8, 4))
        self.safe_button = ttk.Button(
            selection_buttons,
            text="Sélection sûre",
            command=self.select_safe,
        )
        self.safe_button.pack(side="left", padx=(0, 6))
        self.clear_button = ttk.Button(
            selection_buttons,
            text="Tout décocher",
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
        action_buttons.grid(row=4, column=0, sticky="ew", pady=(4, 8))
        self.preview_button = ttk.Button(
            action_buttons,
            text="Prévisualiser",
            command=self.preview,
        )
        self.preview_button.pack(side="left", padx=(0, 6))
        self.publish_button = ttk.Button(
            action_buttons,
            text="Publier la sélection",
            command=self.publish,
        )
        self.publish_button.pack(side="left", padx=6)
        self.deploy_button = ttk.Button(
            action_buttons,
            text="Déployer sur GitHub Pages",
            command=self.deploy_github_pages,
            state="disabled",
        )
        self.deploy_button.pack(side="left", padx=6)
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

        ttk.Label(
            main,
            text=(
                "Publier la sélection met à jour les fichiers locaux ; "
                "l’aperçu local reste sur cet ordinateur ; déployer sur "
                "GitHub Pages met le site en ligne."
            ),
            wraplength=920,
        ).grid(row=5, column=0, sticky="w", pady=(0, 8))

        ttk.Label(
            main,
            text="Prévisualisation et bilan",
            font=("TkDefaultFont", 11, "bold"),
        ).grid(row=6, column=0, sticky="w")

        self.output = scrolledtext.ScrolledText(
            main,
            height=14,
            wrap="word",
            font=("TkFixedFont", 10),
            state="disabled",
        )
        self.output.grid(row=7, column=0, sticky="nsew", pady=(4, 8))

        ttk.Separator(main).grid(row=8, column=0, sticky="ew")
        ttk.Label(main, textvariable=self.status).grid(
            row=9,
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

        if not self.resources:
            message = (
                f"{self.pdf_count} PDF trouvé(s), mais aucun nom de fichier "
                "n'est reconnu."
            )
            self.status.set("Aucun PDF reconnu.")
            self._set_output(message)
            messagebox.showwarning(
                "Aucun PDF reconnu",
                message,
                parent=self.root,
            )
            return

        self._set_resource_buttons_state("normal")
        self._update_selection_status()
        self._set_output(
            f"{len(self.resources)} document(s) reconnu(s) parmi "
            f"{self.pdf_count} PDF.\n\n"
            "Choisissez les documents puis utilisez « Prévisualiser » "
            "avant de publier."
        )

    def _display_resource_checkboxes(self) -> None:
        for child in self.documents_frame.winfo_children():
            child.destroy()
        self.variables.clear()

        if not self.resources:
            ttk.Label(
                self.documents_frame,
                text="Aucun document reconnu.",
            ).grid(row=0, column=0, sticky="w")
            return

        resources_by_notion: dict[
            str, list[publisher.Resource]
        ] = defaultdict(list)
        for resource in sorted(
            self.resources,
            key=lambda item: (
                item.notion,
                publisher.KIND_ORDER[item.kind],
                item.source.name.casefold(),
            ),
        ):
            resources_by_notion[resource.notion].append(resource)

        self.documents_frame.columnconfigure(0, weight=1)
        for row, notion in enumerate(sorted(resources_by_notion)):
            notion_resources = resources_by_notion[notion]
            try:
                topic = publisher.notion_display_topic(
                    notion,
                    notion_resources,
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
            notion_frame.grid(
                row=row,
                column=0,
                sticky="ew",
                pady=(0, 8),
            )
            notion_frame.columnconfigure(0, weight=1)

            kind_counts = Counter(
                resource.kind for resource in notion_resources
            )
            for resource_row, resource in enumerate(notion_resources):
                variable = tk.BooleanVar(
                    value=resource.kind in publisher.SAFE_DEFAULT_KINDS
                )
                self.variables[resource] = variable
                label = publisher.selection_label(
                    resource,
                    duplicate_kind=kind_counts[resource.kind] > 1,
                )
                ttk.Checkbutton(
                    notion_frame,
                    text=label,
                    variable=variable,
                    command=self._update_selection_status,
                ).grid(
                    row=resource_row,
                    column=0,
                    sticky="w",
                    pady=2,
                )

    def selected_resources(self) -> list[publisher.Resource]:
        return [
            resource
            for resource in self.resources
            if self.variables[resource].get()
        ]

    def _update_selection_status(self) -> None:
        self.deploy_button.configure(state="disabled")
        selected_count = len(self.selected_resources())
        self.status.set(
            f"{selected_count} document(s) sélectionné(s) sur "
            f"{len(self.resources)}."
        )

    def select_safe(self) -> None:
        for resource, variable in self.variables.items():
            variable.set(resource.kind in publisher.SAFE_DEFAULT_KINDS)
        self._update_selection_status()

    def clear_all(self) -> None:
        for variable in self.variables.values():
            variable.set(False)
        self._update_selection_status()

    def select_all(self) -> None:
        confirmed = messagebox.askyesno(
            "Tout sélectionner",
            "Cette sélection inclura les mini-tests, les devoirs et tous "
            "les corrigés.\n\nVoulez-vous vraiment tout cocher ?",
            parent=self.root,
        )
        if not confirmed:
            return
        for variable in self.variables.values():
            variable.set(True)
        self._update_selection_status()

    def _run_publication(
        self,
        selected: list[publisher.Resource],
        dry_run: bool,
    ) -> publisher.PublicationReport:
        if not publisher.SOURCE_ROOT.is_dir():
            raise FileNotFoundError(
                f"Dossier source introuvable : {publisher.SOURCE_ROOT}"
            )
        if not publisher.DOCS_ROOT.is_dir():
            raise FileNotFoundError(
                f"Dossier MkDocs introuvable : {publisher.DOCS_ROOT}"
            )
        for resource in selected:
            if not resource.source.is_file():
                raise FileNotFoundError(
                    f"PDF source introuvable : {resource.source}"
                )

        return publisher.publish_selected_resources(
            self.resources,
            selected,
            publisher.DOCS_ROOT,
            self.pdf_count,
            self.ignored_pdf_count,
            dry_run=dry_run,
        )

    def preview(self) -> None:
        selected = self.selected_resources()
        self._set_busy(True)
        try:
            report = self._run_publication(selected, dry_run=True)
        except (OSError, ValueError) as error:
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

        self._set_output(format_report(report))
        self.status.set(
            "Prévisualisation terminée : aucune écriture effectuée."
        )

    def publish(self) -> None:
        selected = self.selected_resources()
        confirmation = (
            f"Publier {len(selected)} document(s) sélectionné(s) ?\n\n"
            "Les liens des documents non sélectionnés seront retirés des "
            "zones AUTO-DOCS. Les PDF déjà présents dans docs/ ne seront "
            "pas supprimés."
        )
        if not messagebox.askyesno(
            "Confirmer la publication",
            confirmation,
            parent=self.root,
        ):
            return

        self.deploy_button.configure(state="disabled")
        self._set_busy(True)
        try:
            report = self._run_publication(selected, dry_run=False)
        except (OSError, ValueError) as error:
            message = (
                f"{error}\n\nLa publication a été interrompue. Certains "
                "fichiers ont éventuellement été copiés avant l'erreur ; "
                "aucun PDF existant n'a été supprimé."
            )
            self._set_output(f"ERREUR DE PUBLICATION\n\n{message}")
            messagebox.showerror(
                "Erreur de publication",
                message,
                parent=self.root,
            )
            self.status.set("Publication interrompue.")
            return
        finally:
            self._set_busy(False)

        self._set_output(format_report(report))
        self.deploy_button.configure(state="normal")
        self.status.set(
            f"Publication terminée : {len(report.copied_files)} fichier(s) "
            f"copié(s), {len(report.modified_pages)} page(s) modifiée(s). "
            "Le déploiement GitHub Pages est maintenant disponible."
        )

        if report.missing_pages or report.warnings:
            details = []
            if report.missing_pages:
                details.append(
                    "Pages introuvables : "
                    + ", ".join(report.missing_pages)
                )
            if report.warnings:
                details.append(
                    f"{len(report.warnings)} autre(s) avertissement(s)."
                )
            messagebox.showwarning(
                "Publication terminée avec avertissements",
                "\n".join(details)
                + "\n\nConsultez le bilan pour plus de détails. Vous "
                "pouvez ensuite déployer les pages disponibles.",
                parent=self.root,
            )
        else:
            messagebox.showinfo(
                "Publication terminée",
                "Les fichiers locaux ont été mis à jour.\n\n"
                "Cliquez maintenant sur « Déployer sur GitHub Pages » "
                "pour actualiser le site public.",
                parent=self.root,
            )

    def deploy_github_pages(self) -> None:
        executable = self._mkdocs_executable_or_error()
        if executable is None:
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
