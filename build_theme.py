# -*- coding: utf-8 -*-
"""Fabrique le theme WordPress « seigneurie » A PARTIR du site statique livre.

Principe : on n'ecrit pas une deuxieme fois le site. On EXTRAIT l'habillage
(barre utilitaire, en-tete, pied, boite de recherche) des pages statiques
elles-memes et on le transforme en gabarits PHP. Retaper les textes serait le
moyen le plus sur d'introduire une difference invisible entre la version
statique deja validee et la version WordPress.

Ce que le script produit :
  wp/wp-content/themes/seigneurie/   le theme complet
  seigwp/pages.json                  la liste des pages a creer (lue par seed.php)

Ce qu'il ne fait pas : creer les pages. C'est le travail de seed.php, qui parle
a WordPress et non au disque.
"""
import json
import os
import re
import shutil

ICI = os.path.dirname(os.path.abspath(__file__))
STATIQUE = os.path.join(os.path.dirname(ICI), "seigneurie")
THEME = os.path.join(ICI, "wp", "wp-content", "themes", "seigneurie")

# --------------------------------------------------------------------------
# La carte des pages. Elle est ECRITE ICI et nulle part ailleurs : le
# reecrivain de liens, le semeur de pages et les menus la lisent tous les
# trois. Une seule source, donc pas de derive possible entre les trois.
# (fichier, langue, slug, parent, titre de menu, titre de page)
# --------------------------------------------------------------------------
PAGES = [
    # anglais -- la racine
    ("index.html",            "en", "home",              None, "Home",              "Adjaoudi Lordship"),
    ("the-lordship.html",     "en", "the-lordship",      None, "The Lordship",      "The Lordship"),
    ("heritage.html",         "en", "heritage",          None, "Heritage",          "Heritage"),
    ("house-of-adjaoudi.html","en", "house-of-adjaoudi", None, "House of Adjaoudi", "House of Adjaoudi"),
    ("initiatives.html",      "en", "initiatives",       None, "Initiatives",       "Initiatives"),
    ("journal.html",          "en", "journal",           None, "Journal",           "Journal"),
    ("media-library.html",    "en", "media-library",     None, "Media Library",     "Media Library"),
    ("contact.html",          "en", "contact",           None, "Contact",           "Contact"),
    ("private-circle.html",   "en", "private-circle",    None, "Private Circle",    "Private Circle"),
    ("legal.html",            "en", "legal",             None, "Legal & privacy",   "Legal & privacy"),
    # francais -- sous /fr/
    ("fr/index.html",           "fr", "fr",               None, "Accueil",           "Seigneurie Adjaoudi"),
    ("fr/la-seigneurie.html",   "fr", "la-seigneurie",    "fr", "La Seigneurie",     "La Seigneurie"),
    ("fr/patrimoine.html",      "fr", "patrimoine",       "fr", "Patrimoine",        "Patrimoine"),
    ("fr/la-maison.html",       "fr", "la-maison",        "fr", "La Maison Adjaoudi","La Maison Adjaoudi"),
    ("fr/initiatives.html",     "fr", "initiatives-fr",   "fr", "Initiatives",       "Initiatives"),
    ("fr/journal.html",         "fr", "journal-fr",       "fr", "Journal",           "Journal"),
    ("fr/mediatheque.html",     "fr", "mediatheque",      "fr", "Médiathèque",       "Médiathèque"),
    ("fr/contact.html",         "fr", "contact-fr",       "fr", "Contact",           "Contact"),
    ("fr/cercle-prive.html",    "fr", "cercle-prive",     "fr", "Cercle privé",      "Cercle privé"),
    ("fr/mentions-legales.html","fr", "mentions-legales", "fr", "Mentions légales",  "Mentions légales"),
]

