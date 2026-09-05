<?php
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

<footer class="pied"><div class="wrap"><div class="cols"><div><h4>Sections</h4><?php seig_menu( 'pied' ); ?></div><div><h4>Canaux officiels</h4><ul><li><span class="att">En attente d’autorisation</span></li></ul></div><div><h4>Langues</h4><?php seig_langues_pied(); ?><p style="font-size:.83rem;color:#B0A49A">Des versions en arabe et en tamazight sont prévues. Le site est bâti pour qu’une troisième langue soit un dossier et une traduction, pas une reconstruction.</p></div></div><p class="decl">La Seigneurie Adjaoudi est une identité familiale et culturelle. Elle n’est pas une autorité publique, n’exerce aucune fonction officielle, et ne confère aucun titre, rang, préséance ou noblesse. Ni la désignation ni le blason ne sont présentés comme reconnus, concédés, enregistrés ou accrédités par une quelconque autorité.</p><p class="bas">Seigneurie Adjaoudi</p></div></footer>
<div class="rech" id="rech" role="dialog" aria-modal="true" aria-label="Rechercher"><div class="boite"><div class="barre"><label class="sr" for="q">Rechercher</label><input id="q" type="search" autocomplete="off" placeholder="Rechercher dans le site"><button class="fermer" type="button">Fermer</button></div><ul class="res" id="res"></ul><p class="sr" id="rech-vide">Aucune section ne correspond à cette recherche.</p></div></div>
<noscript><p class="sr">La recherche demande JavaScript. Toutes les pages sont accessibles depuis le menu ci-dessus.</p></noscript>

<?php else : ?>

<footer class="pied"><div class="wrap"><div class="cols"><div><h4>Sections</h4><?php seig_menu( 'pied' ); ?></div><div><h4>Official channels</h4><ul><li><span class="att">Awaiting authorisation</span></li></ul></div><div><h4>Languages</h4><?php seig_langues_pied(); ?><p style="font-size:.83rem;color:#B0A49A">Arabic and Tamazight versions are planned. The site is built so that a third language is a folder and a translation, not a rebuild.</p></div></div><p class="decl">The Adjaoudi Lordship is a family and cultural identity. It is not a public authority, exercises no official function, and confers no title, rank, precedence or nobility. Neither the designation nor the coat of arms is claimed to be recognised, granted, registered or accredited by any authority whatsoever.</p><p class="bas">Adjaoudi Lordship</p></div></footer>
<div class="rech" id="rech" role="dialog" aria-modal="true" aria-label="Search"><div class="boite"><div class="barre"><label class="sr" for="q">Search</label><input id="q" type="search" autocomplete="off" placeholder="Search the site"><button class="fermer" type="button">Close</button></div><ul class="res" id="res"></ul><p class="sr" id="rech-vide">No section matches that search.</p></div></div>
<noscript><p class="sr">Search needs JavaScript. Every page is reachable from the menu above.</p></noscript>

<?php endif; ?>
<?php wp_footer(); ?>
</body>
</html>
