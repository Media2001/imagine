"""Vrais POST options.php C25 ; aucune écriture des réglages des autres lots."""
import re
from html import unescape


def run(c25, http, base, admin, checks):
    path = '/wp-admin/admin.php?page=imagine-reglages'
    headers = {'X-Imagine-C25-Settings': 'recette-fictive', 'Referer': base + path}

    def read():
        return c25.wp('''global $wpdb;$events=[];foreach($wpdb->get_col("SELECT option_value FROM {$wpdb->options} WHERE option_name LIKE 'imagine_reglages_journal_%' ORDER BY option_id") as $raw){$e=maybe_unserialize($raw);if(is_array($e)&&($e['option']??'')===Imagine\\Site\\Retractation::OPTION){$events[]=$e;}}echo wp_json_encode(['value'=>get_option(Imagine\\Site\\Retractation::OPTION,null),'events'=>$events]);''')

    def post(days, origin, fault=False):
        page = http(path, user=admin)
        forms = re.findall(r'''<form\b[^>]*action=["']options.php["'][^>]*>(.*?)</form>''', page, re.S)
        assert len(forms) == 1 and 'imagine-retractation-reglages' in forms[0]
        fields = dict(re.findall(r'''name=["']([^"']+)["']\s+(?:[^>]*?)value=["']([^"']*)["']''', forms[0]))
        assert fields.get('option_page') == 'imagine_reglages' and fields.get('_wpnonce')
        payload = {k: unescape(fields[k]) for k in ['option_page', 'action', '_wpnonce', '_wp_http_referer']}
        payload.update({'imagine_retractation_reglages[jours]': str(days), 'imagine_retractation_reglages[origine]': origin})
        return http('/wp-admin/options.php', user=admin, data=payload,
                    headers={**headers, **({'X-Imagine-C25-Failure': 'journal'} if fault else {})})

    before = read()
    assert before['value'] is None, 'Préimage C25 attendue absente'
    failed_creation = post(1, 'manuelle', True)
    checks['options_creation_panne_preimage_absente_relue'] = read() == before and 'setting-error-imagine_retractation_journal' in failed_creation
    post(14, 'paiement')
    created = read()
    events = created['events'][len(before['events']):]
    checks['options_creation_journal_avant_apres_auteur_UTC'] = created['value'] == {'jours': 14, 'origine': 'paiement'} and len(events) == 1 and events[0]['avant'] is None and events[0]['apres'] == created['value'] and events[0]['qui_id'] == admin and bool(events[0]['qui_login']) and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ', events[0]['quand_utc']) is not None
    post(1, 'manuelle')
    modified = read()
    checks['options_modification_journal_2_reglages'] = modified['value'] == {'jours': 1, 'origine': 'manuelle'} and len(modified['events']) == len(created['events']) + 1 and modified['events'][-1]['avant'] == created['value'] and modified['events'][-1]['apres'] == modified['value'] and modified['events'][-1]['qui_id'] == admin
    failed_update = post(30, 'paiement', True)
    checks['options_modification_panne_preimage_exacte_relue'] = read() == modified and 'setting-error-imagine_retractation_journal' in failed_update
    page = http(path, user=admin)
    checks['options_journal_affiche_C10'] = 'imagine_retractation_reglages' in page and modified['events'][-1]['qui_login'] in page
    post(14, 'paiement')
    checks['options_reprise_apres_panne'] = read()['value'] == {'jours': 14, 'origine': 'paiement'}
    checks['options_deux_pannes_SQL_reelles'] = c25.wp('echo wp_json_encode(get_option("imagine_c25_observations")["settings_SQL_refus"]??0);') == 2
    return {'created': created, 'modified': modified, 'final': read(), 'fixture_group_restricted_to_C25': True}