# les pages qui vont dans le menu principal, dans l'ordre du site statique
MENU_PRINCIPAL = {
    "en": ["the-lordship", "heritage", "house-of-adjaoudi", "initiatives",
           "journal", "media-library", "contact"],
    "fr": ["la-seigneurie", "patrimoine", "la-maison", "initiatives-fr",
           "journal-fr", "mediatheque", "contact-fr"],
}
MENU_PIED = {
    "en": MENU_PRINCIPAL["en"] + ["private-circle", "legal"],
    "fr": MENU_PRINCIPAL["fr"] + ["cercle-prive", "mentions-legales"],
}
# la page equivalente dans l'autre langue (le selecteur de langue)
JUMELLES = [
    ("home", "fr"), ("the-lordship", "la-seigneurie"), ("heritage", "patrimoine"),
    ("house-of-adjaoudi", "la-maison"), ("initiatives", "initiatives-fr"),
    ("journal", "journal-fr"), ("media-library", "mediatheque"),
    ("contact", "contact-fr"), ("private-circle", "cercle-prive"),
    ("legal", "mentions-legales"),
]

# --------------------------------------------------------------------------
# Reecriture des liens : chemin statique -> chemin WordPress
# --------------------------------------------------------------------------
CHEMIN = {}
for fichier, langue, slug, parent, _m, _t in PAGES:
    if slug == "home":
        url = "/"
    elif slug == "fr":
        url = "/fr/"
    elif parent:
        url = "/%s/%s/" % (parent, slug.replace("-fr", "") if slug.endswith("-fr") else slug)
    else:
        url = "/%s/" % slug
    CHEMIN[fichier] = url

# les slugs des pages filles ne doivent pas porter le suffixe technique -fr
# dans l'URL : WordPress les distingue par leur parent.
SLUG_URL = {
    "initiatives-fr": "initiatives", "journal-fr": "journal",
    "contact-fr": "contact",
}


def url_de(fichier):
    return CHEMIN[fichier]


def reecrit(html, depuis_fr, mode="php"):
    """Remplace les liens et les ressources du site statique par ceux du theme.

    depuis_fr : la page qui contient ce html est-elle dans /fr/ ? Les chemins
    relatifs n'ont pas la meme base dans les deux cas.

    mode « php »     : pour les gabarits du theme -> appels PHP (home_url,
                       get_theme_file_uri). Le site marche alors quel que soit
                       le domaine ET quel que soit le sous-dossier.
    mode « contenu » : pour le contenu des pages, qui est stocke en base. On y
                       ecrit des URL ABSOLUES sur le site de developpement,
                       parce que c'est ce que All-in-One WP Migration sait
                       reecrire a l'import. Un chemin commencant par / ne
                       serait PAS reecrit et casserait une installation dans
                       un sous-dossier.
    """
    def cible(ref):
        # ancre seule
        if ref.startswith("#"):
            return ref
        chemin, _, ancre = ref.partition("#")
        ancre = ("#" + ancre) if ancre else ""
        chemin = chemin.split("?")[0]
        if chemin.startswith("assets/") or chemin.startswith("../assets/"):
            nom = chemin.split("assets/", 1)[1]
            if mode == "contenu":
                return "%%URL%%/wp-content/themes/seigneurie/assets/" + nom + ancre
            return "<?php echo esc_url( get_theme_file_uri( 'assets/%s' ) ); ?>%s" % (nom, ancre)
        # normalise le chemin relatif en chemin depuis la racine du site statique
        if depuis_fr:
            if chemin.startswith("../"):
                cle = chemin[3:]
            else:
                cle = "fr/" + chemin
        else:
            cle = chemin
        if cle in CHEMIN:
            if mode == "contenu":
                return "%%URL%%" + CHEMIN[cle] + ancre
            return ("<?php echo esc_url( home_url( '%s' ) ); ?>%s"
                    % (CHEMIN[cle], ancre))
        raise KeyError("lien non cartographie : %r (depuis_fr=%s)" % (ref, depuis_fr))

    def sub(m):
        attr, ref = m.group(1), m.group(2)
        return '%s="%s"' % (attr, cible(ref))

    return re.sub(r'\b(href|src)="([^"]+)"', sub, html)


def lire(fichier):
    with open(os.path.join(STATIQUE, fichier), encoding="utf-8") as f:
        return f.read()


def morceaux(html):
    """Decoupe une page statique en tete / habillage haut / contenu / bas."""
    corps = html[html.index("<body>") + len("<body>"):]
    haut = corps[:corps.index("<main")]
    i = corps.index(">", corps.index("<main")) + 1
    contenu = corps[i:corps.index("</main>")]
    bas = corps[corps.index("</main>") + len("</main>"):]
    bas = bas[:bas.index("</body>")]
    return haut, contenu, bas


