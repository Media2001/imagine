<?php
/** C20 current safe presentation only: native profiles, no mutation. */
declare(strict_types=1);
namespace Imagine\Demo\C20Ui;
use Imagine\Site\{MonCompte, Paywall};
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo' || home_url() !== 'http://192.168.129.32:8085') {
    throw new \RuntimeException('C20 fictitious target required');
}
$f = get_option('imagine_c09_fixture');
$checks = [];
foreach (['A-CARTE','A-SEPA4','A-VIR','A-PAPIER'] as $who) {
    wp_set_current_user($f['users'][$who]);
    $row = MonCompte::donnees()['abonnements'][0];
    ob_start();
    do_action('imagine_compte_renouvellement', $row);
    $html = ob_get_clean();
    $checks[$who . '_presentation'] = str_contains($html, 'data-imagine-renouvellement');
    $checks[$who . '_no_C20_button'] = !str_contains($html, '<button') && !str_contains($html, '<form');
    $expected = $who === 'A-SEPA4' ? 'faites la demande auprès d’Imagine' : 'renouvellement est manuel';
    $checks[$who . '_message'] = str_contains(html_entity_decode($html), $expected);
    $sub = wcs_get_subscription($f['subscriptions'][$who]);
    $actions = wcs_get_all_user_actions_for_subscription($sub, get_current_user_id());
    $checks[$who . '_native_cancel_button_hidden'] = !isset($actions['cancel']) && !isset($actions['reactivate']);
}
wp_set_current_user($f['users']['A-VIR']);
$row['id'] = $f['subscriptions']['A-CARTE'];
ob_start();
do_action('imagine_compte_renouvellement', $row);
$checks['other_owner_no_presentation'] = ob_get_clean() === '';
$sub = wcs_get_subscription($row['id']);
$checks['native_other_owner_mutation_refused'] = !\WCS_User_Change_Status_Handler::validate_request(get_current_user_id(), $sub, 'cancelled');
wp_set_current_user(0);
echo wp_json_encode(['checks'=>$checks,'total'=>count($checks),'failures'=>array_keys(array_filter($checks,static fn($ok)=>!$ok))]);
