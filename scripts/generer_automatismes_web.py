#!/usr/bin/env python3
"""Automatismes en ligne : génère, depuis les sources Beamer d'automatismes, les
pages MkDocs du site.

Pour chaque notion déclarée dans « automatismes_web.json » (à la racine du site) :

1. une page « lecture » : énoncés en texte (maths MathJax), figures, coups de
   pouce et corrigés repliables ;
2. une page « QCM interactif » : banque de questions embarquée en JSON, moteur
   en JavaScript pur (docs/javascripts/automatismes-qcm.js).

Le générateur met aussi à jour, entre des marqueurs qui lui sont réservés :
le menu « ⚡ Automatismes » de mkdocs.yml, l'encadré de docs/automatismes/index.md
et un lien dans chaque page notion (après le bloc AUTO-DOCS).

Les sources LaTeX ne sont jamais modifiées : elles sont seulement lues. Les
macros définies dans le préambule de chaque source (\\diapoquestions,
\\sixquestions, \\qcmitem, \\questionsframe…) sont développées avant la lecture,
si bien que les différents « dialectes » de sources se ramènent tous à des
frames Beamer ordinaires. Les figures TikZ sont compilées en SVG (pdflatex,
pdfcrop, pdftocairo) ; les tableaux de valeurs deviennent des tableaux HTML.

Usage (depuis la racine du site) :
    python3 scripts/generer_automatismes_web.py            # toutes les notions
    python3 scripts/generer_automatismes_web.py N03 N06-1  # seulement celles-ci
    python3 scripts/generer_automatismes_web.py --verifier # lire et contrôler sans rien écrire
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

VERSION_FIGURES = "1"          # à incrémenter pour forcer le recalcul des figures
LARGEUR_FIGURE_CM = 7.5        # largeur visée pour une figure TikZ
PX_PAR_PT = 1.8                # échelle d'affichage des SVG


class ErreurSource(Exception):
    pass


# ==========================================================================
# Lecture LaTeX : outils de base
# ==========================================================================

def sans_commentaires(tex: str) -> str:
    """Retire les commentaires « % » (comme TeX, un commentaire mange aussi la fin de ligne)."""
    lignes = tex.split("\n")
    sortie = []
    for ligne in lignes:
        i, coupe = 0, None
        while i < len(ligne):
            if ligne[i] == "\\":
                i += 2
                continue
            if ligne[i] == "%":
                coupe = i
                break
            i += 1
        if coupe is None:
            sortie.append(ligne + "\n")
        else:
            sortie.append(ligne[:coupe])
    return "".join(sortie)


def lire_groupe(t: str, i: int) -> tuple[str, int]:
    """t[i] == « { » : renvoie le contenu du groupe et l'indice après « } »."""
    if t[i] != "{":
        raise ErreurSource(f"accolade attendue : {t[i:i + 40]!r}")
    prof, debut = 0, i
    while i < len(t):
        c = t[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            prof += 1
        elif c == "}":
            prof -= 1
            if prof == 0:
                return t[debut + 1:i], i + 1
        i += 1
    raise ErreurSource(f"accolade non fermée : {t[debut:debut + 60]!r}")


def sauter_blancs(t: str, i: int) -> int:
    while i < len(t) and t[i].isspace():
        i += 1
    return i


def lire_argument(t: str, i: int) -> tuple[str, int]:
    """Argument non délimité à la manière de TeX : un groupe {…} ou un seul lexème."""
    i = sauter_blancs(t, i)
    if i >= len(t):
        raise ErreurSource("argument manquant en fin de texte")
    if t[i] == "{":
        return lire_groupe(t, i)
    if t[i] == "\\":
        m = re.match(r"\\([A-Za-z@]+|.)", t[i:])
        return m.group(0), i + m.end()
    return t[i], i + 1


def lire_optionnel(t: str, i: int) -> tuple[str | None, int]:
    j = sauter_blancs(t, i)
    if j >= len(t) or t[j] != "[":
        return None, i
    prof, k = 0, j
    while k < len(t):
        c = t[k]
        if c == "\\":
            k += 2
            continue
        if c == "{":
            prof += 1
        elif c == "}":
            prof -= 1
        elif c == "]" and prof == 0:
            return t[j + 1:k], k + 1
        k += 1
    raise ErreurSource("crochet non fermé")


def remplacer_commande(texte: str, nom: str, fonction) -> str:
    """Remplace chaque \\nom{arg} par fonction(arg) (accolades imbriquées gérées)."""
    motif = re.compile(r"\\" + nom + r"(?![A-Za-z])")
    sortie, pos = [], 0
    while (m := motif.search(texte, pos)):
        j = sauter_blancs(texte, m.end())
        if j >= len(texte) or texte[j] != "{":
            sortie.append(texte[pos:m.end()])
            pos = m.end()
            continue
        arg, fin = lire_groupe(texte, j)
        sortie.append(texte[pos:m.start()])
        sortie.append(fonction(arg))
        pos = fin
    sortie.append(texte[pos:])
    return "".join(sortie)


def environnements(t: str, nom: str) -> list[tuple[int, int, str]]:
    """Occurrences de premier niveau de \\begin{nom}…\\end{nom} : (début, fin, contenu)."""
    res, pos = [], 0
    ouvre, ferme = "\\begin{" + nom + "}", "\\end{" + nom + "}"
    while (d := t.find(ouvre, pos)) >= 0:
        prof, k = 0, d
        while True:
            o, f = t.find(ouvre, k), t.find(ferme, k)
            if f < 0:
                raise ErreurSource(f"environnement {nom} non fermé")
            if 0 <= o < f:
                prof, k = prof + 1, o + len(ouvre)
            else:
                prof, k = prof - 1, f + len(ferme)
                if prof == 0:
                    break
        res.append((d, k, t[d + len(ouvre):k - len(ferme)]))
        pos = k
    return res


# ==========================================================================
# Développement des macros du préambule
# ==========================================================================

@dataclass
class Macro:
    nargs: int
    defaut: str | None
    corps: str


# Environnements définis par \newenvironment dans la source en cours : nom -> (début, fin).
ENVIRONNEMENTS: dict[str, tuple[Macro, str]] = {}


GARDEES = {"bandeau", "numq", "pastille", "resultat", "resultattexte",
           "choixA", "choixB", "choixC", "choixD"}
MOTIF_FIGURE = re.compile(r"\\begin\{(?:tikzpicture|tabular|axis)\}|\\includegraphics|\\tkzTab")
MOTIF_STRUCTURE = re.compile(r"\\numq|\\choix|\\begin\{frame\}|#")


def lire_definition(t: str, i: int, nom_cmd: str, macros: dict[str, Macro]) -> int:
    """t[i:] commence juste après \\newcommand, \\def… ; enregistre la macro, renvoie la fin."""
    if nom_cmd in ("def", "gdef", "edef", "xdef"):
        m = re.match(r"\s*\\([A-Za-z@]+)", t[i:])
        nom, j = m.group(1), i + m.end()
        k = t.index("{", j)
        nargs = t[j:k].count("#")
        corps, fin = lire_groupe(t, k)
        macros[nom] = Macro(nargs, None, corps)
        return fin
    if nom_cmd in ("newenvironment", "renewenvironment"):
        nom, j = lire_argument(t, i)
        n, j = lire_optionnel(t, j)
        defaut, j = lire_optionnel(t, j)
        debut, j = lire_argument(t, j)
        fin_env, j = lire_argument(t, j)
        ENVIRONNEMENTS[nom.strip()] = (Macro(int(n) if n else 0, defaut, debut), fin_env)
        return j
    if nom_cmd == "DeclareMathOperator":
        j = i
        if t[j:j + 1] == "*":
            j += 1
        nom_brut, j = lire_argument(t, j)
        texte, fin = lire_argument(t, j)
        macros[nom_brut.strip().lstrip("\\")] = Macro(0, None, r"\operatorname{" + texte + "}")
        return fin
    j = i
    if t[j:j + 1] == "*":
        j += 1
    nom_brut, j = lire_argument(t, j)
    nom = nom_brut.strip().lstrip("\\")
    n, j = lire_optionnel(t, j)
    defaut, j = lire_optionnel(t, j)
    corps, fin = lire_argument(t, j)
    if nom_cmd == "providecommand" and nom in macros:
        return fin
    macros[nom] = Macro(int(n) if n else 0, defaut, corps)
    return fin


def substituer(corps: str, args: list[str]) -> str:
    def rempl(m: re.Match) -> str:
        if m.group(0) == "##":
            return "#"
        return args[int(m.group(1)) - 1]
    return re.sub(r"##|#([1-9])", rempl, corps)


DEFINITIONS = ("newcommand", "renewcommand", "providecommand",
               "def", "gdef", "edef", "xdef", "DeclareMathOperator",
               "newenvironment", "renewenvironment")


def lire_preambule(preambule: str) -> dict[str, Macro]:
    macros: dict[str, Macro] = {}
    ENVIRONNEMENTS.clear()
    motif = re.compile(r"\\(" + "|".join(DEFINITIONS) + r")(?![A-Za-z])")
    pos = 0
    while (m := motif.search(preambule, pos)):
        pos = lire_definition(preambule, m.end(), m.group(1), macros)
    return macros


def macros_figures(macros: dict[str, Macro]) -> set[str]:
    return {nom for nom, mac in macros.items()
            if mac.nargs == 0 and MOTIF_FIGURE.search(mac.corps)
            and not MOTIF_STRUCTURE.search(mac.corps)}


def developper(texte: str, macros: dict[str, Macro], gardees: set[str]) -> str:
    """Développe, de gauche à droite comme TeX, les macros définies dans la source.
    Les définitions rencontrées en cours de route (\\def, \\renewcommand) sont
    enregistrées puis retirées du texte."""
    sortie: list[str] = []
    i, etapes = 0, 0
    while i < len(texte):
        c = texte[i]
        if c != "\\":
            j = texte.find("\\", i)
            j = len(texte) if j < 0 else j
            sortie.append(texte[i:j])
            i = j
            continue
        m = re.match(r"\\([A-Za-z@]+)", texte[i:])
        if not m:
            sortie.append(texte[i:i + 2])
            i += 2
            continue
        nom, j = m.group(1), i + m.end()
        if nom in DEFINITIONS:
            i = lire_definition(texte, j, nom, macros)
            continue
        if nom in ("begin", "end") and texte[j:j + 1] == "{":
            env, k = lire_groupe(texte, j)
            if env in ENVIRONNEMENTS:
                mac, fin_env = ENVIRONNEMENTS[env]
                if nom == "end":
                    texte = fin_env + texte[k:]
                    i = 0
                    continue
                args, n = [], mac.nargs
                if mac.defaut is not None:
                    opt, k = lire_optionnel(texte, k)
                    args.append(mac.defaut if opt is None else opt)
                    n -= 1
                for _ in range(n):
                    a, k = lire_argument(texte, k)
                    args.append(a)
                texte = substituer(mac.corps, args) + texte[k:]
                i = 0
                continue
        if nom in macros and nom not in gardees:
            etapes += 1
            if etapes > 20000:
                raise ErreurSource("développement des macros sans fin (macro récursive ?)")
            mac = macros[nom]
            args = []
            n = mac.nargs
            if mac.defaut is not None:
                opt, j = lire_optionnel(texte, j)
                args.append(mac.defaut if opt is None else opt)
                n -= 1
            for _ in range(n):
                a, j = lire_argument(texte, j)
                args.append(a)
            corps = substituer(mac.corps, args)
            # « \R x » : TeX avale l'espace après \R ; on la garde, sans effet en HTML.
            texte = corps + texte[j:]
            i = 0
            continue
        sortie.append(texte[i:j])
        i = j
    return "".join(sortie)


# ==========================================================================
# Figures
# ==========================================================================

@dataclass
class Figure:
    latex: str             # code LaTeX autonome (macros du préambule autorisées)
    html: str = ""         # rempli au rendu


def tabular_en_html(latex: str, conv) -> str | None:
    """Convertit un tableau simple (tableau de valeurs) en <table>. None si trop complexe."""
    envs = environnements(latex.strip(), "tabular")
    if len(envs) != 1 or envs[0][0] != 0 or envs[0][1] != len(latex.strip()):
        return None
    contenu = envs[0][2]
    _, k = lire_groupe(contenu, sauter_blancs(contenu, 0))     # colonnes
    contenu = contenu[k:]
    if re.search(r"\\(multicolumn|multirow|begin)", contenu):
        return None
    lignes = [l for l in re.split(r"\\\\(?:\[[^\]]*\])?", contenu) if l.strip()]
    rangs = []
    for l in lignes:
        l = re.sub(r"\\(hline|cline\{[^}]*\})", "", l)
        cellules = [conv(c.strip()) for c in l.split("&")]
        balise = "th" if not rangs else "td"
        rangs.append("<tr>" + "".join(
            f"<{'th' if j == 0 else balise}>{c}</{'th' if j == 0 else balise}>"
            for j, c in enumerate(cellules)) + "</tr>")
    return '<div class="auto-figure"><table class="auto-tableau">' + "".join(rangs) + "</table></div>"


class Rendu:
    """Compile les figures TikZ en SVG, avec cache par empreinte."""

    def __init__(self, dossier: Path, prefixe: str, preambule: str, ecrire: bool):
        self.dossier, self.prefixe, self.preambule, self.ecrire = dossier, prefixe, preambule, ecrire
        self.produits: set[str] = set()

    def _compiler(self, latex: str, rep: Path) -> Path:
        doc = (self.preambule + "\n\\begin{document}\n\\begin{frame}[plain]\n\\centering\n"
               + latex + "\n\\end{frame}\n\\end{document}\n")
        (rep / "f.tex").write_text(doc, encoding="utf-8")
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "f.tex"],
                           cwd=rep, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            fin = "\n".join(r.stdout.splitlines()[-25:])
            raise ErreurSource(f"compilation de figure impossible :\n{fin}")
        subprocess.run(["pdfcrop", "--margins", "3", "f.pdf", "c.pdf"], cwd=rep,
                       capture_output=True, check=True, timeout=60)
        return rep / "c.pdf"

    @staticmethod
    def _largeur_pt(pdf: Path) -> float:
        r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True)
        m = re.search(r"Page size:\s*([\d.]+) x ([\d.]+)", r.stdout)
        return float(m.group(1))

    @staticmethod
    def _echelonner(latex: str, facteur: float) -> str:
        def opt(m: re.Match) -> str:
            options = m.group(1)
            if options is None:
                return f"\\begin{{tikzpicture}}[scale={facteur:.3f}]"
            if re.search(r"(?<![a-z ])scale\s*=", options):
                options = re.sub(r"(?<![a-z ])scale\s*=\s*([\d.]+)",
                                 lambda s: f"scale={float(s.group(1)) * facteur:.3f}", options)
            else:
                options = f"scale={facteur:.3f}," + options
            return f"\\begin{{tikzpicture}}[{options}]"
        return re.sub(r"\\begin\{tikzpicture\}(?:\[([^\]]*)\])?", opt, latex, count=1)

    def svg(self, latex: str, alt: str) -> str:
        # Sur une diapositive, \tiny reste lisible ; à l'écran d'un téléphone, non.
        latex = re.sub(r"\\tiny(?![A-Za-z])", r"\\footnotesize", latex)
        cle = hashlib.sha1((VERSION_FIGURES + self.preambule + latex).encode()).hexdigest()[:10]
        nom = f"{self.prefixe}-{cle}.svg"
        self.produits.add(nom)
        chemin = self.dossier / nom
        if self.ecrire and not chemin.exists():
            with tempfile.TemporaryDirectory() as tmp:
                rep = Path(tmp)
                pdf = self._compiler(latex, rep)
                if "tikzpicture" in latex:
                    facteur = LARGEUR_FIGURE_CM / 2.54 * 72 / self._largeur_pt(pdf)
                    facteur = max(1.0, min(facteur, 4.0))
                    if facteur > 1.15:
                        pdf = self._compiler(self._echelonner(latex, facteur), rep)
                subprocess.run(["pdftocairo", "-svg", str(pdf), str(rep / "f.svg")],
                               check=True, capture_output=True, timeout=60)
                self.dossier.mkdir(parents=True, exist_ok=True)
                shutil.copy(rep / "f.svg", chemin)
        largeur = ""
        if chemin.exists():
            m = re.search(r'<svg[^>]*\bwidth="([\d.]+)(pt)?"', chemin.read_text(encoding="utf-8")[:2000])
            if m:
                largeur = f' width="{round(float(m.group(1)) * PX_PAR_PT)}"'
        return (f'<div class="auto-figure"><img src="../figures/{nom}" alt="{html.escape(alt)}"'
                f'{largeur}></div>')

    def nettoyer(self) -> None:
        """Supprime les anciennes figures de cette notion qui ne servent plus."""
        if self.ecrire and self.dossier.exists():
            for f in self.dossier.glob(f"{self.prefixe}-*.svg"):
                if f.name not in self.produits:
                    f.unlink()