def php_haut(langue):
    """L'habillage du haut, extrait de la page d'accueil de la langue."""
    src = "index.html" if langue == "en" else "fr/index.html"
    haut, _, _ = morceaux(lire(src))
    haut = reecrit(haut, langue == "fr")

    # le menu principal devient un menu WordPress, rendu a l'identique
    haut, n1 = re.subn(
        r'<nav class="nav" aria-label="[^"]*">.*?</nav>',
        "<?php seig_menu( 'principal' ); ?>",
        haut, flags=re.S)

    # le selecteur de langue pointe sur la page jumelle de la page courante
    haut, n2 = re.subn(
        r'<div class="langues">.*?</div>',
        "<?php seig_langues(); ?>",
        haut, flags=re.S)

    if (n1, n2) != (1, 1):
        raise AssertionError("en-tete %s : nav=%d langues=%d" % (langue, n1, n2))
    return haut


def php_bas(langue):
    src = "index.html" if langue == "en" else "fr/index.html"
    _, _, bas = morceaux(lire(src))
    bas = reecrit(bas, langue == "fr")

    # la colonne « Sections » du pied devient elle aussi un menu WordPress
    bas, n1 = re.subn(
        r'(<h4>(?:Sections)</h4>)<ul>.*?</ul>',
        r"\1<?php seig_menu( 'pied' ); ?>",
        bas, flags=re.S)
    # la colonne « Langues » mene a la page courante dans chaque langue
    bas, n2 = re.subn(
        r'(<h4>(?:Languages|Langues)</h4>)<ul>.*?</ul>',
        r"\1<?php seig_langues_pied(); ?>",
        bas, flags=re.S)
    # une substitution qui ne trouve rien laisserait le balisage fige sans
    # rien signaler : c'est exactement le defaut qu'on veut voir echouer ici.
    if (n1, n2) != (1, 1):
        raise AssertionError("pied %s : sections=%d langues=%d" % (langue, n1, n2))

    # les deux scripts sont charges par WordPress (wp_enqueue_script)
    bas = re.sub(r'<script src="[^"]*"></script>\s*', "", bas)
    return bas


def contenu_page(fichier):
    _, contenu, _ = morceaux(lire(fichier))
    return reecrit(contenu, fichier.startswith("fr/"), mode="contenu").strip()


def tete_de(fichier):
    html = lire(fichier)
    tete = html[:html.index("</head>")]
    titre = re.search(r"<title>(.*?)</title>", tete, re.S).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)"', tete)
    return titre, (desc.group(1) if desc else "")


# --------------------------------------------------------------------------
# Ecriture du theme
# --------------------------------------------------------------------------
STYLE_CSS = """/*
Theme Name: Seigneurie Adjaoudi
Description: Theme du site de la Seigneurie Adjaoudi. Bilingue anglais / francais. Aucune ressource exterieure : polices, images et scripts sont servis par le theme lui-meme.
Version: 1.0.0
Requires at least: 6.0
Tested up to: 7.1
Requires PHP: 7.4
Text Domain: seigneurie
*/

/* La feuille de style reelle est assets/site.css, mise en file d'attente par
   functions.php. Ce fichier n'existe que parce que WordPress exige un
   style.css portant l'en-tete du theme. */
"""

