#!/usr/bin/env python3
"""Rend cliquables les bulles de la carte de progression (docs/progression.md).

Principe : pour chaque bulle déclarée dans scripts/carte_progression_zones.json
(point d'amorce à l'intérieur de la bulle + lien + libellé), le script remplit
la bulle depuis ce point pour trouver son contour, puis écrit dans
docs/progression.md, entre les marqueurs CARTE-PROGRESSION, des liens
transparents positionnés en pourcentages par-dessus l'image (donc corrects à
toute largeur d'écran).

À relancer seulement si l'image de la carte change :
    python3 scripts/carte_progression.py            # met à jour la page
    python3 scripts/carte_progression.py --controle out.png   # + image de contrôle

Si une bulle n'est pas trouvée (amorce posée sur du texte ou un trait),
déplacer légèrement son point « amorce » dans le JSON.
"""
import argparse
import json
import re
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

RACINE = Path(__file__).resolve().parent.parent
ZONES = RACINE / "scripts" / "carte_progression_zones.json"
PAGE = RACINE / "docs" / "progression.md"
DEBUT, FIN = "<!-- CARTE-PROGRESSION:DEBUT -->", "<!-- CARTE-PROGRESSION:FIN -->"


def contour(a, x, y, larg_max=190, haut_max=135):
    """Plus grande région claire et homogène contenant (x, y), essayée depuis
    plusieurs amorces voisines (le texte de la bulle coupe la région)."""
    H, W, _ = a.shape
    meilleur = None
    for ox in range(-30, 31, 10):
        for oy in range(-30, 31, 10):
            sx, sy = x + ox, y + oy
            if a[sy, sx].min() < 200:
                continue
            ref = a[sy, sx]
            vu = np.zeros((H, W), bool)
            vu[sy, sx] = True
            file, xs, ys = deque([(sx, sy)]), [], []
            while file and len(xs) < 20000:
                cx, cy = file.popleft()
                xs.append(cx)
                ys.append(cy)
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < W and 0 <= ny < H and not vu[ny, nx] \
                            and np.abs(a[ny, nx] - ref).sum() < 40:
                        vu[ny, nx] = True
                        file.append((nx, ny))
            if len(xs) >= 20000:
                continue
            bb = (min(xs), min(ys), max(xs), max(ys))
            if not (bb[0] < x < bb[2] and bb[1] < y < bb[3]):
                continue
            if bb[2] - bb[0] > larg_max or bb[3] - bb[1] > haut_max:
                continue
            if meilleur is None or len(xs) > meilleur[1]:
                meilleur = (bb, len(xs))
    return meilleur[0] if meilleur else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--controle", help="image PNG de contrôle (contours en rouge)")
    args = p.parse_args()

    cfg = json.loads(ZONES.read_text(encoding="utf-8"))
    img_path = RACINE / "docs" / cfg["image"]
    img = Image.open(img_path).convert("RGB")
    W, H = img.size
    a = np.asarray(img).astype(int)

    liens, boites = [], {}
    for z in cfg["zones"]:
        bb = contour(a, *z["amorce"], cfg.get("largeur_max", 190), cfg.get("hauteur_max", 135))
        if bb is None:
            raise SystemExit(f"Bulle introuvable : {z['libelle']} (déplacer l'amorce)")
        boites[z["libelle"]] = bb
        x0, y0, x1, y1 = bb
        style = (f"left:{100 * x0 / W:.2f}%;top:{100 * y0 / H:.2f}%;"
                 f"width:{100 * (x1 - x0) / W:.2f}%;height:{100 * (y1 - y0) / H:.2f}%")
        liens.append(f'[{z["libelle"]}]({z["lien"]}){{.bulle-progression '
                     f'style="{style}" title="{z["libelle"]}"}}')

    bloc = "\n".join([
        DEBUT,
        '<div class="carte-progression-cadre" markdown="1">',
        '<button type="button" class="carte-fermer" aria-label="Fermer la carte agrandie">✕ Fermer</button>',
        f'<div class="carte-progression" markdown="1" style="--ratio:{W / H:.4f}">',
        "",
        f'![{cfg["alt"]}]({cfg["image"]})',
        "",
        *liens,
        "",
        "</div>",
        "</div>",
        "",
        '<button type="button" class="carte-agrandir md-button">Agrandir la carte (plein écran, bulles cliquables)</button>',
        FIN,
    ])
    texte = PAGE.read_text(encoding="utf-8")
    motif = re.compile(re.escape(DEBUT) + ".*?" + re.escape(FIN), re.S)
    if not motif.search(texte):
        raise SystemExit(f"Marqueurs {DEBUT} … {FIN} absents de {PAGE}")
    PAGE.write_text(motif.sub(lambda _: bloc, texte), encoding="utf-8")
    print(f"{len(liens)} bulles cliquables écrites dans {PAGE.relative_to(RACINE)}")

    if args.controle:
        d = ImageDraw.Draw(img)
        for lib, bb in boites.items():
            d.ellipse(bb, outline=(255, 0, 0), width=3)
        img.save(args.controle)
        print(f"Contrôle : {args.controle}")


if __name__ == "__main__":
    main()