# ==========================================================================
# Conversion LaTeX → HTML (MathJax via la classe « arithmatex »)
# ==========================================================================

SEUIL_COUPURE = 24   # au-delà, une chaîne d'égalités est découpée pour le mobile
MISE_EN_FORME = (r"\\(?:tiny|scriptsize|footnotesize|small|normalsize|large|Large|LARGE|huge|Huge|"
                 r"bfseries|itshape|centering|raggedright|raggedleft|noindent|smallskip|medskip|"
                 r"bigskip|par|hfill|newline|linebreak|null|relax)(?![A-Za-z])")
AVERTISSEMENTS: list[str] = []


def segments_math(texte: str) -> list[tuple[bool, str]]:
    """Découpe en segments (est_math, contenu) selon $…$, \\(…\\) et \\[…\\]."""
    morceaux, dans_math, courant, i = [], False, [], 0
    imbrique = 0   # formule écrite dans une boîte de texte, elle-même dans une formule

    def couper(bascule: bool) -> None:
        nonlocal courant, dans_math
        morceaux.append((dans_math, "".join(courant)))
        courant, dans_math = [], bascule

    while i < len(texte):
        deux = texte[i:i + 2]
        if deux in ("\\(", "\\[") and not dans_math:
            couper(True)
            i += 2
            continue
        if deux == "\\(" and dans_math:
            imbrique += 1
            courant.append(deux)
            i += 2
            continue
        if deux == "\\)" and dans_math and imbrique:
            imbrique -= 1
            courant.append(deux)
            i += 2
            continue
        if deux in ("\\)", "\\]") and dans_math:
            couper(False)
            i += 2
            continue
        if texte[i] == "\\":
            courant.append(deux)
            i += 2
            continue
        if texte[i] == "$":
            couper(not dans_math)
            i += 1
            continue
        courant.append(texte[i])
        i += 1
    morceaux.append((dans_math, "".join(courant)))
    return [(m, s) for m, s in morceaux if s]