FUNCTIONS_PHP = r"""<?php
/**
 * Seigneurie Adjaoudi — fonctions du theme.
 *
 * Regle de ce site, tenue ici comme dans la version statique : AUCUNE
 * ressource n'est chargee depuis un serveur tiers. Les polices, les images et
 * le script sont dans le theme. On retire donc aussi ce que WordPress ajoute
 * de lui-meme et qui sortirait du domaine ou alourdirait la page sans servir.
 */

if ( ! defined( 'ABSPATH' ) ) { exit; }

define( 'SEIG_VERSION', '1.0.0' );

/* ------------------------------------------------------------------ socle */

function seig_setup() {
	add_theme_support( 'title-tag' );
	add_theme_support( 'html5', array( 'search-form', 'style', 'script' ) );
	register_nav_menus( array(
		'principal-en' => 'Menu principal (English)',
		'principal-fr' => 'Menu principal (Français)',
		'pied-en'      => 'Pied de page (English)',
		'pied-fr'      => 'Pied de page (Français)',
	) );
}
add_action( 'after_setup_theme', 'seig_setup' );

function seig_assets() {
	wp_enqueue_style( 'seigneurie', get_theme_file_uri( 'assets/site.css' ), array(), SEIG_VERSION );
	// L'index de recherche depend de la langue de la page affichee.
	$idx = ( 'fr' === seig_langue() ) ? 'assets/index-fr.js' : 'assets/index-en.js';
	wp_enqueue_script( 'seigneurie-index', get_theme_file_uri( $idx ), array(), SEIG_VERSION, true );
	wp_enqueue_script( 'seigneurie', get_theme_file_uri( 'assets/site.js' ), array( 'seigneurie-index' ), SEIG_VERSION, true );
}
add_action( 'wp_enqueue_scripts', 'seig_assets' );

/* Rien de tout cela n'existait dans la version statique : on ne l'ajoute pas. */
remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
remove_action( 'wp_print_styles', 'print_emoji_styles' );
remove_action( 'wp_head', 'wp_generator' );
remove_action( 'wp_head', 'wlwmanifest_link' );
remove_action( 'wp_head', 'rsd_link' );
remove_action( 'wp_head', 'wp_shortlink_wp_head' );
remove_action( 'wp_head', 'wp_oembed_add_discovery_links' );
remove_action( 'wp_head', 'wp_oembed_add_host_js' );
remove_action( 'wp_head', 'rest_output_link_wp_head' );
remove_action( 'wp_head', 'feed_links', 2 );
remove_action( 'wp_head', 'feed_links_extra', 3 );
remove_action( 'wp_head', 'wp_resource_hints', 2 );
remove_action( 'wp_enqueue_scripts', 'wp_enqueue_global_styles' );
remove_action( 'wp_footer', 'wp_enqueue_global_styles', 1 );
remove_action( 'wp_body_open', 'wp_global_styles_render_svg_filters' );
add_filter( 'emoji_svg_url', '__return_false' );
add_filter( 'the_generator', '__return_empty_string' );
add_filter( 'wp_img_tag_add_auto_sizes', '__return_false' );
// La feuille de style des blocs n'est pas utilisee : le contenu est du HTML
// deja mis en forme, et la feuille du site le couvre entierement.
add_action( 'wp_enqueue_scripts', function () {
	wp_dequeue_style( 'wp-block-library' );
	wp_dequeue_style( 'wp-block-library-theme' );
	wp_dequeue_style( 'global-styles' );
	wp_dequeue_style( 'classic-theme-styles' );
	wp_dequeue_style( 'wp-img-auto-sizes-contain' );
}, 100 );

/**
 * Le contenu des pages est du HTML deja mis en forme, decoupe en blocs
 * « HTML personnalise ». wpautop ajouterait des <p> au milieu de ce balisage :
 * on le retire sur les pages du site, et sur elles seulement.
 */
add_action( 'wp', function () {
	if ( is_singular() && get_post_meta( get_queried_object_id(), '_seig_lang', true ) ) {
		remove_filter( 'the_content', 'wpautop' );
		remove_filter( 'the_content', 'shortcode_unautop' );
		// wp_filter_content_tags reecrit les <img> (fetchpriority, decoding,
		// loading="lazy"). La version statique a ete mesuree SANS ces
		// attributs ; on ne laisse pas WordPress modifier un balisage deja
		// verifie, sinon les deux versions divergent sans qu'on l'ait decide.
		// La priorite fait partie de l'identite du filtre : sans le 12,
		// remove_filter cherche a la priorite 10 et ne retire RIEN, en
		// silence.
		remove_filter( 'the_content', 'wp_filter_content_tags', 12 );
	}
} );

/* ----------------------------------------------------------------- langue */

/**
 * La langue de la page affichee. Elle est portee par la page elle-meme
 * (metadonnee _seig_lang), pas devinee a partir de l'URL : une URL peut
 * changer, la metadonnee non.
 */
function seig_langue() {
	$id = get_queried_object_id();
	if ( $id ) {
		$l = get_post_meta( $id, '_seig_lang', true );
		if ( 'fr' === $l || 'en' === $l ) { return $l; }
	}
	return 'en';
}

function seig_accueil( $langue = null ) {
	$langue = $langue ? $langue : seig_langue();
	if ( 'fr' === $langue ) {
		$p = get_page_by_path( 'fr' );
		return $p ? get_permalink( $p ) : home_url( '/fr/' );
	}
	return home_url( '/' );
}

/** La page equivalente dans l'autre langue, ou l'accueil de cette langue. */
function seig_jumelle() {
	$id = get_queried_object_id();
	$alt = $id ? (int) get_post_meta( $id, '_seig_alt', true ) : 0;
	if ( $alt && 'publish' === get_post_status( $alt ) ) {
		return get_permalink( $alt );
	}
	return seig_accueil( 'fr' === seig_langue() ? 'en' : 'fr' );
}

/** Le selecteur EN / FR, rendu exactement comme dans la version statique. */
function seig_langues() {
	$langue = seig_langue();
	$ici    = get_permalink( get_queried_object_id() );
	$autre  = seig_jumelle();
	$en = ( 'en' === $langue ) ? $ici : $autre;
	$fr = ( 'fr' === $langue ) ? $ici : $autre;
	echo '<div class="langues">';
	printf( '<a href="%s" hreflang="en" lang="en"%s>EN</a>',
		esc_url( $en ), ( 'en' === $langue ) ? ' aria-current="true"' : '' );
	echo '<span>/</span>';
	printf( '<a href="%s" hreflang="fr" lang="fr"%s>FR</a>',
		esc_url( $fr ), ( 'fr' === $langue ) ? ' aria-current="true"' : '' );
	echo '</div>';
}

/**
 * La colonne « Langues » du pied de page.
 *
 * Elle ne mene PAS a l'accueil des deux langues : dans la version statique,
 * elle mene a la page courante et a sa jumelle, exactement comme le selecteur
 * du haut. C'est la comparaison page par page avec la version statique qui a
 * releve la difference — le pied avait ete extrait de la page d'accueil, ou
 * les deux se confondent.
 */
function seig_langues_pied() {
	$langue = seig_langue();
	$ici    = get_permalink( get_queried_object_id() );
	$autre  = seig_jumelle();
	$en = ( 'en' === $langue ) ? $ici : $autre;
	$fr = ( 'fr' === $langue ) ? $ici : $autre;
	echo '<ul>';
	printf( '<li><a href="%s" hreflang="en">English</a></li>', esc_url( $en ) );
	printf( '<li><a href="%s" hreflang="fr">Français</a></li>', esc_url( $fr ) );
	echo '</ul>';
}

/* ------------------------------------------------------------------ menus */

/**
 * Rend un menu WordPress avec le balisage du site statique.
 *
 * Le menu principal est une suite de <a> nus dans un <nav> ; le pied est une
 * liste. Le marqueur de page courante (aria-current) est pose ici, pas par
 * les classes de WordPress : la feuille de style du site ne connait que lui.
 */
class Seig_Walker extends Walker_Nav_Menu {
	public $liste = false;
	public function start_lvl( &$sortie, $profondeur = 0, $args = null ) {}
	public function end_lvl( &$sortie, $profondeur = 0, $args = null ) {}
	public function start_el( &$sortie, $element, $profondeur = 0, $args = null, $id = 0 ) {
		$courant = ! empty( $element->current ) || ! empty( $element->current_item_ancestor );
		$a = sprintf( '<a href="%s"%s>%s</a>',
			esc_url( $element->url ),
			$courant ? ' aria-current="page"' : '',
			esc_html( $element->title ) );
		$sortie .= $this->liste ? '<li>' . $a . '</li>' : $a;
	}
	public function end_el( &$sortie, $element, $profondeur = 0, $args = null ) {}
}

function seig_menu( $ou ) {
	$emplacement = $ou . '-' . seig_langue();
	if ( ! has_nav_menu( $emplacement ) ) { return; }
	$walker = new Seig_Walker();
	$walker->liste = ( 'pied' === $ou );
	wp_nav_menu( array(
		'theme_location' => $emplacement,
		'container'      => 'pied' === $ou ? false : 'nav',
		'container_class'=> 'nav',
		'container_aria_label' => ( 'fr' === seig_langue() ) ? 'Principal' : 'Main',
		'items_wrap'     => 'pied' === $ou ? '<ul>%3$s</ul>' : '%3$s',
		'depth'          => 1,
		'walker'         => $walker,
		'fallback_cb'    => false,
	) );
}

/* --------------------------------------------------------------- en-tete */

/**
 * Le titre du document est celui de la version statique, mot pour mot.
 * WordPress fabriquerait « Page – Nom du site » avec son propre separateur et
 * le nom du site en anglais sur les pages francaises.
 */
function seig_titre( $titre ) {
	$id = get_queried_object_id();
	if ( $id ) {
		$t = get_post_meta( $id, '_seig_title', true );
		if ( $t ) { return $t; }
	}
	return $titre;
}
add_filter( 'pre_get_document_title', 'seig_titre' );

function seig_tete() {
	$id = get_queried_object_id();
	$desc = $id ? get_post_meta( $id, '_seig_desc', true ) : '';
	if ( $desc ) {
		printf( '<meta name="description" content="%s">' . "\n", esc_attr( $desc ) );
	}
	printf( '<link rel="icon" href="%s" type="image/svg+xml">' . "\n",
		esc_url( get_theme_file_uri( 'assets/favicon.svg' ) ) );
	// hreflang : la page et sa jumelle, dans les deux sens.
	$langue = seig_langue();
	$ici    = get_permalink( $id );
	$autre  = seig_jumelle();
	if ( $ici ) {
		printf( '<link rel="alternate" hreflang="%s" href="%s">' . "\n",
			esc_attr( $langue ), esc_url( $ici ) );
		printf( '<link rel="alternate" hreflang="%s" href="%s">' . "\n",
			esc_attr( 'fr' === $langue ? 'en' : 'fr' ), esc_url( $autre ) );
	}
	// La classe js est posee tout de suite : la feuille de style s'en sert
	// pour ne replier le menu que si le script pourra le rouvrir.
	echo '<script>document.documentElement.className+=" js";</script>' . "\n";
}
add_action( 'wp_head', 'seig_tete' );
"""

