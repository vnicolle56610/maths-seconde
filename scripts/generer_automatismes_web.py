#!/usr/bin/env python3
"""PROTOTYPE — Génère, depuis la source Beamer d'automatismes, deux pages MkDocs :

1. une page « lecture » : énoncés en texte (maths MathJax), coups de pouce et
   corrigés repliables ;
2. une page « QCM interactif » : banque de questions embarquée en JSON dans la
   page, moteur en JavaScript pur (docs/javascripts/automatismes-qcm.js).

La source LaTeX n'est jamais modifiée : elle est seulement lue.

Usage :
    python3 generer_automatismes_web.py SOURCE.tex DOCS_DIR \
        --code N04 --slug calcul-litteral --titre "Calcul littéral" \
        --niveau Seconde --pdf AUTOMATISMES_N04_CALCUL_LITTERAL.pdf \
        --notion ../notions/N04-calcul-litteral.md
"""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass, field
from pathlib import Path


# --------------------------------------------------------------------------
# Lecture LaTeX : outils de base
# --------------------------------------------------------------------------

def lire_argument(texte: str, i: int) -> tuple[str, int]:
    """Lit un argument {…} à partir de l'indice i (qui pointe sur « { »)."""
    while texte[i].isspace():
        i += 1
    if texte[i] != "{":
        raise ValueError(f"accolade attendue à l'indice {i} : {texte[i:i+30]!r}")
    profondeur, debut = 0, i
    while True:
        c = texte[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            profondeur += 1
        elif c == "}":
            profondeur -= 1
            if profondeur == 0:
                return texte[debut + 1:i], i + 1
        i += 1


def remplacer_commande(texte: str, nom: str, fonction) -> str:
    """Remplace chaque \\nom{arg} par fonction(arg) (accolades imbriquées gérées)."""
    motif = re.compile(r"\\" + nom + r"(?![A-Za-z])")
    sortie, pos = [], 0
    while (m := motif.search(texte, pos)):
        arg, fin = lire_argument(texte, m.end())
        sortie.append(texte[pos:m.start()])
        sortie.append(fonction(arg))
        pos = fin
    sortie.append(texte[pos:])
    return "".join(sortie)


def segments_math(texte: str) -> list[tuple[bool, str]]:
    """Découpe en segments (est_math, contenu) selon les $…$."""
    morceaux, dans_math, courant, i = [], False, [], 0
    while i < len(texte):
        c = texte[i]
        if c == "\\" and i + 1 < len(texte):
            courant.append(texte[i:i + 2])
            i += 2
            continue
        if c == "$":
            morceaux.append((dans_math, "".join(courant)))
            courant, dans_math = [], not dans_math
        else:
            courant.append(c)
        i += 1
    morceaux.append((dans_math, "".join(courant)))
    return [(m, s) for m, s in morceaux if s]


# --------------------------------------------------------------------------
# Conversion LaTeX → HTML (MathJax via la classe « arithmatex »)
# --------------------------------------------------------------------------

def math_html(tex: str) -> str:
    tex = remplacer_commande(tex, "resultat", lambda a: r"\boxed{" + a + "}")
    return f'<span class="arithmatex">\\({html.escape(tex, quote=False)}\\)</span>'


def texte_html(tex: str) -> str:
    """Convertit un fragment de texte LaTeX courant en HTML."""
    # Commandes « résultat » hors mode maths
    tex = remplacer_commande(tex, "resultattexte",
                             lambda a: "\x00RT" + a + "\x00")
    tex = remplacer_commande(tex, "textbf", lambda a: "\x00B" + a + "\x00")
    morceaux, formules = [], []

    def resultat_hors_maths(arg: str) -> str:
        formules.append(math_html(r"\boxed{" + arg + "}"))
        return f"\x00M{len(formules) - 1}\x00"

    for est_math, s in segments_math(tex):
        if est_math:
            morceaux.append(math_html(s))
        else:
            s = remplacer_commande(s, "resultat", resultat_hors_maths)
            s = s.replace("~", "\u00a0").replace("\\,", "\u202f").replace("\\ ", " ")
            s = re.sub(r"\\quad|\\qquad", " ", s)
            s = html.escape(s, quote=False)
            s = re.sub(r"\x00RT(.*?)\x00", r'<strong class="auto-resultat">\1</strong>', s)
            s = re.sub(r"\x00B(.*?)\x00", r"<strong>\1</strong>", s)
            s = re.sub(r"\x00M(\d+)\x00", lambda m: formules[int(m.group(1))], s)
            morceaux.append(s)
    return re.sub(r"\s+", " ", "".join(morceaux)).strip()


def items(bloc: str) -> list[str]:
    """Liste des \\item d'un itemize, ou le texte brut s'il n'y en a pas."""
    bloc = re.sub(r"\\(begin|end)\{itemize\}|\\tiny", "", bloc)
    if "\\item" in bloc:
        return [texte_html(x) for x in bloc.split("\\item") if x.strip()]
    return [texte_html(bloc)] if bloc.strip() else []


# --------------------------------------------------------------------------
# Lecture des frames Beamer
# --------------------------------------------------------------------------

@dataclass
class Question:
    numero: int
    enonce: str                    # HTML
    choix: list[str] = field(default_factory=list)   # HTML, ordre A-D
    corrige: str = ""              # HTML
    bonne: int | None = None       # indice 0-3 pour un QCM


@dataclass
class Serie:
    lettre: str
    duree: str
    theme: str
    consigne: str = ""
    conseils: list[str] = field(default_factory=list)
    vigilance: list[str] = field(default_factory=list)
    methode: list[str] = field(default_factory=list)
    vigilance_corrige: list[str] = field(default_factory=list)
    questions: list[Question] = field(default_factory=list)

    @property
    def est_qcm(self) -> bool:
        return all(q.choix for q in self.questions)


def bloc_env(frame: str, env: str) -> str:
    m = re.search(r"\\begin\{" + env + r"\}(.*?)\\end\{" + env + r"\}", frame, re.S)
    return m.group(1).strip() if m else ""


def lignes_tableau(frame: str) -> list[tuple[int, str]]:
    debut = frame.index("\\begin{tabular}") + len("\\begin{tabular}")
    _, debut = lire_argument(frame, debut)          # spécification des colonnes
    corps = frame[debut:frame.index("\\end{tabular}", debut)]
    lignes = re.split(r"\\\\\[[^\]]*\]|\\\\\s*$", corps)
    sortie = []
    for ligne in lignes:
        m = re.match(r"\s*\\numq\{(\d+)\}\s*&\s*(.*)", ligne, re.S)
        if m:
            sortie.append((int(m.group(1)), m.group(2).strip()))
    return sortie


def decouper_choix(contenu: str) -> tuple[str, list[str]]:
    m = re.search(r"\\begin\{minipage\}(?:\[[^\]]*\])?\{[^}]*\}(.*?)\\end\{minipage\}", contenu, re.S)
    if not m:
        return contenu, []
    enonce = contenu[:m.start()].strip()
    bloc = m.group(1).replace("\\tiny", "")
    parties = re.split(r"\\choix[ABCD]\\?\s*", bloc)[1:]
    choix = [texte_html(re.sub(r"\\quad\s*$", "", p.strip()).strip()) for p in parties]
    return enonce, choix


def lire_series(source: str) -> list[Serie]:
    corps = source.split("\\begin{document}", 1)[1]
    if "\\(" in corps:
        raise ValueError("formules en \\(…\\) non gérées par le prototype (format N07-N15)")
    frames = re.findall(r"\\begin\{frame\}(.*?)\\end\{frame\}", corps, re.S)
    series: dict[str, Serie] = {}
    for frame in frames:
        i = frame.index("\\bandeau")
        a1, i = lire_argument(frame, i + len("\\bandeau"))
        a2, i = lire_argument(frame, i)
        a3, i = lire_argument(frame, i)
        lettre = re.search(r"Série\s+([A-Z])", a2).group(1)
        if a1.startswith("AUTOMATISMES"):
            duree = re.search(r"—\s*(.*)$", a2)
            serie = series.setdefault(lettre, Serie(lettre, "", a3))
            serie.duree = duree.group(1).strip() if duree else ""
            serie.theme = a3
            serie.consigne = texte_html(bloc_env(frame, "blocconsigne"))
            serie.conseils = items(bloc_env(frame, "blocconseils"))
            serie.vigilance = items(bloc_env(frame, "blocvigilance"))
            for num, contenu in lignes_tableau(frame):
                enonce, choix = decouper_choix(contenu)
                serie.questions.append(Question(num, texte_html(enonce), choix))
        elif a1.startswith("CORRECTION"):
            serie = series[lettre]
            serie.methode = items(bloc_env(frame, "blocmethode"))
            serie.vigilance_corrige = items(bloc_env(frame, "blocvigilance"))
            for num, contenu in lignes_tableau(frame):
                q = next(x for x in serie.questions if x.numero == num)
                m = re.match(r"\\resultattexte\{réponse\s+([ABCD])\}\s*:?\s*(.*)", contenu, re.S)
                if m and q.choix:
                    q.bonne = "ABCD".index(m.group(1))
                    q.corrige = texte_html(m.group(2))
                else:
                    q.corrige = texte_html(contenu)
    if not series:
        raise ValueError("aucune série lue : format de source non reconnu "
                         "(frames appelées par macro \\questionsframe ?)")
    for s in series.values():
        for q in s.questions:
            if q.choix and q.bonne is None:
                raise ValueError(f"Série {s.lettre} Q{q.numero} : bonne réponse introuvable")
            if not q.corrige:
                raise ValueError(f"Série {s.lettre} Q{q.numero} : corrigé manquant")
    return [series[k] for k in sorted(series)]


# --------------------------------------------------------------------------
# Écriture de la page « lecture »
# --------------------------------------------------------------------------

def yaml_str(s: str) -> str:
    """Chaîne YAML sûre (JSON est un sous-ensemble de YAML)."""
    return json.dumps(s, ensure_ascii=False)


def indenter(lignes: list[str], n: int = 4) -> list[str]:
    return [(" " * n + l) if l else "" for l in lignes]


def liste_html(elements: list[str]) -> str:
    if len(elements) == 1:
        return f"<p>{elements[0]}</p>"
    return "<ul>" + "".join(f"<li>{e}</li>" for e in elements) + "</ul>"


def page_lecture(series: list[Serie], a: argparse.Namespace) -> str:
    nb_q = sum(len(s.questions) for s in series)
    L = [
        "---",
        "title: " + yaml_str(f"Automatismes {a.niveau} – {a.titre} : exercices et QCM corrigés"),
        "description: " + yaml_str(f"{nb_q} questions d'automatismes de {a.niveau} en {a.titre.lower()}, "
        f"sans calculatrice, en {len(series)} séries chronométrées, avec corrigés détaillés et QCM interactif."),
        "---",
        "",
        f"# Automatismes {a.code} — {a.titre}",
        "",
        f"{nb_q} questions **sans calculatrice**, réparties en {len(series)} séries courtes "
        "à faire en quelques minutes. Chercher d'abord seul, puis ouvrir le corrigé.",
        "",
        '<div class="auto-actions" markdown>',
        f"[⚡ Faire le QCM interactif](qcm-{a.code}-{a.slug}.md){{ .md-button .md-button--primary }}",
        f"[📄 Diaporama PDF à projeter]({a.pdf}){{ .md-button }}",
        f"[📖 Revoir la notion]({a.notion}){{ .md-button }}",
        "</div>",
        "",
    ]
    for s in series:
        titre = s.theme.replace(" — ", " : ", 1)
        L += [f"## Série {s.lettre} — {titre}", ""]
        if s.duree:
            L += [f'<p class="auto-meta">⏱ {s.duree} · Calculatrice interdite</p>', ""]
        L += ['<div class="auto-consigne" markdown>',
              f"**Consigne.** {s.consigne}", "</div>", ""]
        L.append('<ol class="auto-questions">')
        for q in s.questions:
            bloc = f"<li>{q.enonce}"
            if q.choix:
                bloc += '<ol class="auto-choix" type="A">' + "".join(
                    f"<li>{c}</li>" for c in q.choix) + "</ol>"
            L.append(bloc + "</li>")
        L += ["</ol>", ""]
        if s.conseils or s.vigilance:
            L += ['??? tip "Coup de pouce"', ""]
            interne = []
            if s.conseils:
                interne += [f"<p><strong>Conseils</strong></p>{liste_html(s.conseils)}"]
            if s.vigilance:
                interne += [f"<p><strong>Vigilance</strong></p>{liste_html(s.vigilance)}"]
            L += indenter(interne) + [""]
        L += [f'??? success "Corrigé de la série {s.lettre}"', ""]
        interne = ['<ol class="auto-corrige">']
        for q in s.questions:
            if q.choix:
                interne.append(f'<li><strong class="auto-resultat">Réponse {"ABCD"[q.bonne]}</strong> : {q.corrige}</li>')
            else:
                interne.append(f"<li>{q.corrige}</li>")
        interne.append("</ol>")
        if s.methode:
            interne.append(f'<div class="auto-methode"><strong>Méthode.</strong> {" ".join(s.methode)}</div>')
        if s.vigilance_corrige:
            interne.append(f'<div class="auto-vigilance"><strong>Vigilance.</strong> {" ".join(s.vigilance_corrige)}</div>')
        L += indenter(interne) + [""]
    L += [
        "---",
        "",
        f"*Ces questions reprennent le diaporama d'automatismes {a.code} utilisé en classe. "
        "Licence CC BY-NC-SA 4.0 : réutilisation libre en classe, en citant la source.*",
        "",
    ]
    return "\n".join(L)


# --------------------------------------------------------------------------
# Écriture de la page « QCM interactif »
# --------------------------------------------------------------------------

def banque(series: list[Serie], a: argparse.Namespace) -> dict:
    questions = []
    for s in series:
        for q in s.questions:
            questions.append({
                "id": f"{a.code}-{s.lettre}{q.numero}",
                "serie": s.lettre,
                "theme": s.theme,
                "type": "qcm" if q.choix else "flash",
                "enonce": q.enonce,
                "choix": q.choix,
                "bonne": q.bonne,
                "corrige": q.corrige,
                "methode": " ".join(s.methode),
            })
    return {
        "notion": a.code,
        "titre": a.titre,
        "niveau": a.niveau,
        "series": [{"lettre": s.lettre, "theme": s.theme, "duree": s.duree,
                    "consigne": s.consigne, "qcm": s.est_qcm} for s in series],
        "questions": questions,
    }


def page_qcm(series: list[Serie], a: argparse.Namespace) -> str:
    donnees = json.dumps(banque(series, a), ensure_ascii=False, indent=1)
    donnees = donnees.replace("</", "<\\/")  # sûreté dans <script>
    return "\n".join([
        "---",
        "title: " + yaml_str(f"QCM automatismes {a.niveau} – {a.titre} (interactif, corrigé)"),
        "description: " + yaml_str(f"QCM en ligne d'automatismes de {a.niveau} en {a.titre.lower()} : "
        "chronomètre, score immédiat et correction détaillée, sans calculatrice."),
        "---",
        "",
        f"# QCM interactif — {a.titre}",
        "",
        "Entraînement **sans calculatrice**. Rien n'est enregistré ni envoyé : "
        "tout se passe dans le navigateur.",
        "",
        f"[← Énoncés et corrigés à lire](automatismes-{a.code}-{a.slug}.md)",
        "",
        '<div class="auto-qcm" data-banque="banque-automatismes"></div>',
        "",
        f'<script type="application/json" id="banque-automatismes">\n{donnees}\n</script>',
        "",
        "<noscript>Le QCM interactif nécessite JavaScript. "
        f'Les énoncés et corrigés sont aussi disponibles <a href="../automatismes-{a.code}-{a.slug}/">en lecture</a>.</noscript>',
        "",
    ])


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    p.add_argument("docs", type=Path)
    p.add_argument("--code", required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--titre", required=True)
    p.add_argument("--niveau", required=True)
    p.add_argument("--pdf", required=True)
    p.add_argument("--notion", required=True)
    a = p.parse_args()
    series = lire_series(a.source.read_text(encoding="utf-8"))
    dossier = a.docs / "automatismes"
    (dossier / f"automatismes-{a.code}-{a.slug}.md").write_text(page_lecture(series, a), encoding="utf-8")
    (dossier / f"qcm-{a.code}-{a.slug}.md").write_text(page_qcm(series, a), encoding="utf-8")
    for s in series:
        print(f"Série {s.lettre} ({s.duree}, {'QCM' if s.est_qcm else 'réponse libre'}) : "
              f"{len(s.questions)} questions — {s.theme}")


if __name__ == "__main__":
    main()