def normaliser_resultats(tex: str) -> str:
    """\\resultat{\\(x\\)} ou \\resultattexte{\\(x\\)} (formule dans la boîte) -> \\resultat{x}."""
    def un(a: str, nom: str) -> str:
        m = re.fullmatch(r"\s*\\\((.*)\\\)\s*", a, re.S)
        if m and "\\(" not in m.group(1):
            return "\\resultat{" + m.group(1) + "}"
        if "\\(" in a:          # texte et formule mêlés : boîte de texte
            return "\\resultattexte{" + a + "}"
        return "\\" + nom + "{" + a + "}"
    for nom in ("resultat", "resultattexte"):
        tex = remplacer_commande(tex, nom, lambda a, n=nom: un(a, n))
    return tex


def recomposer(segments: list[tuple[bool, str]]) -> str:
    return "".join(f"\\({s}\\)" if m else s for m, s in segments)


def couper_egalites(tex: str) -> list[str]:
    """Découpe après chaque « = » ou « \\Longleftrightarrow » de premier niveau
    (hors accolades), pour que le navigateur puisse aller à la ligne entre les
    morceaux : MathJax 3 ne coupe jamais une formule en ligne."""
    morceaux, debut, profondeur, i = [], 0, 0, 0
    while i < len(tex):
        c = tex[i]
        if c == "\\":
            m = re.match(r"\\(?:Longleftrightarrow|iff|Leftrightarrow)(?![A-Za-z])", tex[i:])
            if m and profondeur == 0:
                i += m.end()
                morceaux.append(tex[debut:i])
                debut = i
                continue
            i += 2
            continue
        if c == "{":
            profondeur += 1
        elif c == "}":
            profondeur -= 1
        elif c == "=" and profondeur == 0:
            morceaux.append(tex[debut:i + 1])
            debut = i + 1
        i += 1
    morceaux.append(tex[debut:])
    morceaux = [m for m in morceaux if m.strip()]
    # Avec des équivalences, couper seulement entre les équations, jamais au milieu.
    equiv = ("\\Longleftrightarrow", "\\iff", "\\Leftrightarrow")
    if any(m.rstrip().endswith(equiv) for m in morceaux):
        regroupes, courant = [], ""
        for m in morceaux:
            courant += m
            if m.rstrip().endswith(equiv):
                regroupes.append(courant)
                courant = ""
        if courant:
            regroupes.append(courant)
        morceaux = regroupes
    # Les \begin…\end (matrices) ne doivent jamais être coupés.
    if any(m.count("\\begin") != m.count("\\end") for m in morceaux):
        morceaux = ["".join(morceaux)]
    return morceaux


def preparer_math(tex: str) -> str:
    tex = remplacer_commande(tex, "resultat", lambda a: r"\boxed{" + a + "}")
    tex = remplacer_commande(tex, "resultattexte", lambda a: r"\boxed{\text{" + a + "}}")
    tex = remplacer_commande(tex, "ensuremath", lambda a: a)
    tex = re.sub(r"\\begin\{psmallmatrix\}", r"\\left(\\begin{smallmatrix}", tex)
    tex = re.sub(r"\\end\{psmallmatrix\}", r"\\end{smallmatrix}\\right)", tex)
    tex = re.sub(MISE_EN_FORME, "", tex)
    tex = re.sub(r"\\mj(textbf|textit|texttt|underline)", r"\\\1", tex)
    # formule dans une boîte de texte, dans une formule : \text{… $x$ …}
    tex = tex.replace("\\(", "$").replace("\\)", "$")
    return tex.strip()


def math_html(tex: str) -> str:
    tex = preparer_math(tex)
    if not tex:
        return ""
    morceaux = couper_egalites(tex) if len(tex) > SEUIL_COUPURE else [tex]
    return "<wbr>".join(
        f'<span class="arithmatex">\\({html.escape(m, quote=False)}\\)</span>' for m in morceaux)