HEADER_PHP_MODELE = """<?php
/**
 * En-tete du site. L'habillage est celui de la version statique, extrait
 * d'elle et non retape : barre utilitaire, selecteur de langue, en-tete,
 * menu principal.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
$seig_langue = seig_langue();
?><!doctype html>
<html lang="<?php echo esc_attr( $seig_langue ); ?>">
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php if ( 'fr' === $seig_langue ) : ?>
%FR%
<?php else : ?>
%EN%
<?php endif; ?>
"""

FOOTER_PHP_MODELE = """<?php
/**
 * Pied de page. Meme principe que l'en-tete : le balisage vient de la version
 * statique. La colonne « Sections » est un menu WordPress, le reste est du
 * texte de charte que l'on ne modifie pas a la legere — en particulier la
 * declaration, qui est la clause que le document du client impose.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
$seig_langue = seig_langue();
?>
<?php if ( 'fr' === $seig_langue ) : ?>
%FR%
<?php else : ?>
%EN%
<?php endif; ?>
<?php wp_footer(); ?>
</body>
</html>
"""

PAGE_PHP = """<?php
/**
 * Une page. Le contenu editable est ce qu'il y a entre <main> et </main> dans
 * la version statique : tout ce que le client voudra changer se change dans
 * l'editeur, l'habillage reste au theme.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();
?>
<main id="contenu">
<?php
while ( have_posts() ) {
	the_post();
	the_content();
}
?>
</main>
<?php
get_footer();
"""

