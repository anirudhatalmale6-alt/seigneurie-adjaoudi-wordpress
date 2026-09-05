<?php
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
