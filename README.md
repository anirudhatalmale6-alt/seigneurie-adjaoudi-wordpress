# Seigneurie Adjaoudi — version WordPress

Le site de la Seigneurie Adjaoudi, livré en WordPress, sous la forme d'une
archive `.wpress` importable par All-in-One WP Migration.

C'est le **même site** que la version statique déjà livrée : mêmes 20 pages,
même texte, même mise en page, mêmes couleurs, mêmes polices embarquées. La
seule différence est qu'il est désormais administrable.

**Fichier à installer : `seigneurie-adjaoudi-1.0.0.wpress` (529 Ko).**

L'archive elle-même n'est pas dans ce dépôt : elle contient la base du site,
donc le compte d'administration et l'empreinte de son mot de passe. Elle est
envoyée dans le fil de discussion, pas publiée. Ce dépôt contient tout le
reste — le thème, les scripts qui le fabriquent et ceux qui le vérifient.

---

## Avant d'installer — à lire, c'est la seule chose qui peut faire des dégâts

Un `.wpress` n'est pas un ajout, c'est un **remplacement complet**. À l'import,
All-in-One WP Migration **efface la base de données et tout le `wp-content`**
du site cible avant d'écrire les siens.

Il s'installe donc :

- sur un WordPress **neuf ou vide**, ou
- sur un **sous-domaine dédié** (par exemple `preprod.` quelque chose),

et **jamais** par-dessus un site qui contient déjà quoi que ce soit.

## Installation

1. Sur le WordPress cible, installer l'extension **All-in-One WP Migration**.
2. `All-in-One WP Migration` → `Import` → `Import From` → `File`, puis choisir
   `seigneurie-adjaoudi-1.0.0.wpress`.
3. Confirmer l'écrasement quand l'extension le demande.
4. À la fin, l'extension demande d'enregistrer deux fois les permaliens :
   `Réglages` → `Permaliens` → `Enregistrer`. C'est ce qui remet les adresses
   propres (`/heritage/`, `/fr/patrimoine/`…) en service.

L'adresse du site est réécrite automatiquement à l'import : rien à modifier à
la main dans la base.

## Après l'import — trois choses à faire tout de suite

1. **Changer le mot de passe.** Le compte livré est `adjaoudi`. Son mot de
   passe est envoyé séparément dans le fil de discussion. `Utilisateurs` →
   `Profil` → nouveau mot de passe.
2. **Mettre une vraie adresse d'administration.** `Réglages` → `Général`.
   L'adresse actuelle est un remplissage sans valeur ; sans adresse valable,
   aucune récupération de mot de passe n'est possible.
3. **Rendre le site visible aux moteurs quand il sera prêt.** Il est livré en
   `Réglages` → `Lecture` → *demander aux moteurs de recherche de ne pas
   indexer ce site*, **coché**. C'est volontaire : c'est une préproduction
   tant que le domaine, les mentions légales et la devise ne sont pas
   tranchés. Décocher le jour du lancement, pas avant.

## Ce qui est modifiable, et où

| Ce que tu veux changer | Où |
|---|---|
| Le texte d'une page | `Pages` → la page → l'éditeur. Chaque section est un bloc. |
| L'ordre ou le libellé du menu | `Apparence` → `Menus`. Quatre menus : principal EN, principal FR, pied EN, pied FR. |
| Le blason, le sceau, le halo | `wp-content/themes/seigneurie/assets/` — ce sont des SVG. |
| Les couleurs, les espacements | `wp-content/themes/seigneurie/assets/site.css` |
| Le bandeau légal du pied de page | `footer.php` du thème. Il est là et pas dans une page **exprès** : c'est la clause que ton propre cahier des charges impose, elle ne doit pas se perdre dans une modification de contenu. |

Les 20 pages sont réparties ainsi : 10 en anglais à la racine, 10 en français
sous `/fr/`. Chaque page connaît sa jumelle dans l'autre langue — c'est ce qui
fait que le sélecteur EN / FR mène à la **même** page traduite et pas à
l'accueil.