class Convertisseur:
    def __init__(self, figures: list[Figure]):
        self.figures = figures

    def __call__(self, tex: str) -> str:
        return self.texte_html(tex)

    def texte_html(self, tex: str) -> str:
        """Convertit un fragment de texte LaTeX courant en HTML."""
        speciaux: list[str] = []

        def garder(h: str) -> str:
            speciaux.append(h)
            return f"\x00{len(speciaux) - 1}\x00"

        tex = re.sub(r"\\[vh]space\*?\{[^{}]*\}", " ", tex)
        tex = re.sub(r"\\(?:begin|end)\{(?:center|flushleft|flushright)\}", " ", tex)
        # Commandes de texte écrites dans une formule : on les traduit pour MathJax.
        # (\textbf, \texttt… dans une formule : MathJax les connaît, on les met à l'abri.)
        tex = recomposer([(m, re.sub(r"\\(textbf|textit|texttt|underline)(?![A-Za-z])", r"\\mj\1",
                                     remplacer_commande(remplacer_commande(
            s, "resultattexte", lambda a: r"\boxed{\text{" + a + "}}"), "emph", lambda a: r"\textit{" + a + "}"))
            if m else s) for m, s in segments_math(tex)])
        tex = re.sub(r"\\FIGURE\{(\d+)\}", lambda m: garder(self.figures[int(m.group(1))].html), tex)
        for nom, balise in (("resultattexte", "R"), ("textbf", "B"), ("textit", "I"),
                            ("emph", "I"), ("underline", "U"), ("texttt", "T")):
            tex = remplacer_commande(tex, nom, lambda a, b=balise: f"\x01{b}{a}\x02")
        morceaux = []
        for est_math, s in segments_math(tex):
            if est_math:
                morceaux.append(garder(math_html(s)))
                continue
            s = remplacer_commande(s, "resultat", lambda a: garder(math_html(r"\boxed{" + a + "}")))
            s = remplacer_commande(s, "text", lambda a: a)
            s = re.sub(r"\\\\(?:\[[^\]]*\])?", " ", s)
            s = re.sub(MISE_EN_FORME, " ", s)
            for avant, apres in ((r"\ldots", "…"), (r"\dots", "…"), (r"\og", "«\u00a0"),
                                 (r"\fg", "\u00a0»"), (r"\%", "%"), (r"\&", "&"), (r"\#", "#"),
                                 (r"\,", "\u202f"), (r"\ ", " "), ("~", "\u00a0"), ("---", "—"),
                                 ("--", "–"), (r"\qquad", " "), (r"\quad", " ")):
                s = s.replace(avant, apres)
            s = s.replace("{}", "")
            restes = re.findall(r"\\[A-Za-z]+", s)
            if restes:
                AVERTISSEMENTS.append("commande(s) ignorée(s) dans le texte : " + ", ".join(sorted(set(restes))))
                s = re.sub(r"\\[A-Za-z]+\*?", "", s)
            s = s.replace("{", "").replace("}", "")
            morceaux.append(html.escape(s, quote=False))
        h = "".join(morceaux)
        balises = {"R": ('<strong class="auto-resultat">', "</strong>"), "B": ("<strong>", "</strong>"),
                   "I": ("<em>", "</em>"), "U": ("<u>", "</u>"), "T": ("<code>", "</code>")}
        motif = re.compile(r"\x01([RBIUT])([^\x01\x02]*)\x02")
        while motif.search(h):
            h = motif.sub(lambda m: balises[m.group(1)][0] + m.group(2) + balises[m.group(1)][1], h)
        h = re.sub(r"\x00(\d+)\x00", lambda m: speciaux[int(m.group(1))], h)
        h = re.sub(r"\x00(\d+)\x00", lambda m: speciaux[int(m.group(1))], h)
        return re.sub(r"\s+", " ", h).strip()

    def items(self, bloc: str) -> list[str]:
        """Liste des \\item d'un itemize, ou le texte brut s'il n'y en a pas."""
        bloc = re.sub(r"\\(begin|end)\{(itemize|enumerate)\}(\[[^\]]*\])?", "", bloc)
        if "\\item" in bloc:
            return [h for x in bloc.split("\\item") if (h := self.texte_html(x))]
        h = self.texte_html(bloc)
        return [h] if h else []


# ==========================================================================
# Lecture des frames Beamer
# ==========================================================================

@dataclass
class Question:
    numero: int
    tex: str                       # énoncé LaTeX (pour l'analyse des dépendances)
    enonce: str                    # HTML
    choix: list[str] = field(default_factory=list)   # HTML, ordre A, B, C…
    corrige: str = ""              # HTML
    bonne: int | None = None       # indice de la bonne réponse pour un QCM
    contexte: list[int] = field(default_factory=list)  # numéros des questions dont celle-ci dépend


@dataclass
class Serie:
    lettre: str
    duree: str = ""
    theme: str = ""
    consigne: str = ""
    conseils: list[str] = field(default_factory=list)
    vigilance: list[str] = field(default_factory=list)
    methode: list[str] = field(default_factory=list)
    vigilance_corrige: list[str] = field(default_factory=list)
    figures: list[str] = field(default_factory=list)          # HTML
    figures_corrige: list[str] = field(default_factory=list)  # HTML
    questions: list[Question] = field(default_factory=list)

    @property
    def est_qcm(self) -> bool:
        return bool(self.questions) and all(q.choix for q in self.questions)


SUITE_DE_LIGNE = re.compile(r"\\\\(?:\[[^\]]*\])?\s*(?:\\(?:numq|pastille)\b|\\end\b|\\hline\b|\}|$)")


def fin_de_cellule(t: str, i: int) -> int:
    """Depuis i, avance jusqu'à la fin de la cellule : la question suivante, un
    « \\\\ » de premier niveau suivi d'une autre question (ou de la fin du bloc),
    un « & » de premier niveau, ou \\end du tableau englobant. Un « \\\\ » suivi
    d'autre chose (propositions de QCM sur une seconde ligne) ne coupe pas."""
    prof, envs = 0, []
    while i < len(t):
        if prof == 0 and not envs and re.match(r"\\(?:numq|pastille)\s*\{", t[i:]):
            return i
        if t.startswith("\\begin{", i):
            nom, j = lire_groupe(t, i + 6)
            envs.append(nom)
            i = j
            continue
        if t.startswith("\\end{", i):
            if not envs:
                return i
            _, j = lire_groupe(t, i + 4)
            envs.pop()
            i = j
            continue
        c = t[i]
        if c == "\\":
            if t.startswith("\\\\", i) and prof == 0 and not envs and SUITE_DE_LIGNE.match(t, i):
                return i
            i += 2
            continue
        if c == "{":
            prof += 1
        elif c == "}":
            if prof == 0:
                return i
            prof -= 1
        elif c == "&" and prof == 0 and not envs:
            return i
        i += 1
    return i


def lignes_numerotees(frame: str) -> list[tuple[int, str, int, int]]:
    """Lignes « \\numq{n} & contenu » : (n, contenu, début, fin)."""
    res = []
    for m in re.finditer(r"\\(?:numq|pastille)\s*\{(\d+)\}\s*&?", frame):
        fin = fin_de_cellule(frame, m.end())
        res.append((int(m.group(1)), frame[m.end():fin].strip(), m.start(), fin))
    return res


def degrouper(tex: str) -> str:
    """Retire les accolades de simple groupement en mode texte ({\\small …}),
    en gardant celles qui servent d'argument à une commande."""
    sortie, pile, i, math = [], [], 0, False
    while i < len(tex):
        deux = tex[i:i + 2]
        if deux in ("\\(", "\\[") and not math:
            math = True
            sortie.append(deux)
            i += 2
            continue
        if deux in ("\\)", "\\]") and math:
            math = False
            sortie.append(deux)
            i += 2
            continue
        c = tex[i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+\*?|.)", tex[i:])
            sortie.append(m.group(0))
            i += m.end()
            continue
        if not math and c == "{":
            avant = "".join(sortie[-3:])
            argument = bool(re.search(r"(\\[A-Za-z]+\*?|[}\]])\s*$", avant)) and not re.search(MISE_EN_FORME + r"\s*$", avant)
            pile.append(argument)
            if argument:
                sortie.append(c)
            i += 1
            continue
        if not math and c == "}" and pile:
            if pile.pop():
                sortie.append(c)
            i += 1
            continue
        sortie.append(c)
        i += 1
    return "".join(sortie)


BLANCS = r"(?:\s|~|\\quad|\\qquad|\\ |\\,|\\;|\\hfill|\\enspace)*"


