<?php
/** Squelette B02 : structure uniquement, formulaire et routes restent natifs Woo. */
declare(strict_types=1);
namespace Imagine\Theme;
if (!defined('ABSPATH') || empty($compte) || $compte['user'] !== get_current_user_id()) {
    return;
}
$nomme = static fn (?string $value, string $placeholder): string => $value !== null && $value !== '' ? $value : $placeholder;
?>
<div data-imagine-mon-compte>
<nav aria-label="<?php esc_attr_e('Dans mon compte', 'imagine'); ?>"><ul>
<?php foreach (['abonnement' => __('Mon abonnement', 'imagine'), 'echeances' => __('Mes échéances', 'imagine'),
    'numeros' => __('Mes numéros', 'imagine'), 'coordonnees' => __('Mes coordonnées', 'imagine'),
    'factures' => __('Mes factures et justificatifs', 'imagine')] as $id => $label) : ?>
<li><a href="#imagine-compte-<?php echo esc_attr($id); ?>"><?php echo esc_html($label); ?></a></li>
<?php endforeach; ?></ul></nav>
<section id="imagine-compte-abonnement"><h2><?php esc_html_e('Mon abonnement', 'imagine'); ?></h2>
<?php if (!$compte['abonnements']) : ?><p><?php esc_html_e('Aucun abonnement natif rattaché à ce compte.', 'imagine'); ?></p><?php endif; ?>
<?php foreach ($compte['abonnements'] as $a) : ?>
<article data-imagine-abonnement="<?php echo esc_attr((string) $a['id']); ?>">
<h3><?php echo esc_html($nomme($a['formule'], __('Formule non raccordée', 'imagine'))); ?></h3>
<dl>
<dt><?php esc_html_e('État', 'imagine'); ?></dt><dd><?php echo esc_html($a['etat']); ?></dd>
<dt><?php esc_html_e('Premier numéro couvert — projection C01', 'imagine'); ?></dt><dd><?php echo esc_html($nomme($a['premier'], __('Premier numéro non raccordé', 'imagine'))); ?></dd>
<dt><?php esc_html_e('Dernier numéro couvert — projection C01', 'imagine'); ?></dt><dd><?php echo esc_html($nomme($a['dernier'], __('Dernier numéro non raccordé', 'imagine'))); ?></dd>
<dt><?php esc_html_e('Numéros restants', 'imagine'); ?></dt><dd><?php echo esc_html__('Compteur non raccordé — historique d’activation C01 manquant', 'imagine'); ?></dd>
<dt><?php esc_html_e('Prochaine échéance native', 'imagine'); ?></dt><dd><?php echo esc_html($a['prochaine'] !== '' ? wp_date('j F Y H:i', strtotime($a['prochaine'] . ' UTC'), wp_timezone()) : __('Aucune date native planifiée', 'imagine')); ?></dd>
<dt><?php esc_html_e('Montant récurrent natif', 'imagine'); ?></dt><dd><?php echo wp_kses_post(wc_price($a['montant'], ['currency' => $a['devise']])); ?></dd>
<dt><?php esc_html_e('Moyen de paiement', 'imagine'); ?></dt><dd><?php echo esc_html($a['paiement']); ?><?php if ($a['manuel']) : ?> — <?php esc_html_e('renouvellement manuel', 'imagine'); ?><?php endif; ?></dd>
</dl>
<?php if (function_exists('do_action')) { do_action('imagine_compte_renouvellement', $a); } ?>
<?php if (!empty($a['bloc_indisponible'])) : ?><p data-imagine-bloc-indisponible><?php echo esc_html(__($a['bloc_indisponible'], 'imagine')); ?></p><?php endif; ?>
<?php foreach ($a['avertissements'] ?? [] as $warning) : ?><p data-imagine-rattachement><?php echo esc_html(__($warning, 'imagine')); ?></p><?php endforeach; ?>
<p><?php esc_html_e('La projection des numéros ne prouve ni règlement ni expédition. Les droits PDF ci-dessous sont contrôlés séparément.', 'imagine'); ?></p>
<p><a href="<?php echo esc_url($a['vue']); ?>"><?php esc_html_e('Gérer cet abonnement dans WooCommerce', 'imagine'); ?></a></p>
<?php if ($a['echec'] || in_array($a['etat'], [__('Suspendu', 'imagine-site'), __('En délai de grâce', 'imagine-site')], true)) : ?>
<aside data-imagine-regularisation role="status"><p><?php echo esc_html($a['echec'] ? __('Échéance échouée : régularisation nécessaire.', 'imagine') : __('Abonnement suspendu ou en délai de grâce. Consultez son état pour le régulariser ; aucun rejet bancaire n’est attesté ici.', 'imagine')); ?></p>
<a href="<?php echo esc_url($a['regulariser'] ?? $a['vue']); ?>"><?php echo esc_html(isset($a['regulariser']) ? __('Régulariser la commande dans WooCommerce', 'imagine') : __('Consulter et gérer l’abonnement', 'imagine')); ?></a></aside>
<?php endif; ?></article><?php endforeach; ?></section>
<section id="imagine-compte-echeances"><h2><?php esc_html_e('Mes échéances', 'imagine'); ?></h2>
<?php $quatre = false; foreach ($compte['abonnements'] as $a) : if (!$a['echeances']) { continue; } $quatre = true; ?>
<table data-imagine-echeancier="<?php echo esc_attr((string) $a['id']); ?>"><caption><?php esc_html_e('Quatre positions du bloc — projection, aucun prélèvement lancé', 'imagine'); ?></caption>
<thead><tr><?php foreach ([__('Position', 'imagine'), __('Numéro', 'imagine'), __('Date', 'imagine'), __('État', 'imagine'), __('Montant', 'imagine')] as $label) : ?><th scope="col"><?php echo esc_html($label); ?></th><?php endforeach; ?></tr></thead>
<tbody><?php foreach ($a['echeances'] as $e) : ?><tr>
<th scope="row"><?php echo esc_html((string) $e['rang']); ?></th>
<td><?php echo esc_html($nomme($e['numero'], __('Numéro non raccordé', 'imagine'))); ?></td>
<td><?php echo esc_html($nomme($e['date'], __('Date non raccordée — marge C05 obligatoire', 'imagine'))); ?></td>
<td><?php echo esc_html(__($e['etat'], 'imagine-site')); ?></td>
<td><?php echo $e['montant'] !== null ? wp_kses_post(wc_price($e['montant'], ['currency' => $e['devise']])) : esc_html__('Montant non raccordé', 'imagine'); ?></td>
</tr><?php endforeach; ?></tbody></table>
<?php endforeach; if (!$quatre) : ?><p><?php esc_html_e('Aucun échéancier en quatre fois natif rattaché à ce compte.', 'imagine'); ?></p><?php endif; ?>
</section>
<section id="imagine-compte-numeros"><h2><?php esc_html_e('Mes numéros', 'imagine'); ?></h2>
<?php if (!$compte['numeros']) : ?><p><?php esc_html_e('Aucun numéro accessible en PDF avec vos droits actuels.', 'imagine'); ?></p><?php else : ?><ul>
<?php foreach ($compte['numeros'] as $n) : ?><li data-imagine-numero="<?php echo esc_attr((string) $n['id']); ?>"><a href="<?php echo esc_url($n['url']); ?>"><?php echo esc_html($n['titre']); ?></a> — <a href="<?php echo esc_url($n['pdf']); ?>"><?php esc_html_e('Télécharger le PDF protégé', 'imagine'); ?></a></li><?php endforeach; ?></ul><?php endif; ?>
</section>
<section id="imagine-compte-coordonnees"><h2><?php esc_html_e('Mes coordonnées', 'imagine'); ?></h2>
<?php foreach ($compte['abonnements'] as $a) : ?><article>
<h3><?php echo esc_html(sprintf(__('Adresse postale de l’abonnement %s', 'imagine'), (string) $a['id'])); ?></h3>
<address><?php echo wp_kses_post(WC()->countries->get_formatted_address($a['adresse'])); ?></address>
<p><?php esc_html_e('Source : adresse de livraison de cette souscription, la même que la liste d’envoi. Le gel des listes closes relève du raccord postal C13.', 'imagine'); ?></p>
<p><a href="<?php echo esc_url($a['edition_adresse']); ?>"><?php esc_html_e('Modifier cette adresse postale', 'imagine'); ?></a></p></article><?php endforeach; ?>
<?php if (!$compte['abonnements']) : ?><p><a href="<?php echo esc_url(wc_get_account_endpoint_url('edit-address')); ?>"><?php esc_html_e('Gérer mes adresses WooCommerce', 'imagine'); ?></a></p><?php endif; ?>
</section>
<section id="imagine-compte-factures"><h2><?php esc_html_e('Mes factures et justificatifs', 'imagine'); ?></h2>
<ul data-imagine-factures><li><?php esc_html_e('Aucune facture disponible — raccord documentaire Odoo non disponible.', 'imagine'); ?></li></ul>
<?php if (function_exists('do_action')) { do_action('imagine_compte_justificatif'); } ?>
<p><?php esc_html_e('Les commandes ne sont pas présentées comme des factures.', 'imagine'); ?> <a href="<?php echo esc_url(wc_get_account_endpoint_url('orders')); ?>"><?php esc_html_e('Voir mes commandes', 'imagine'); ?></a></p>
</section></div>
