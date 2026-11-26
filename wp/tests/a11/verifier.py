"""Verify the A11 packet against the exact final local sources, no PHP or site access."""
import argparse
import hashlib
import json
import pathlib
import sys
sys.dont_write_bytecode = True
REPO = pathlib.Path(__file__).resolve().parents[3]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('packet',type=pathlib.Path)
    args=ap.parse_args()
    packet=args.packet.resolve()
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    runner=read(packet/'runner.json')
    unit=read(packet/'unit.json')
    native=read(packet/'result.json')
    assert all(r['exit_code']==0 and r['checks'] and all(c['status']=='PASS' for c in r['checks']) for r in [runner,unit,native])
    source=read(packet/'sources.json')
    assert source and all(hashlib.sha256((REPO/p).read_bytes()).hexdigest()==h for p,h in source.items())
    before=read(packet/'protected-before.json'); after=read(packet/'protected-after.json')
    assert before==after  # Frozen execution non-regression, not a current sibling pin.
    assert all(p.startswith(('wp/tests/a11/','wp/outils/bascule/a11/')) for p in source)
    doc=(REPO/'wp/tests/a02-audit/README.md').read_text(encoding='utf-8')
    assert all(s in doc for s in ('a11/inventorier-adresses','adresses.csv','adresses.json','empreinte du rapport A-02','A-09','a11/README.md'))
    names={c['check'] for c in native['checks']}
    counts={}
    for storage in ['classic','hpos']:
        for name in ['custom_mu_before_bootstrap','site_symlink_named','failed_select_no_validated_packet']:
            assert storage+':pretty:'+name in names
        for filename in ['object-cache.php','advanced-cache.php','db.php','sunrise.php','wordfence-waf.php','.user.ini']:
            assert storage+':pretty:dropin_refused_before_execution:'+filename in names
        for variant in ['pretty','plain','subdir','attachments-disabled','static-front']:
            stem=storage+'-'+variant
            key=storage+':'+variant+':'
            for check in ['cli','a09_exact_convention','exact_native_urls_and_natures','dates_and_status_native','summary_counts_exact','native_permalink_bases','excluded_exact','root_write_denied','all_tables_unchanged','files_unchanged','no_http_mail_scheduling','repeat']:
                assert key+check in names, key+check
            assert read(packet/(stem+'-before.json'))==read(packet/(stem+'-after.json'))
            proof=read(packet/(stem+'-readonly.json'))
            assert proof and all(proof.values()) and proof['server_readonly']
            report=read(packet/(stem+'-addresses/adresses.json'))
            counts[stem]=report['total']
            assert report['total']==len(report['adresses'])==len({r['ancienne'] for r in report['adresses']})
    result={'verified':True,'unit_checks':len(unit['checks']),'native_checks':len(native['checks']),'runner_checks':len(runner['checks']),'source_files':len(source),'counts':counts,'packet':str(packet),'runner_sha256':hashlib.sha256((packet/'runner.json').read_bytes()).hexdigest()}
    print(json.dumps(result,indent=2))
    return 0
if __name__=='__main__': sys.exit(main())