def nettoyer_bords(tex: str) -> str:
    precedent = None
    while precedent != tex:
        precedent = tex
        tex = re.sub(r"\\\(" + BLANCS + r"\\\)", " ", tex)                 # formule vide
        tex = re.sub(r"\\\(" + BLANCS, r"\\(", tex)
        tex = re.sub(BLANCS + r"\\\)", r"\\)", tex)
        tex = re.sub(r"^" + BLANCS, "", tex)
        tex = re.sub(BLANCS + r"$", "", tex)
    return tex


def separer_choix(contenu: str) -> tuple[str, list[str]]:
    """Sépare l'énoncé et les propositions \\choixA…\\choixD (quelle que soit la mise en page)."""
    if not re.search(r"\\choix[A-D]", contenu):
        return contenu, []
    segs = []
    for est_math, s in segments_math(contenu):
        if est_math:
            if re.search(r"\\choix[A-D]", s):
                s = re.sub(r"\\choix([A-D])(?:\\ )?", r"\\)\\choix\1\\(", s)
            segs.append(f"\\({s}\\)")
        else:
            s = re.sub(r"\\begin\{minipage\}(?:\[[^\]]*\])?\{[^{}]*\}|\\end\{minipage\}", " ", s)
            s = re.sub(r"\\begin\{tabular\}\{(?:[^{}]|\{[^{}]*\})*\}|\\end\{tabular\}", " ", s)
            s = re.sub(r"\\\\(?:\[[^\]]*\])?|&", " ", s)
            s = re.sub(r"\\[vh]space\*?\{[^{}]*\}", " ", s)
            segs.append(s)
    c = degrouper("".join(segs))
    c = re.sub(MISE_EN_FORME, " ", c)
    morceaux = re.split(r"\\choix([A-D])(?:\\ )?", c)
    enonce, lettres, choix = morceaux[0], morceaux[1::2], morceaux[2::2]
    if "".join(lettres) != "ABCD"[:len(lettres)]:
        raise ErreurSource(f"propositions dans un ordre inattendu ({''.join(lettres)}) : {contenu[:80]!r}")
    return nettoyer_bords(enonce), [nettoyer_bords(x) for x in choix]


MOTIF_BONNE = re.compile(r"\\resultat(?:texte)?\s*\{\s*(?:[Rr]éponse\s+)?([A-D])(?=[\s.:,)}])[^{}]*\}")


MOTIF_BONNE_TEXTE = re.compile(r"(?<![A-Za-z])(?:bonne\s+)?[Rr]éponse\s*:?\s*([A-D])(?![A-Za-z])")


def analyser_corrige(contenu: str) -> tuple[int | None, str]:
    m = MOTIF_BONNE.search(contenu) or MOTIF_BONNE_TEXTE.search(contenu)
    if not m:
        return None, contenu
    reste = contenu[:m.start()] + contenu[m.end():]
    # Débris laissés par la lettre retirée (les propositions sont mélangées en
    # ligne) : formule vide « \(\) », « Ici la bonne réponse est », « donc »,
    # « , réponse » en fin de phrase.
    reste = re.sub(r"\\\(\s*\\\)|\$\s*\$", "", reste)
    reste = re.sub(r"(?i)(?:\bici\s+)?(?:\bla\s+)?bonne\s+réponse\s*(?:est\b)?\s*:?", "", reste)
    reste = re.sub(r"(?i)[\s,:;]*(?:\bdonc|\b(?:la\s+)?réponse(?:\s+est)?)\s*(?=[.:;,]*\s*$)", "", reste.strip())
    reste = re.sub(r"(?i)\b(?:la\s+)?réponse(?:\s+est)?\s*:?\s*[.;,]\s*", "", reste)
    reste = re.sub(r"^[\s.:;,]+", "", reste)
    reste = re.sub(r"\s*[.:;,][\s.:;,]*$", ".", reste.strip())
    if re.fullmatch(r"[\s.:;,]*", reste):
        reste = ""
    return "ABCD".index(m.group(1)), reste.strip()


def bloc_env(frame: str, env: str) -> str:
    envs = environnements(frame, env)
    return envs[0][2].strip() if envs else ""


def marquer_figures(frame: str, figures: list[Figure], noms_fig: set[str],
                    macros: dict[str, Macro]) -> str:
    """Remplace dans la frame chaque figure par \\FIGURE{k} (k : indice dans `figures`)."""
    def ajouter(latex: str) -> str:
        figures.append(Figure(latex))
        return f"\\FIGURE{{{len(figures) - 1}}}"

    for d, f, _ in reversed(environnements(frame, "tikzpicture")):
        frame = frame[:d] + ajouter(frame[d:f]) + frame[f:]
    if noms_fig:
        frame = re.sub(r"\\(" + "|".join(sorted(noms_fig, key=len, reverse=True)) + r")(?![A-Za-z])",
                       lambda m: ajouter(macros[m.group(1)].corps.strip()), frame)
    for d, f, contenu in reversed(environnements(frame, "tabular")):
        if not re.search(r"\\numq|\\choix|\\FIGURE", contenu):
            frame = frame[:d] + ajouter(frame[d:f]) + frame[f:]
    return frame


def texte_libre(frame: str, lignes: list[tuple[int, str, int, int]], nb_bandeau: int) -> str:
    """Ce qui reste dans une frame une fois retirés bandeau, blocs, tableau de
    questions et mise en page : une consigne écrite hors bloc, par exemple."""
    t = frame
    for _, _, d, f in lignes:                   # questions : remplacées par des blancs
        t = t[:d] + " " * (f - d) + t[f:]
    for d, f, contenu in reversed(environnements(t, "tabular")):
        if not re.search(r"[A-Za-zÀ-ÿ]{3}", re.sub(r"\\begin\{tabular\}\{(?:[^{}]|\{[^{}]*\})*\}|\\end\{tabular\}|\\[A-Za-z]+", "", contenu)):
            t = t[:d] + t[f:]
    for env in ("blocconsigne", "blocconseils", "blocvigilance", "blocmethode"):
        for d, f, _ in reversed(environnements(t, env)):
            t = t[:d] + t[f:]
    m = re.search(r"\\bandeau", t)
    if m:
        j = m.end()
        for _ in range(nb_bandeau):
            _, j = lire_argument(t, j)
        t = t[:m.start()] + t[j:]
    t = re.sub(r"\\\\(?:\[[^\]]*\])?|&", " ", t)
    t = re.sub(r"\\begin\{columns\}(\[[^\]]*\])?|\\end\{columns\}", " ", t)
    t = re.sub(r"\\begin\{column\}(\[[^\]]*\])?\{[^{}]*\}|\\end\{column\}", " ", t)
    t = re.sub(r"\\(begin|end)\{(center|flushleft|flushright)\}", " ", t)
    t = re.sub(r"\\FIGURE\{\d+\}", " ", t)
    t = re.sub(r"^\s*\[[^\]]*\]", " ", t)          # options de la frame
    t = re.sub(r"\\[vh]space\*?\{[^{}]*\}", " ", t)
    t = re.sub(MISE_EN_FORME, " ", t)
    t = degrouper(t)
    return t.strip() if re.search(r"[A-Za-zÀ-ÿ]{3}", t) else ""


DUREE = re.compile(r"(\d+\s*(?:min(?:utes?)?|s))")


