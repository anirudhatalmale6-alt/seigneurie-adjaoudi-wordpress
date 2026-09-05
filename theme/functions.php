<?php
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
