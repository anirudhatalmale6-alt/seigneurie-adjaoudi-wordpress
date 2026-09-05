# -*- coding: utf-8 -*-
"""Compare le RENDU des deux versions, pas leur code source.

Le controle precedent lit du HTML. Celui-ci ouvre les deux sites dans un vrai
navigateur, a la meme largeur, et compare les images. Une feuille de style qui
ne se charge pas, une police absente ou une regle qui ne s'applique plus se
voient ici et nulle part ailleurs.

On compare la premiere fenetre de chaque page (pas la page entiere : une
capture de page longue depasse les limites de taille et ne se lit plus).
"""
import os
import sys

from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "captures")
# SEIG_WP permet de faire tourner exactement la meme comparaison contre le
# site RESTAURE depuis l'archive livree, et pas seulement contre celui de
# developpement. C'est l'artefact livre qu'il faut regarder, pas sa source.
WP = os.environ.get("SEIG_WP", "http://127.0.0.1:8880")
ST = os.environ.get("SEIG_ST", "http://127.0.0.1:8881")
SUFFIXE = os.environ.get("SEIG_SUFFIXE", "")

# (nom, chemin WordPress, chemin statique)
PAGES = [
    ("accueil-en",      "/",                      "/index.html"),
    ("la-seigneurie",   "/the-lordship/",         "/the-lordship.html"),
    ("patrimoine",      "/heritage/",             "/heritage.html"),
    ("maison",          "/house-of-adjaoudi/",    "/house-of-adjaoudi.html"),
    ("initiatives",     "/initiatives/",          "/initiatives.html"),
    ("journal",         "/journal/",              "/journal.html"),
    ("mediatheque",     "/media-library/",        "/media-library.html"),
    ("contact",         "/contact/",              "/contact.html"),
    ("cercle-prive",    "/private-circle/",       "/private-circle.html"),
    ("mentions",        "/legal/",                "/legal.html"),
    ("accueil-fr",      "/fr/",                   "/fr/index.html"),
    ("fr-la-seigneurie","/fr/la-seigneurie/",     "/fr/la-seigneurie.html"),
    ("fr-patrimoine",   "/fr/patrimoine/",        "/fr/patrimoine.html"),
    ("fr-maison",       "/fr/la-maison/",         "/fr/la-maison.html"),
    ("fr-initiatives",  "/fr/initiatives/",       "/fr/initiatives.html"),
    ("fr-journal",      "/fr/journal/",           "/fr/journal.html"),
    ("fr-mediatheque",  "/fr/mediatheque/",       "/fr/mediatheque.html"),
    ("fr-contact",      "/fr/contact/",           "/fr/contact.html"),
    ("fr-cercle",       "/fr/cercle-prive/",      "/fr/cercle-prive.html"),
    ("fr-mentions",     "/fr/mentions-legales/",  "/fr/mentions-legales.html"),
]

LARGEURS = [(1280, 720), (390, 720)]

ok = True


def v(cond, msg):
    global ok
    print(("  OK    " if cond else "  ECHEC ") + msg)
    if not cond:
        ok = False


def capture(page, url, chemin):
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(400)
    page.screenshot(path=chemin)


def ecart(a, b):
    """Proportion de pixels qui different, en pour cent."""
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    if ia.size != ib.size:
        return 100.0
    diff = ImageChops.difference(ia, ib)
    # un pixel compte comme different des qu'un canal s'ecarte de plus de 8
    boite = diff.point(lambda p: 255 if p > 8 else 0).convert("L")
    differents = sum(1 for p in boite.getdata() if p)
    return 100.0 * differents / (ia.size[0] * ia.size[1])


def main():
    os.makedirs(SORTIE, exist_ok=True)
    with sync_playwright() as p:
        nav = p.chromium.launch()
        for largeur, hauteur in LARGEURS:
            page = nav.new_page(viewport={"width": largeur, "height": hauteur})
            for nom, wp, st in PAGES:
                a = os.path.join(SORTIE, "%s-%d-wp%s.png" % (nom, largeur, SUFFIXE))
                b = os.path.join(SORTIE, "%s-%d-statique%s.png" % (nom, largeur, SUFFIXE))
                capture(page, WP + wp, a)
                capture(page, ST + st, b)
                e = ecart(a, b)
                v(e < 0.20, "%-18s %4dpx  ecart %.3f %%" % (nom, largeur, e))
            page.close()
        nav.close()
    print("\n" + ("LE RENDU EST IDENTIQUE" if ok else "DES PAGES DIFFERENT"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
