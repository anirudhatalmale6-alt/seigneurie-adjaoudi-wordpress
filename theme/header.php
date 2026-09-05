<?php
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

<a class="saut" href="#contenu">Aller au contenu</a><div class="util"><div class="wrap"><button class="loupe" type="button" aria-label="Rechercher" aria-haspopup="dialog"><svg width="16" height="16" viewBox="0 0 20 20" aria-hidden="true" focusable="false"><circle cx="8.5" cy="8.5" r="6" fill="none" stroke="currentColor" stroke-width="2"/><line x1="13" y1="13" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button><?php seig_langues(); ?><a class="pcircle" href="<?php echo esc_url( home_url( '/fr/cercle-prive/' ) ); ?>">Cercle privé</a></div></div><header class="hdr"><div class="wrap"><a class="brand" href="<?php echo esc_url( home_url( '/fr/' ) ); ?>"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/sceau.svg' ) ); ?>" alt="" width="29" height="47"><span class="nm"><span class="n1">Adjaoudi</span><span class="n2">Seigneurie</span></span></a><button class="bascule" type="button" aria-expanded="false" aria-controls="menu" aria-label="Menu"><svg width="17" height="14" viewBox="0 0 18 14" aria-hidden="true" focusable="false"><g stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="1" y1="1" x2="17" y2="1"/><line x1="1" y1="7" x2="17" y2="7"/><line x1="1" y1="13" x2="17" y2="13"/></g></svg></button><div class="panneau" id="menu"><?php seig_menu( 'principal' ); ?><a class="cta" href="<?php echo esc_url( home_url( '/fr/la-seigneurie/' ) ); ?>">Découvrir la Maison</a></div></div></header>

<?php else : ?>

<a class="saut" href="#contenu">Skip to content</a><div class="util"><div class="wrap"><button class="loupe" type="button" aria-label="Search" aria-haspopup="dialog"><svg width="16" height="16" viewBox="0 0 20 20" aria-hidden="true" focusable="false"><circle cx="8.5" cy="8.5" r="6" fill="none" stroke="currentColor" stroke-width="2"/><line x1="13" y1="13" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button><?php seig_langues(); ?><a class="pcircle" href="<?php echo esc_url( home_url( '/private-circle/' ) ); ?>">Private Circle</a></div></div><header class="hdr"><div class="wrap"><a class="brand" href="<?php echo esc_url( home_url( '/' ) ); ?>"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/sceau.svg' ) ); ?>" alt="" width="29" height="47"><span class="nm"><span class="n1">Adjaoudi</span><span class="n2">Lordship</span></span></a><button class="bascule" type="button" aria-expanded="false" aria-controls="menu" aria-label="Menu"><svg width="17" height="14" viewBox="0 0 18 14" aria-hidden="true" focusable="false"><g stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="1" y1="1" x2="17" y2="1"/><line x1="1" y1="7" x2="17" y2="7"/><line x1="1" y1="13" x2="17" y2="13"/></g></svg></button><div class="panneau" id="menu"><?php seig_menu( 'principal' ); ?><a class="cta" href="<?php echo esc_url( home_url( '/the-lordship/' ) ); ?>">Discover the House</a></div></div></header>

<?php endif; ?>
