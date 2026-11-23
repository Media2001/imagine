"""Refus opérateur de bout en bout, source inventée, gardes anti-site/compte."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_archive_reelle import fixture
TOOLS = ROOT / 'wp/outils/staging-court'
sys.path.insert(0, str(TOOLS))
import publish


def main():
    out = ROOT / 'production/A-01/archive-reelle' / ('refusal-' + uuid.uuid4().hex[:12])
    out.mkdir(parents=True, exist_ok=False)
    scratch = Path.home() / 'AppData/Local/hermes/cache/scratch' if os.name == 'nt' else Path(os.environ['TMPDIR'])
    result = {'status':'FAIL', 'synthetic_only':True, 'site_api_guarded':True, 'downloads_guarded':True}
    with tempfile.TemporaryDirectory(dir=scratch) as tmp:
        archive = Path(tmp) / 'fiction.wpress'
        raw = fixture([('uploads/2026/FICTION\\one.jpg',b'A'),('uploads/2026/FICTION\\two.jpg',b'B'),
                       ('package.json',b'{"WordPress":{"Version":"6.9.1"}}'),('database.sql',b'NOT_EXECUTED')])
        archive.write_bytes(raw)
        args = ['publish.py','--operator-ced','--archive',str(archive),'--name','imagine-test-a01-path-refusal','--production-url','https://fiction.invalid']
        # Real main/runner/copy/preflight/cleanup; forbidden lifecycle/download/
        # password helpers are canaries and must never be reached, even on a bug.
        code = '''import sys
sys.dont_write_bytecode=True
sys.path.insert(0,TOOLS)
import publish
def forbidden(*a,**k): raise AssertionError('FORBIDDEN_EFFECT_REACHED')
publish.api=forbidden
publish.prepare_core=forbidden
publish.read_admin_password=forbidden
sys.argv=ARGV
raise SystemExit(publish.main())
'''.replace('TOOLS',repr(str(TOOLS))).replace('ARGV',repr(args))
        p = subprocess.run([sys.executable,'-c',code],input=b'',capture_output=True,timeout=600)
        (out / 'stdout.log').write_bytes(p.stdout)
        (out / 'stderr.log').write_bytes(p.stderr)
        assert p.returncode == 1
        console = json.loads(p.stdout)
        expected = [{'code':'ARCHIVE_PATH_BACKSLASH','count':2,'first_zone':'uploads/2026','extension':'.jpg'}]
        assert console['refusals'] == expected
        report_path = Path(console['report'])
        assert report_path.resolve().is_relative_to((ROOT / 'production/A-01/publication-23nov').resolve())
        receipt = json.loads(report_path.read_bytes())
        assert len(receipt['cases']) == 1
        case = receipt['cases'][0]
        assert case['status'] == 'FAIL' and 'normal_creation' not in case and 'offline' not in case
        assert 'public_core' not in receipt and 'runtime_core_preflight' not in case
        assert case['archive_core_preflight']['code'] == 'ARCHIVE_PATH_BACKSLASH'
        assert case['archive_core_preflight']['detail']['count'] == 2
        assert receipt['tool_sources_unchanged'] is True
        assert receipt['cleanup'] and not receipt.get('cleanup_errors')
        for item in receipt['cleanup']:
            assert item['absent'] is True
            state = publish.call(['inspect',item['name']],check=False)
            assert state.returncode != 0 and b'no such object' in state.stderr.lower()
        assert raw == archive.read_bytes()
        result.update(subject_exit=p.returncode, subject_report=str(report_path.relative_to(ROOT)),
                      console_refusals=console['refusals'], no_site_created=True, no_core_download=True,
                      source_archive_sha256=hashlib.sha256(raw).hexdigest(),
                      cleanup=receipt['cleanup'], tool_sources_unchanged=True)
    assert not Path(tmp).exists()
    result.update(status='PASS',synthetic_archive_removed=True,scratch_directory_removed=True)
    (out / 'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'status':result['status'],'report':str(out/'result.json')}))


if __name__ == '__main__':
    main()