## Ce que le thème ne fait pas, volontairement

- **Aucune requête sortante.** Pas de Google Fonts, pas de CDN, pas de mesure
  d'audience. Les polices (Cormorant Garamond, Inter) sont dans le thème.
  C'était déjà la règle sur la version statique, elle est tenue ici et
  vérifiée page par page.
- **Aucun contenu inventé.** Rien n'a été ajouté ni retiré au texte livré : ni
  date, ni nom, ni ancêtre, ni source. Les mentions « En attente
  d'autorisation » sont toujours là où elles étaient.
- **Pas de commentaires**, désactivés sur tout le site.

## Comment cette version a été vérifiée

Le site statique avait déjà passé sa propre suite de contrôles. La question
n'était donc pas « est-ce que le site est bon » mais « est-ce que WordPress
rend **exactement** la même chose ». Trois contrôles, dans cet ordre :

1. **`verifie.py` — 145 contrôles.** Il compare, page par page, le HTML rendu
   par WordPress au HTML de la version statique, après avoir ramené les deux à
   une forme canonique (seules les URL s'écrivent différemment). Le contenu de
   `<main>`, le titre du document, la méta description, le menu principal, le
   pied de page, l'absence de tout appel sortant, et le fait que les 21
   adresses internes du site répondent toutes en 200.

2. **`visuel.py` — 40 comparaisons d'images.** Les deux sites sont ouverts
   dans un vrai Chromium, à 1280 px et à 390 px, et les captures sont
   comparées pixel à pixel. Écart mesuré : **0,000 % sur les 40**. Le banc a
   été éprouvé par mutation — une seule règle de couleur changée dans le thème
   fait monter l'écart à 8,86 %, donc un contrôle vert veut dire quelque
   chose.

3. **`restaure.py` — la restauration pour de vrai.** Les deux contrôles
   ci-dessus tournent sur le WordPress de développement, qui est en SQLite à
   l'adresse où l'archive a été fabriquée. Deux choses n'y sont donc jamais
   éprouvées : est-ce que le `database.sql` est du vrai MySQL, et est-ce que le
   site survit au changement d'adresse. Ce script refait donc ce que fait
   All-in-One WP Migration — il ouvre l'archive livrée, remet `wp-content` en
   place, remplace l'ancienne adresse par une nouvelle, importe dans une base
   **MySQL 8 vierge** et sert le résultat. **Les 145 contrôles et les 40
   comparaisons d'images ont ensuite été relancés contre ce site restauré**, et
   ce sont ces résultats-là qui comptent.

Trois défauts réels ont été trouvés par cette comparaison, et aucun ne se
voyait à l'œil nu :

- la colonne « Langues » du pied de page menait à l'accueil des deux langues
  au lieu de mener à la page courante et à sa traduction. Le pied avait été
  extrait de la page d'accueil, où les deux se confondent ;
- WordPress réécrivait les `<img>` du contenu (`fetchpriority`, `decoding`,
  `loading="lazy"`), donc le balisage livré n'était plus celui qui avait été
  mesuré ;
- WordPress supprimait silencieusement les `<form>` des maquettes de
  formulaire — les pages Contact et Cercle privé perdaient leurs champs sans
  le moindre message d'erreur.

## Les fichiers de ce dépôt

| | |
|---|---|
| `theme/` | le thème, tel qu'il est dans l'archive |
| `build_theme.py` | fabrique le thème **à partir du site statique** — l'habillage est extrait des pages livrées, jamais retapé |
| `seed.php` | crée les 20 pages et les 4 menus dans WordPress. Idempotent : on peut le relancer |
| `verifie.py` | les 145 contrôles |
| `visuel.py` | les 40 comparaisons d'images |
| `restaure.py` | la restauration en MySQL à une autre adresse |
| `apercus/` | les captures |

Rien ici n'est écrit à la main dans le `.docx` ou le HTML final : le thème est
**généré** depuis le site statique, et les contrôles relisent le résultat
produit, pas les sources qui l'ont produit.
