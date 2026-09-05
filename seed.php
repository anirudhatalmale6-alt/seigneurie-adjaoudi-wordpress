<?php
/**
 * Cree le contenu du site dans WordPress a partir de pages.json.
 *
 * Le script est IDEMPOTENT : relance-le autant de fois que tu veux, il met a
 * jour les pages existantes au lieu d'en creer des doubles. C'est ce qui
 * permet de corriger le gabarit et de resemer sans repartir d'une base vide.
 *
 * Usage : php seed.php /chemin/vers/wordpress /chemin/vers/pages.json
 */

if ( php_sapi_name() !== 'cli' ) { exit( 1 ); }

$racine = rtrim( $argv[1] ?? '', '/' );
$json   = $argv[2] ?? '';
if ( ! $racine || ! $json ) {
	fwrite( STDERR, "usage: seed.php <wordpress> <pages.json>\n" );
	exit( 1 );
}

require $racine . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/post.php';

/* En ligne de commande il n'y a pas d'utilisateur connecte, donc WordPress
   applique kses au contenu qu'on lui donne : il retire les <form>, les
   <input> et les attributs onsubmit des maquettes de formulaire. Le site
   perdrait ses formulaires sans le moindre message. */
kses_remove_filters();

$donnees = json_decode( file_get_contents( $json ), true );
if ( ! $donnees ) { fwrite( STDERR, "pages.json illisible\n" ); exit( 1 ); }

/* ------------------------------------------------------------- reglages */

switch_theme( 'seigneurie' );
update_option( 'blogname', 'Adjaoudi Lordship' );
update_option( 'blogdescription', '' );
/* Poser l'option ne suffit pas : $wp_rewrite a deja lu l'ancienne valeur au
   chargement, et get_permalink() rendrait des URL en ?page_id= pendant tout ce
   script — c'est-a-dire exactement les URL qu'on ecrirait ensuite en base. */
global $wp_rewrite;
$wp_rewrite->set_permalink_structure( '/%postname%/' );
update_option( 'default_comment_status', 'closed' );
update_option( 'default_ping_status', 'closed' );
update_option( 'comment_registration', 1 );
update_option( 'blog_public', 0 );          // le site part en preproduction
update_option( 'timezone_string', '' );
update_option( 'gmt_offset', 0 );
update_option( 'start_of_week', 1 );

/* Le contenu par defaut de WordPress n'a rien a faire sur ce site. */
foreach ( get_posts( array(
	'post_type'   => array( 'post', 'page' ),
	'post_status' => 'any',
	'numberposts' => -1,
	'fields'      => 'ids',
) ) as $id_defaut ) {
	if ( ! get_post_meta( $id_defaut, '_seig_cle', true ) ) {
		wp_delete_post( $id_defaut, true );
	}
}
update_option( 'wp_page_for_privacy_policy', 0 );

/* ---------------------------------------------------------------- pages */

/**
 * Retrouve une page par sa cle de chantier, jamais par son titre : deux pages
 * du site portent le meme titre dans les deux langues (Contact, Journal,
 * Initiatives), et chercher par titre en attraperait une au hasard.
 */
function seig_page_par_cle( $cle ) {
	$q = get_posts( array(
		'post_type'   => 'page',
		'post_status' => 'any',
		'numberposts' => 2,
		'meta_key'    => '_seig_cle',
		'meta_value'  => $cle,
		'fields'      => 'ids',
	) );
	return $q ? (int) $q[0] : 0;
}

/** Decoupe le contenu en blocs « HTML personnalise », un par element. */
function seig_blocs( $html ) {
	$blocs = array();
	foreach ( preg_split( '/\r?\n/', $html ) as $ligne ) {
		$ligne = trim( $ligne );
		if ( '' === $ligne ) { continue; }
		$blocs[] = "<!-- wp:html -->\n" . $ligne . "\n<!-- /wp:html -->";
	}
	return implode( "\n\n", $blocs );
}

$racine_url = untrailingslashit( home_url() );
$ids = array();

// premier passage : les parents d'abord, sinon l'URL des filles est fausse
usort( $donnees['pages'], function ( $a, $b ) {
	return ( $a['parent'] ? 1 : 0 ) - ( $b['parent'] ? 1 : 0 );
} );