def dependances(serie: Serie) -> None:
    """Repère les questions qui n'ont de sens qu'avec une question précédente
    (« question 3 », « correspondante », fonction définie plus haut…)."""
    for k, q in enumerate(serie.questions):
        avant = serie.questions[:k]
        refs: set[int] = set()
        for m in re.finditer(r"(?i)question\s+(\d+)", q.tex):
            refs.add(int(m.group(1)))
        if re.search(r"(?i)correspondante?s?(?!\s+(?:à|au|aux)\b)|précédente?s?\b|ci-dessus|même figure|même fonction", q.tex):
            refs.update(p.numero for p in avant)
        if MOTIF_REPRISE.search(q.tex):
            refs.update(p.numero for p in avant)
        for p in avant:
            for lettre in set(re.findall(r"(?<![A-Za-z\\])([A-Za-z])\s*\(\s*x\s*\)\s*=", p.tex)):
                definie_ici = re.search(r"(?<![A-Za-z\\])" + lettre + r"\s*\(\s*x\s*\)\s*=", q.tex)
                if not definie_ici and re.search(r"(?<![A-Za-z\\])" + lettre + r"(?![A-Za-z])", q.tex):
                    refs.add(p.numero)
        # Question sans données propres (« Calculer \(P(B)\) ») qui reprend un
        # objet nommé plus haut (événement, variable, point, chemin d'arbre).
        if not q.choix and not porte_ses_donnees(q.tex):
            symboles = majuscules(q.tex)
            for p in avant:
                if symboles & majuscules(p.tex):
                    refs.add(p.numero)
        for p in avant:   # les questions reprises emportent leur propre contexte
            if p.numero in refs:
                refs.update(p.contexte)
        q.contexte = sorted(r for r in refs if r != q.numero and any(p.numero == r for p in avant))


# Reprise explicite d'une question précédente : « avec la même suite », « ce tableau »…
MOTIF_REPRISE = re.compile(
    r"(?i)\b(?:la|le|les|du|des|au|aux)\s+m[êe]mes?\b|\bm[êe]mes\s+données\b|\b(?:ce|cet|cette|ces)\s+(?:tableau|liste|suite|droite|données|deux|points?|contexte|"
    r"fréquence|nuage|arbre|programme|algorithme|valeurs?|résultats?|situation|modèle)\b|\bdéduire\b")
# Mots qui introduisent des données dans l'énoncé lui-même.
MOTIF_DONNEES = re.compile(r"(?i)\b(?:si|soit|pour|avec|on\s+a|on\s+répète|vérifie|passe|prend|vaut|valeurs?)\b")


def porte_ses_donnees(tex: str) -> bool:
    """Vrai si l'énoncé apporte ses propres données : mot introducteur, ou nombre
    écrit hors parenthèses (« Calculer \\(P(X\\geqslant 10)\\) » n'en apporte pas)."""
    if MOTIF_DONNEES.search(tex):
        return True
    sans_parentheses = re.sub(r"\\[()\[\]]", " ", tex)
    if re.search(r"\(\s*-?\s*\d[^()]*;", sans_parentheses):   # coordonnées A(1;2)
        return True
    while True:
        reduit = re.sub(r"\([^()]*\)", " ", sans_parentheses)
        if reduit == sans_parentheses:
            break
        sans_parentheses = reduit
    return bool(re.search(r"\d", re.sub(r"\\[A-Za-z]+", " ", sans_parentheses)))


def majuscules(tex: str) -> set[str]:
    """Lettres majuscules qui nomment un objet dans une formule (A, B, X, G, S…),
    hors P (probabilité), E (espérance) et ensembles \\mathscr/\\mathbb."""
    lettres: set[str] = set()
    for est_math, s in segments_math(tex):
        if not est_math:
            continue
        s = re.sub(r"\\(?:mathscr|mathcal|mathbb)\s*\{?[A-Z]\}?", " ", s)
        s = re.sub(r"\\[A-Za-z]+", " ", s)
        s = re.sub(r"\\text\{[^}]*\}", " ", s)
        for mot in re.findall(r"(?<![A-Za-z])[A-Z]+(?![A-Za-z])", s):
            if len(mot) <= 3:
                lettres.update(mot)
    return lettres - {"P", "E"}


VIRGULE_ENTRE_NOMBRES = re.compile(r"(?<![\d.{])-?\d+(?:\{,\}\d+)?\s*,\s*(?:\\[ ,]|~)*\s*-?\d")


def signaler_virgules(corps: str) -> None:
    """Liste de nombres séparés par « , » dans une formule : ambigu en français
    (2,5 = 2 + 5/10). La source doit écrire « ; » (charte 02, § Séparateur)."""
    for est_math, s in segments_math(corps):
        if est_math:
            s = re.sub(r"\\texttt\{[^}]*\}", "", s)
            for m in VIRGULE_ENTRE_NOMBRES.finditer(s):
                AVERTISSEMENTS.append(f"nombres séparés par une virgule (écrire « ; ») : {s[max(0, m.start() - 15):m.end() + 10]!r}")


def lire_series(source: str, rendu: Rendu | None) -> list[Serie]:
    source = sans_commentaires(source)
    if "\\begin{document}" not in source:
        raise ErreurSource("\\begin{document} introuvable")
    preambule, corps = source.split("\\begin{document}", 1)
    corps = corps.split("\\end{document}", 1)[0]
    macros = lire_preambule(preambule)
    noms_fig = macros_figures(macros)
    corps = developper(corps, macros, GARDEES | noms_fig)
    corps = normaliser_resultats(corps)
    signaler_virgules(corps)

    nb_bandeau = macros["bandeau"].nargs if "bandeau" in macros else 3
    figures: list[Figure] = []
    conv = Convertisseur(figures)
    series: dict[str, Serie] = {}
    frames = [c for _, _, c in environnements(corps, "frame")]
    for frame in frames:
        mb = re.search(r"\\bandeau(?![A-Za-z])", frame)
        if not mb:
            continue
        a1, j = lire_argument(frame, mb.end())
        a2, j = lire_argument(frame, j)
        a3, j = lire_argument(frame, j) if nb_bandeau >= 3 else ("", j)
        ml = re.search(r"Série\s+([A-Z])", a2) or re.search(r"Série\s+([A-Z])", a1 + a3)
        if not ml:
            continue
        lettre = ml.group(1)
        theme = conv.texte_html(a3)
        n0 = len(figures)
        frame = marquer_figures(frame, figures, noms_fig, macros)
        for fig in figures[n0:]:
            fig.html = rendre_figure(fig, conv, rendu, f"Figure de la série {lettre}")
        lignes = lignes_numerotees(frame)
        dans_lignes = set()
        for _, contenu, _, _ in lignes:
            dans_lignes.update(int(x) for x in re.findall(r"\\FIGURE\{(\d+)\}", contenu))
        figures_frame = [figures[k].html for k in range(n0, len(figures)) if k not in dans_lignes]
        libre = texte_libre(frame, lignes, nb_bandeau)
        correction = bool(re.search(r"(?i)correction|corrig", a1 + " " + a2))

        if not correction:
            serie = series.setdefault(lettre, Serie(lettre))
            md = DUREE.search(a2)
            serie.duree = md.group(1) if md else ""
            serie.theme = theme if nb_bandeau >= 3 else ""
            consigne = conv.texte_html(bloc_env(frame, "blocconsigne"))
            if libre:
                consigne = (consigne + " " + conv.texte_html(libre)).strip()
            serie.consigne = consigne
            serie.conseils = conv.items(bloc_env(frame, "blocconseils"))
            serie.vigilance = conv.items(bloc_env(frame, "blocvigilance"))
            serie.figures = figures_frame
            for num, contenu, _, _ in lignes:
                enonce, choix = separer_choix(contenu)
                serie.questions.append(Question(num, enonce, conv.texte_html(enonce),
                                                [conv.texte_html(c) for c in choix]))
        else:
            if lettre not in series:
                raise ErreurSource(f"correction de la série {lettre} avant ses questions")
            serie = series[lettre]
            serie.methode = conv.items(bloc_env(frame, "blocmethode"))
            serie.vigilance_corrige = conv.items(bloc_env(frame, "blocvigilance"))
            serie.figures_corrige = figures_frame
            for num, contenu, _, _ in lignes:
                q = next((x for x in serie.questions if x.numero == num), None)
                if q is None:
                    raise ErreurSource(f"Série {lettre} : corrigé de la question {num} sans énoncé")
                if q.choix:
                    bonne, reste = analyser_corrige(contenu)
                    q.bonne = bonne
                    q.corrige = conv.texte_html(reste)
                    if bonne is not None and not q.corrige:
                        q.corrige = q.choix[bonne]
                else:
                    q.corrige = conv.texte_html(contenu)
    if not series:
        raise ErreurSource("aucune série lue : format de source non reconnu")
    for s in series.values():
        if not s.questions:
            raise ErreurSource(f"Série {s.lettre} : aucune question lue")
        for q in s.questions:
            if q.choix and q.bonne is None:
                raise ErreurSource(f"Série {s.lettre} Q{q.numero} : bonne réponse introuvable")
            if q.choix and q.bonne >= len(q.choix):
                raise ErreurSource(f"Série {s.lettre} Q{q.numero} : bonne réponse hors des propositions")
            if not q.corrige:
                raise ErreurSource(f"Série {s.lettre} Q{q.numero} : corrigé manquant")
        dependances(s)
    return [series[k] for k in sorted(series)]


