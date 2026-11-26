"""Derive only transport negative probes from the accepted A23 fixture."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
p = ROOT / 'wp/tests/a23/inside.py'
s = p.read_text(encoding='utf-8').replace('A23','A25').replace('a23','a25').replace('comptes.json','visiteurs.json').replace('comptes.md','visiteurs.md').replace('inventorier-comptes','inventorier-visiteurs').replace('accounts','visitors')
# Keep native setup, early guards, all independent channel probes, exact fingerprints.
start = s.index('    expected = {')
end = s.index('    payload = ', start)
s = s[:start] + '''    expected = {'comments': {'all': group(autres=3), 'email': group(autres=2),
                              'ip': group(autres=2), 'account': group(autres=1)},
                'forms': group(autres=4), 'guests': group(autres=2)}
    b.check(storage + ':exact_native_counts', d['counts'] == expected)
    b.check(storage + ':closed_form_adapter_and_other', d['forms'] == {
        'listed_extensions': ['Fluent Forms'], 'other_tables': 1, 'clear_messages_after_import': True})
''' + s[end:]
s = s.replace("'--output=/hors-web/comptes-date'", "'--output=/hors-web/visiteurs-date'")
s = s.replace("not re.search(r'CANARY|@|/scratch|user_pass|user_email|user_login|a25-fictif|a02-admin', payload)", "not re.search(r'CANARY|@|/scratch|a25_unknown|a25-fictif|a02-admin|192\\.0\\.2', payload)")
s = s.replace("    return {'groups': [{'label': label, 'visitors': n} for label, n in pairs], 'autres': autres}", "    return {'groups': [], 'autres': autres}")
# Add exact native file fingerprint receipts, not just boolean assertions.
s = s.replace("    b.check(storage + ':site_files_identical', files == b.files(site))", "    final_files = b.files(site)\n    (OUT / (storage + '-files.json')).write_text(json.dumps({'before': files, 'after': final_files}), encoding='utf-8')\n    b.check(storage + ':site_files_identical', files == final_files)")
start = s.index("    b.check(storage + ':actual_import_replaces_three_fields'")
end = s.index("    b.sql('mysql', \"GRANT SELECT", start)
s = s[:start] + '''    b.check(storage + ':actual_import_comments_changed_forms_clear',
            provenance['neutraliser_and_anonymiser_executed'] is True and provenance['marker_count'] == 1
            and provenance['comments_before'] == provenance['comments_after'] == 3
            and provenance['emails_before'] == 2 and provenance['emails_after'] == 3
            and provenance['ip_before'] == 2 and provenance['ip_after'] == 0
            and provenance['known_message_preserved'] and provenance['unknown_message_preserved']
            and provenance['guest_orders_preserved'])
''' + s[end:]
start = s.index("        b.check(storage + ':six_unknown_blocks_never_zero'")
end = s.index('        clone_after =', start)
s = s[:start] + '''        b.check(storage + ':neutral_unknown_never_zero', n['neutralisation'] == 'inconnu après neutralisation'
                and n['counts']['comments']['email'] == 'inconnu après neutralisation'
                and n['counts']['comments']['ip'] == 'inconnu après neutralisation'
                and n['counts']['forms'] == 'inconnu après neutralisation')
        b.check(storage + ':unchanged_native_counts_after_import', n['counts']['comments']['all'] == expected['comments']['all']
                and n['counts']['comments']['account'] == expected['comments']['account']
                and n['counts']['guests'] == expected['guests'])
''' + s[end:]
# No private text even when fixture exceptions are caught by reused oracle.
s = s.replace("b.run_storage = run_storage", "b.run_storage = run_storage")
(ROOT / 'wp/tests/a25/inside.py').write_text(s,encoding='utf-8',newline='\n')
print('Owned A25 native fixture written')