INDEX_PHP = """<?php
/**
 * Gabarit de repli. Le site n'a que des pages ; ce fichier existe parce que
 * WordPress exige un index.php, et il se comporte comme page.php.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();
?>
<main id="contenu">
<?php
if ( have_posts() ) {
	while ( have_posts() ) {
		the_post();
		echo '<section class="papier"><div class="wrap">';
		echo '<h1>' . esc_html( get_the_title() ) . '</h1><hr class="filet">';
		the_content();
		echo '</div></section>';
	}
}
?>
</main>
<?php
get_footer();
"""

QUATRECENTQUATRE_PHP = """<?php
/**
 * Page introuvable. Elle ne promet rien et renvoie au menu, dans la langue de
 * l'accueil demande.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
get_header();
$fr = ( 0 === strpos( trim( $_SERVER['REQUEST_URI'], '/' ), 'fr/' ) );
?>
<main id="contenu">
<section class="papier"><div class="wrap">
<h1><?php echo $fr ? 'Page introuvable' : 'Page not found'; ?></h1>
<hr class="filet">
<p><?php echo $fr
	? 'Cette adresse ne correspond a aucune page du site. Le menu ci-dessus mene a toutes les sections.'
	: 'This address matches no page on this site. Every section is reachable from the menu above.'; ?></p>
</div></section>
</main>
<?php
get_footer();
"""