def rendre_figure(fig: Figure, conv: Convertisseur, rendu: Rendu | None, alt: str) -> str:
    tableau = tabular_en_html(fig.latex, conv.texte_html)
    if tableau:
        return tableau
    if rendu is None:
        return '<div class="auto-figure">[figure]</div>'
    return rendu.svg(fig.latex, alt)


# ==========================================================================
# Écriture de la page « lecture »
# ==========================================================================

def yaml_str(s: str) -> str:
    """Chaîne YAML sûre (JSON est un sous-ensemble de YAML)."""
    return json.dumps(s, ensure_ascii=False)


def indenter(lignes: list[str], n: int = 4) -> list[str]:
    return [(" " * n + l) if l else "" for l in lignes]


def liste_html(elements: list[str]) -> str:
    if len(elements) == 1:
        return f"<p>{elements[0]}</p>"
    return "<ul>" + "".join(f"<li>{e}</li>" for e in elements) + "</ul>"


@dataclass
class Notion:
    id: str
    code: str
    slug: str
    titre: str
    source: Path
    pdf: str
    notion: str
    niveau: str

    @property
    def page(self) -> str:
        return f"automatismes-{self.code}-{self.slug}.md"

    @property
    def page_qcm(self) -> str:
        return f"qcm-{self.code}-{self.slug}.md"


def titre_court(n: Notion) -> str:
    return n.titre[0].lower() + n.titre[1:] if not n.titre[:2].isupper() else n.titre


def page_lecture(series: list[Serie], n: Notion) -> str:
    nb_q = sum(len(s.questions) for s in series)
    L = [
        "---",
        "title: " + yaml_str(f"Automatismes {n.niveau} – {n.titre} : exercices et QCM corrigés"),
        "description: " + yaml_str(f"{nb_q} questions d'automatismes de {n.niveau} ({titre_court(n)}), "
                                   f"sans calculatrice, en {len(series)} séries chronométrées, "
                                   "avec corrigés détaillés et QCM interactif."),
        "---",
        "",
        f"# Automatismes {n.code} — {n.titre}",
        "",
        f"{nb_q} questions **sans calculatrice**, réparties en {len(series)} séries courtes "
        "à faire en quelques minutes. Chercher d'abord seul, puis ouvrir le corrigé.",
        "",
        '<div class="auto-actions" markdown>',
        f"[⚡ Faire le QCM interactif]({n.page_qcm}){{ .md-button .md-button--primary }}",
        f"[📄 Diaporama PDF à projeter]({n.pdf}){{ .md-button }}",
        f"[📖 Revoir la notion]({n.notion}){{ .md-button }}",
        "</div>",
        "",
    ]
    for s in series:
        titre = s.theme.replace(" — ", " : ", 1)
        L += [f"## Série {s.lettre} — {titre}", ""]
        if s.duree:
            L += [f'<p class="auto-meta">⏱ {s.duree} · Calculatrice interdite</p>', ""]
        if s.consigne:
            L += ['<div class="auto-consigne" markdown>',
                  f"**Consigne.** {s.consigne}", "</div>", ""]
        for fig in s.figures:
            L += [fig, ""]
        L.append('<ol class="auto-questions">')
        for q in s.questions:
            bloc = f'<li value="{q.numero}">{q.enonce}'
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
        interne = list(s.figures_corrige)
        interne.append('<ol class="auto-corrige">')
        for q in s.questions:
            if q.choix:
                interne.append(f'<li value="{q.numero}"><strong class="auto-resultat">Réponse {"ABCD"[q.bonne]}</strong> : {q.corrige}</li>')
            else:
                interne.append(f'<li value="{q.numero}">{q.corrige}</li>')
        interne.append("</ol>")
        if s.methode:
            interne.append(f'<div class="auto-methode"><strong>Méthode.</strong> {" ".join(s.methode)}</div>')
        if s.vigilance_corrige:
            interne.append(f'<div class="auto-vigilance"><strong>Vigilance.</strong> {" ".join(s.vigilance_corrige)}</div>')
        L += indenter(interne) + [""]
    L += [
        "---",
        "",
        f"*Ces questions reprennent le diaporama d'automatismes {n.code} utilisé en classe. "
        "Licence CC BY-NC-SA 4.0 : réutilisation libre en classe, en citant la source.*",
        "",
    ]
    return "\n".join(L)


# ==========================================================================
# Écriture de la page « QCM interactif »
# ==========================================================================

def banque(series: list[Serie], n: Notion) -> dict:
    questions = []
    for s in series:
        for q in s.questions:
            contexte = [f"<strong>Q{p.numero}.</strong> {p.enonce}"
                        for p in s.questions if p.numero in q.contexte]
            questions.append({
                "id": f"{n.id}-{s.lettre}{q.numero}",
                "serie": s.lettre,
                "theme": s.theme,
                "type": "qcm" if q.choix else "flash",
                "enonce": q.enonce,
                "contexte": contexte,
                "choix": q.choix,
                "bonne": q.bonne,
                "corrige": q.corrige,
                "methode": " ".join(s.methode),
            })
    return {
        "notion": n.code,
        "cle": n.id,
        "titre": n.titre,
        "niveau": n.niveau,
        "series": [{"lettre": s.lettre, "theme": s.theme, "duree": s.duree,
                    "consigne": s.consigne, "qcm": s.est_qcm,
                    "figure": "".join(s.figures)} for s in series],
        "questions": questions,
    }


def page_qcm(series: list[Serie], n: Notion) -> str:
    donnees = json.dumps(banque(series, n), ensure_ascii=False, indent=1)
    donnees = donnees.replace("</", "<\\/")  # sûreté dans <script>
    return "\n".join([
        "---",
        "title: " + yaml_str(f"QCM automatismes {n.niveau} – {n.titre} (interactif, corrigé)"),
        "description: " + yaml_str(f"QCM en ligne d'automatismes de {n.niveau} ({titre_court(n)}) : "
                                   "chronomètre, score immédiat et correction détaillée, sans calculatrice."),
        "---",
        "",
        f"# QCM interactif — {n.titre}",
        "",
        "Entraînement **sans calculatrice**. Rien n'est enregistré ni envoyé : "
        "tout se passe dans le navigateur.",
        "",
        f"[← Énoncés et corrigés à lire]({n.page})",
        "",
        '<div class="auto-qcm" data-banque="banque-automatismes"></div>',
        "",
        f'<script type="application/json" id="banque-automatismes">\n{donnees}\n</script>',
        "",
        "<noscript>Le QCM interactif nécessite JavaScript. "
        f'Les énoncés et corrigés sont aussi disponibles <a href="../{n.page[:-3]}/">en lecture</a>.</noscript>',
        "",
    ])


# ==========================================================================
# Liens : menu, index des automatismes, pages notions
# ==========================================================================

DEBUT, FIN = "<!-- AUTOMATISMES-WEB:START -->", "<!-- AUTOMATISMES-WEB:END -->"
MASQUE_DEBUT = '<div class="auto-docs-masque" hidden markdown="1">'
MASQUE_FIN = "</div>"


