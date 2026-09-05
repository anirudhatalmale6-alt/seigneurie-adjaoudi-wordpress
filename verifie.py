# -*- coding: utf-8 -*-
"""Compare la version WordPress a la version statique DEJA VALIDEE.

Le site statique a passe sa propre suite de controles. La question ici n'est
donc pas « est-ce que le site est bon » mais « est-ce que WordPress rend
exactement la meme chose ». On compare donc du rendu contre du rendu, page par
page, apres avoir ramene les deux a une forme canonique : les URL n'ont pas la
meme ecriture des deux cotes, tout le reste doit etre identique au caractere.

Ce que le script verifie :
  1. les 20 pages repondent en 200 ;
  2. le contenu de <main> est identique, une fois les URL canonisees ;
  3. le titre du document et la meta description sont identiques ;
  4. le menu principal et le pied listent les memes destinations ;
  5. AUCUNE ressource n'est chargee depuis un autre domaine ;
  6. tous les liens internes de toutes les pages repondent en 200 ;
  7. l'index de recherche pointe sur des URL qui existent.
"""

import json
import os
import re
import sys
import urllib.request

import build_theme as B

# SEIG_WP : la meme suite tourne contre le site de developpement ET contre le
# site restaure depuis l'archive livree. C'est le second qui compte.
BASE = os.environ.get("SEIG_WP", "http://127.0.0.1:8880")
ICI = os.path.dirname(os.path.abspath(__file__))
STATIQUE = B.STATIQUE

ok = True


def v(cond, msg):
    global ok
    print(("  OK    " if cond else "  ECHEC ") + msg)
    if not cond:
        ok = False


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.status, r.read().decode("utf-8")


def code(url):
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:                                   # noqa: BLE001
        return str(e)


# --------------------------------------------------------------------------
# Forme canonique : une adresse, ecrite de la meme facon des deux cotes
# --------------------------------------------------------------------------
INVERSE = {}
for _fichier, _url in B.CHEMIN.items():
    INVERSE[_url] = "PAGE:" + _fichier


def canonise_wp(html):
    html = html.replace(BASE + "/wp-content/themes/seigneurie/assets/", "ASSET:")
    html = re.sub(r"(ASSET:[\w./-]+)\?ver=[\w.]+", r"\1", html)

    def page(m):
        chemin = m.group(0)[len(BASE):]
        return INVERSE.get(chemin, "INCONNU:" + chemin)

    html = re.sub(re.escape(BASE) + r"/[\w/-]*/?", page, html)
    return html


def canonise_statique(html, depuis_fr):
    def ref(m):
        attr, valeur = m.group(1), m.group(2)
        if valeur.startswith("#"):
            return m.group(0)
        chemin, _, ancre = valeur.partition("#")
        ancre = ("#" + ancre) if ancre else ""
        chemin = chemin.split("?")[0]
        if "assets/" in chemin:
            return '%s="ASSET:%s%s"' % (attr, chemin.split("assets/", 1)[1], ancre)
        cle = chemin
        if depuis_fr:
            cle = chemin[3:] if chemin.startswith("../") else "fr/" + chemin
        return '%s="PAGE:%s%s"' % (attr, cle, ancre)

    return re.sub(r'\b(href|src)="([^"]+)"', ref, html)


def entre(html, debut, fin):
    i = html.index(debut)
    i = html.index(">", i) + 1
    return html[i:html.index(fin, i)]


def lignes(bloc):
    return [l.strip() for l in bloc.strip().split("\n") if l.strip()]


def liens_de(bloc):
    return re.findall(r'href="([^"]+)"', bloc)


# --------------------------------------------------------------------------
print("\n--- les 20 pages ---")
pages = json.load(open(os.path.join(ICI, "pages.json"), encoding="utf-8"))["pages"]
rendus = {}

for p in pages:
    url = BASE + B.CHEMIN[p["fichier"]]
    try:
        statut, html = get(url)
    except Exception as e:                                   # noqa: BLE001
        v(False, "%s : %s" % (p["cle"], e))
        continue
    rendus[p["cle"]] = html
    v(statut == 200, "%-18s %s -> %s" % (p["cle"], B.CHEMIN[p["fichier"]], statut))