def ecrire(chemin, texte):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte)


def main():
    if os.path.isdir(THEME):
        shutil.rmtree(THEME)
    os.makedirs(THEME)

    # 1. les ressources, copiees fichier par fichier (jamais un cp -r d'un
    #    dossier de travail : on ne copie que ce qu'on a nomme)
    src_assets = os.path.join(STATIQUE, "assets")
    dst_assets = os.path.join(THEME, "assets")
    os.makedirs(os.path.join(dst_assets, "fonts"))
    for nom in ("site.css", "site.js", "index-en.js", "index-fr.js",
                "favicon.svg", "sceau.svg", "halo.svg",
                "blason-ivoire.svg", "blason-couleur.svg"):
        shutil.copy2(os.path.join(src_assets, nom), os.path.join(dst_assets, nom))
    for nom in os.listdir(os.path.join(src_assets, "fonts")):
        shutil.copy2(os.path.join(src_assets, "fonts", nom),
                     os.path.join(dst_assets, "fonts", nom))

    # 2. les index de recherche : leurs URL pointent sur des fichiers .html
    for langue in ("en", "fr"):
        chemin = os.path.join(dst_assets, "index-%s.js" % langue)
        with open(chemin, encoding="utf-8") as f:
            js = f.read()
        donnees = json.loads(js[js.index("["):].rstrip().rstrip(";"))
        for entree in donnees:
            ref, _, ancre = entree["u"].partition("#")
            # l'index francais nomme ses pages relativement a /fr/
            if langue == "fr" and not ref.startswith("fr/"):
                ref = ref[3:] if ref.startswith("../") else "fr/" + ref
            entree["u"] = url_de(ref) + (("#" + ancre) if ancre else "")
        ecrire(chemin, "window.__IDX=" + json.dumps(donnees, ensure_ascii=False) + ";\n")

    # 3. les gabarits
    ecrire(os.path.join(THEME, "style.css"), STYLE_CSS)
    ecrire(os.path.join(THEME, "functions.php"), FUNCTIONS_PHP)
    ecrire(os.path.join(THEME, "header.php"),
           HEADER_PHP_MODELE.replace("%EN%", php_haut("en")).replace("%FR%", php_haut("fr")))
    ecrire(os.path.join(THEME, "footer.php"),
           FOOTER_PHP_MODELE.replace("%EN%", php_bas("en")).replace("%FR%", php_bas("fr")))
    ecrire(os.path.join(THEME, "page.php"), PAGE_PHP)
    ecrire(os.path.join(THEME, "front-page.php"), PAGE_PHP)
    ecrire(os.path.join(THEME, "index.php"), INDEX_PHP)
    ecrire(os.path.join(THEME, "404.php"), QUATRECENTQUATRE_PHP)

    # 4. la liste des pages pour seed.php
    jumelles = {}
    for a, b in JUMELLES:
        jumelles[a] = b
        jumelles[b] = a
    sortie = []
    for fichier, langue, slug, parent, menu, _titre in PAGES:
        titre_doc, desc = tete_de(fichier)
        sortie.append({
            "fichier": fichier,
            "langue": langue,
            "slug": SLUG_URL.get(slug, slug),
            "cle": slug,
            "parent": parent,
            "menu": menu,
            "titre": _titre,
            "titre_doc": titre_doc,
            "description": desc,
            "jumelle": jumelles.get(slug, ""),
            "contenu": contenu_page(fichier),
        })
    ecrire(os.path.join(ICI, "pages.json"), json.dumps({
        "pages": sortie,
        "menu_principal": MENU_PRINCIPAL,
        "menu_pied": MENU_PIED,
    }, ensure_ascii=False, indent=1))

    print("theme ecrit  : %s" % THEME)
    print("pages.json   : %d pages" % len(sortie))


if __name__ == "__main__":
    main()
