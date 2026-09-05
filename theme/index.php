<?php
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