print("\n--- le contenu de <main>, compare caractere par caractere ---")
for p in pages:
    if p["cle"] not in rendus:
        continue
    wp = canonise_wp(entre(rendus[p["cle"]], "<main", "</main>"))
    with open(os.path.join(STATIQUE, p["fichier"]), encoding="utf-8") as f:
        st = f.read()
    stat = canonise_statique(entre(st, "<main", "</main>"),
                             p["fichier"].startswith("fr/"))
    a, b = lignes(wp), lignes(stat)
    if a == b:
        v(True, "%-18s %d elements identiques" % (p["cle"], len(a)))
    else:
        v(False, "%-18s %d elements cote WordPress, %d cote statique"
                 % (p["cle"], len(a), len(b)))
        for i in range(max(len(a), len(b))):
            x = a[i] if i < len(a) else "(absent)"
            y = b[i] if i < len(b) else "(absent)"
            if x != y:
                print("        WP  : " + x[:160])
                print("        HTML: " + y[:160])
                break

print("\n--- titre et description ---")
for p in pages:
    if p["cle"] not in rendus:
        continue
    html = rendus[p["cle"]]
    titre = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)"', html)
    desc = desc.group(1) if desc else ""
    v(titre == p["titre_doc"],
      "%-18s titre %r" % (p["cle"], titre if titre == p["titre_doc"]
                          else titre + " != " + p["titre_doc"]))
    v(desc == p["description"], "%-18s description identique" % p["cle"])

print("\n--- menus ---")
for p in pages:
    if p["cle"] not in rendus:
        continue
    html = rendus[p["cle"]]
    with open(os.path.join(STATIQUE, p["fichier"]), encoding="utf-8") as f:
        st = canonise_statique(f.read(), p["fichier"].startswith("fr/"))
    wp = canonise_wp(html)
    nav_wp = liens_de(entre(wp, '<nav class="nav"', "</nav>"))
    nav_st = liens_de(entre(st, '<nav class="nav"', "</nav>"))
    v(nav_wp == nav_st, "%-18s menu principal : %d entrees, memes destinations"
      % (p["cle"], len(nav_wp)))
    pied_wp = liens_de(entre(wp, '<footer class="pied"', "</footer>"))
    pied_st = liens_de(entre(st, '<footer class="pied"', "</footer>"))
    v(pied_wp == pied_st, "%-18s pied de page : %d liens, memes destinations"
      % (p["cle"], len(pied_wp)))

print("\n--- aucune ressource exterieure ---")
# la regle du site : ni CDN, ni police distante, ni mesure d'audience.
for cle, html in rendus.items():
    externes = set()
    for m in re.findall(r'\b(?:href|src)="(https?://[^"]+)"', html):
        if not m.startswith(BASE):
            externes.add(m)
    # les liens rel=alternate hreflang et canonical restent internes
    v(not externes, "%-18s %s" % (cle, "aucun appel sortant" if not externes
                                  else "SORTIES : " + ", ".join(sorted(externes)[:3])))

print("\n--- tous les liens internes repondent ---")
vus = {}
for cle, html in rendus.items():
    for lien in re.findall(r'href="(%s[^"#]*)"' % re.escape(BASE), html):
        vus.setdefault(lien, set()).add(cle)
casses = []
for lien in sorted(vus):
    c = code(lien)
    if c != 200:
        casses.append((lien, c, sorted(vus[lien])[:3]))
v(not casses, "%d adresses distinctes, toutes en 200%s"
  % (len(vus), "" if not casses else " -- CASSEES : " + str(casses[:3])))

print("\n--- index de recherche ---")
for langue in ("en", "fr"):
    chemin = os.path.join(B.THEME, "assets", "index-%s.js" % langue)
    with open(chemin, encoding="utf-8") as f:
        js = f.read()
    donnees = json.loads(js[js.index("["):].rstrip().rstrip(";\n"))
    mauvais = [e["u"] for e in donnees
               if e["u"].split("#")[0] not in INVERSE]
    v(not mauvais, "index %s : %d entrees, toutes vers une page du site%s"
      % (langue, len(donnees), "" if not mauvais else " -- " + str(mauvais[:3])))

print("\n--- pages 404 et administration ---")
v(code(BASE + "/cette-page-n-existe-pas/") == 404, "une adresse inconnue rend un 404")
v(code(BASE + "/wp-login.php") == 200, "la page de connexion repond")

print("\n" + ("TOUT EST VERT" if ok else "DES CONTROLES ONT ECHOUE"))
sys.exit(0 if ok else 1)