def remplacer_bloc(texte: str, bloc: str, ancre_apres: str | None) -> str:
    """Remplace le bloc balisé, ou l'insère après `ancre_apres` (ou en fin de texte)."""
    complet = f"{DEBUT}\n{bloc}\n{FIN}"
    if DEBUT in texte and FIN in texte:
        return re.sub(re.escape(DEBUT) + r".*?" + re.escape(FIN), lambda _: complet, texte, flags=re.S)
    if ancre_apres and ancre_apres in texte:
        i = texte.index(ancre_apres) + len(ancre_apres)
        return texte[:i] + "\n\n" + complet + texte[i:]
    return texte.rstrip("\n") + "\n\n" + complet + "\n"


def maj_index(docs: Path, notions: list[Notion]) -> None:
    chemin = docs / "automatismes" / "index.md"
    texte = chemin.read_text(encoding="utf-8")
    # ancien encadré du prototype (avant la généralisation)
    texte = re.sub(r'!!! tip "Nouveau : les automatismes en ligne"\n\n    .*?\n\n', "", texte, flags=re.S)
    lignes = ['!!! tip "Automatismes en ligne : énoncés corrigés et QCM interactif"', "",
              "    Sans rien télécharger : questions à l'écran, corrigés repliables et QCM chronométré.", ""]
    for n in notions:
        lignes.append(f"    - **{n.code} — {n.titre}** : [énoncés et corrigés]({n.page}) · "
                      f"[QCM interactif]({n.page_qcm}) · [diaporama PDF]({n.pdf})")
    texte = remplacer_bloc(texte, "\n".join(lignes) + "\n", "Exercices d'automatismes et mini-tests, classés par notion.")
    # L'ancienne liste des PDF (zone AUTO-DOCS, régénérée par l'outil de publication)
    # fait doublon : on la masque à l'affichage sans toucher à ses marqueurs, sinon
    # l'outil la recréerait en bas de page.
    if not texte.startswith("---\n"):
        texte = "---\nhide:\n  - toc\n---\n\n" + texte      # titres masqués : pas de sommaire
    if MASQUE_DEBUT not in texte and "<!-- AUTO-DOCS:START -->" in texte:
        texte = texte.replace("<!-- AUTO-DOCS:START -->", MASQUE_DEBUT + "\n\n<!-- AUTO-DOCS:START -->", 1)
        texte = texte.replace("<!-- AUTO-DOCS:END -->", "<!-- AUTO-DOCS:END -->\n\n" + MASQUE_FIN, 1)
    chemin.write_text(texte, encoding="utf-8")


def maj_notions(docs: Path, notions: list[Notion]) -> None:
    par_page: dict[Path, list[Notion]] = {}
    for n in notions:
        chemin = (docs / "automatismes" / n.notion).resolve()
        par_page.setdefault(chemin, []).append(n)
    for chemin, liste in par_page.items():
        if not chemin.exists():
            AVERTISSEMENTS.append(f"page notion introuvable : {chemin}")
            continue
        texte = chemin.read_text(encoding="utf-8")
        # ancien lien du prototype
        texte = re.sub(r"\n- ⚡ \[Automatismes [^\]]* en ligne : [^\]]*\]\([^)]*\)\n", "\n", texte)
        lignes = [f"- ⚡ [Automatismes {n.code} en ligne{(' — ' + n.titre.split(':')[0].strip()) if len(liste) > 1 else ''} : "
                  f"énoncés, corrigés et QCM interactif](../automatismes/{n.page})" for n in liste]
        texte = remplacer_bloc(texte, "\n".join(lignes), "<!-- AUTO-DOCS:END -->")
        chemin.write_text(texte, encoding="utf-8")


def maj_menu(racine: Path, notions: list[Notion]) -> None:
    chemin = racine / "mkdocs.yml"
    lignes = chemin.read_text(encoding="utf-8").split("\n")
    k = next((i for i, l in enumerate(lignes) if re.match(r'\s*- "⚡ Automatismes":', l)), None)
    if k is None:
        AVERTISSEMENTS.append("menu « ⚡ Automatismes » introuvable dans mkdocs.yml : non modifié")
        return
    indent = len(lignes[k]) - len(lignes[k].lstrip())
    fin = k + 1
    while fin < len(lignes) and lignes[fin].strip() and (len(lignes[fin]) - len(lignes[fin].lstrip())) > indent:
        fin += 1
    pad = " " * (indent + 4)
    bloc = [" " * indent + '- "⚡ Automatismes":', pad + "- automatismes/index.md"]
    for n in notions:
        bloc.append(pad + "- " + yaml_str(f"{n.code} — {n.titre} (en ligne)") + f": automatismes/{n.page}")
    lignes[k:fin] = bloc
    chemin.write_text("\n".join(lignes), encoding="utf-8")


# ==========================================================================
# Programme principal
# ==========================================================================

def charger_config(chemin: Path) -> list[Notion]:
    conf = json.loads(chemin.read_text(encoding="utf-8"))
    racine_src = Path(conf["source_racine"]).expanduser()
    return [Notion(id=e.get("id", e["code"]), code=e["code"], slug=e["slug"], titre=e["titre"],
                   source=racine_src / e["source"], pdf=e["pdf"], notion=e["notion"],
                   niveau=conf["niveau"]) for e in conf["notions"]]


def main() -> int:
    racine = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ids", nargs="*", help="identifiants des notions à traiter (défaut : toutes)")
    p.add_argument("--config", type=Path, default=racine / "automatismes_web.json")
    p.add_argument("--verifier", action="store_true", help="lire et contrôler sans rien écrire")
    a = p.parse_args()

    toutes = charger_config(a.config)
    choisies = [n for n in toutes if not a.ids or n.id in a.ids]
    inconnues = set(a.ids) - {n.id for n in toutes}
    if inconnues:
        print("Notion(s) absente(s) de la configuration :", ", ".join(sorted(inconnues)), file=sys.stderr)
        return 2
    docs = racine / "docs"
    erreurs = 0
    for n in choisies:
        print(f"— {n.id} : {n.source.name}")
        AVERTISSEMENTS.clear()
        try:
            src = n.source.read_text(encoding="utf-8")
            preambule = sans_commentaires(src).split("\\begin{document}", 1)[0]
            rendu = Rendu(docs / "automatismes" / "figures", f"{n.code}-{n.slug}", preambule,
                          ecrire=not a.verifier)
            series = lire_series(src, rendu)
        except (ErreurSource, OSError, subprocess.SubprocessError) as e:
            print(f"  ERREUR : {e}", file=sys.stderr)
            erreurs += 1
            continue
        for s in series:
            nb_qcm = sum(1 for q in s.questions if q.choix)
            dep = [f"Q{q.numero}←{','.join(map(str, q.contexte))}" for q in s.questions if q.contexte]
            print(f"  Série {s.lettre} ({s.duree or 'durée ?'}) : {len(s.questions)} questions"
                  f"{f', dont {nb_qcm} QCM' if nb_qcm else ''}"
                  f"{f', {len(s.figures)} figure(s)' if s.figures else ''}"
                  f"{f', dépendances {dep}' if dep else ''} — {re.sub('<[^>]+>', '', s.theme)}")
        for w in sorted(set(AVERTISSEMENTS)):
            print(f"  avertissement : {w}")
        if not a.verifier:
            dossier = docs / "automatismes"
            (dossier / n.page).write_text(page_lecture(series, n), encoding="utf-8")
            (dossier / n.page_qcm).write_text(page_qcm(series, n), encoding="utf-8")
            rendu.nettoyer()
    if not a.verifier and not erreurs:
        AVERTISSEMENTS.clear()
        maj_index(docs, toutes)
        maj_notions(docs, toutes)
        maj_menu(racine, toutes)
        for w in AVERTISSEMENTS:
            print(f"avertissement : {w}")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