foreach ( $donnees['pages'] as $page ) {
	$contenu = str_replace( '%%URL%%', $racine_url, $page['contenu'] );
	$parent  = $page['parent'] ? ( $ids[ $page['parent'] ] ?? 0 ) : 0;

	$champs = array(
		'post_type'      => 'page',
		'post_status'    => 'publish',
		'post_author'    => 1,
		'post_title'     => $page['titre'],
		'post_name'      => $page['slug'],
		'post_parent'    => $parent,
		'post_content'   => seig_blocs( $contenu ),
		'comment_status' => 'closed',
		'ping_status'    => 'closed',
	);

	$id = seig_page_par_cle( $page['cle'] );
	if ( $id ) {
		$champs['ID'] = $id;
		wp_update_post( $champs );
	} else {
		$id = wp_insert_post( $champs, true );
		if ( is_wp_error( $id ) ) {
			fwrite( STDERR, 'echec : ' . $page['cle'] . ' : ' . $id->get_error_message() . "\n" );
			exit( 1 );
		}
	}
	update_post_meta( $id, '_seig_cle', $page['cle'] );
	update_post_meta( $id, '_seig_lang', $page['langue'] );
	update_post_meta( $id, '_seig_title', $page['titre_doc'] );
	update_post_meta( $id, '_seig_desc', $page['description'] );
	$ids[ $page['cle'] ] = $id;
	echo sprintf( "page %-18s -> #%d  %s\n", $page['cle'], $id, get_permalink( $id ) );
}

// second passage : la page jumelle, qui n'existait pas forcement au premier
foreach ( $donnees['pages'] as $page ) {
	$alt = $page['jumelle'] ? ( $ids[ $page['jumelle'] ] ?? 0 ) : 0;
	update_post_meta( $ids[ $page['cle'] ], '_seig_alt', $alt );
}

/* L'accueil anglais est la page d'accueil du site. */
update_option( 'show_on_front', 'page' );
update_option( 'page_on_front', $ids['home'] );
update_option( 'page_for_posts', 0 );

/* ---------------------------------------------------------------- menus */

$emplacements = array();
foreach ( array( 'principal' => 'menu_principal', 'pied' => 'menu_pied' ) as $ou => $cle ) {
	foreach ( array( 'en', 'fr' ) as $langue ) {
		$nom = ( 'principal' === $ou ? 'Menu principal' : 'Pied de page' )
			. ' (' . ( 'fr' === $langue ? 'Français' : 'English' ) . ')';

		$menu = wp_get_nav_menu_object( $nom );
		if ( $menu ) {
			foreach ( wp_get_nav_menu_items( $menu->term_id ) as $item ) {
				wp_delete_post( $item->ID, true );
			}
			$menu_id = $menu->term_id;
		} else {
			$menu_id = wp_create_nav_menu( $nom );
			if ( is_wp_error( $menu_id ) ) {
				fwrite( STDERR, 'menu : ' . $menu_id->get_error_message() . "\n" );
				exit( 1 );
			}
		}

		foreach ( $donnees[ $cle ][ $langue ] as $page_cle ) {
			$titre = '';
			foreach ( $donnees['pages'] as $p ) {
				if ( $p['cle'] === $page_cle ) { $titre = $p['menu']; break; }
			}
			wp_update_nav_menu_item( $menu_id, 0, array(
				'menu-item-object-id' => $ids[ $page_cle ],
				'menu-item-object'    => 'page',
				'menu-item-type'      => 'post_type',
				'menu-item-title'     => $titre,
				'menu-item-status'    => 'publish',
			) );
		}
		$emplacements[ $ou . '-' . $langue ] = $menu_id;
		echo sprintf( "menu %-14s -> #%d  (%d entrees)\n", $ou . '-' . $langue, $menu_id,
			count( $donnees[ $cle ][ $langue ] ) );
	}
}
set_theme_mod( 'nav_menu_locations', $emplacements );

/* ------------------------------------------------------------- nettoyage */

/* Les revisions gardent l'historique de MES essais, y compris des versions
   intermediaires fausses. Elles n'ont rien a faire dans la sauvegarde livree :
   le client repart d'une page propre, et son propre historique commence a sa
   premiere modification. */
$revisions = get_posts( array(
	'post_type'   => 'revision',
	'post_status' => 'any',
	'numberposts' => -1,
	'fields'      => 'ids',
) );
foreach ( $revisions as $r ) { wp_delete_post_revision( $r ); }
echo sprintf( "revisions supprimees : %d\n", count( $revisions ) );

flush_rewrite_rules( true );

echo "\ntheme actif : " . get_stylesheet() . "\n";
echo "accueil     : " . home_url( '/' ) . "\n";
echo "pages       : " . count( $ids ) . "\n";
