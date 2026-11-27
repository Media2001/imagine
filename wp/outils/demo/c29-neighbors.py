"""C29 successor receipt: strip only owned bootstrap delta; historical packets never rewritten."""
import sys
sys.dont_write_bytecode=True
import contextlib
import hashlib
import importlib.util
import io
import json
import c29
import b11
import b12
import c28
ROOT,OUT=c29.ROOT,c29.OUT
BOOT='wp/plugins/imagine-site/imagine-site.php'

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def predecessor(raw):
    assert raw.count(c29.BLOCK.encode())==1, 'C29 block absent/duplicated'
    old=raw.replace(c29.BLOCK.encode(),b'',1)
    expected=json.loads((ROOT/'production/B-12/reception-complement-voisins-V2.json').read_text(encoding='utf-8'))['bootstrap_current']
    assert hashlib.sha256(old).hexdigest()==expected, 'Unrelated bootstrap bytes changed'
    return old

def run(label,live=True):
    if live:b11.guard()
    before=c29.state() if live else None
    raw=(ROOT/BOOT).read_bytes();old=predecessor(raw);current=hashlib.sha256(raw).hexdigest()
    rejected=False
    try:predecessor(raw+b'\n')
    except AssertionError:rejected=True
    assert rejected
    names=['production/C-27/correction-final-V2.json','production/C-28/reception-corrections.json','production/B-11/reception-politique1330-V2.json','production/B-12/reception-V2.json','production/B-12/reception-complement-voisins-V2.json']
    names += ['production/'+n+'/PRET' for n in ['C-27','C-28','B-11','B-12']]
    history={n:digest(ROOT/n) for n in names}
    for owner,path,legacy in [(b12,'production/B-12/reception-V2.json',old),(b11,'production/B-11/reception-politique1330-V2.json',old.replace(b12.BLOCK.encode(),b'',1)),(c28,'production/C-28/reception-corrections.json',old.replace(b12.BLOCK.encode(),b'',1))]:
        expected=json.loads((ROOT/path).read_text(encoding='utf-8'))['sources']
        actual=owner.sources()
        assert set(actual)==set(expected)
        assert {k for k in actual if actual[k]!=expected[k]}=={BOOT}
        assert hashlib.sha256(legacy).hexdigest()==expected[BOOT]
        def component_sources(original=owner.sources,legacy_sha=expected[BOOT]):
            values=original();assert values[BOOT]==current
            values[BOOT]=legacy_sha;return values
        owner.sources=component_sources
    buffer=io.StringIO()
    with contextlib.redirect_stdout(buffer):
        c27=module('c29_C27',ROOT/'production/C-27/verifier.py')
        a=c27.validate(ROOT,c27.load(ROOT/'production/C-27/correction-final-V2.json'))
        print('C27',a)
        v11=module('c29_B11',ROOT/'wp/tests/demo/b11-verifier1330.py')
        b=v11.verify(False);d=v11.verify(True) if live else None
        v28=module('c29_C28',ROOT/'wp/tests/demo/c28-verifier.py')
        e=v28.verify(False);f=v28.verify(True) if live else None
        v12=module('c29_B12',ROOT/'wp/tests/demo/b12-verifier.py')
        g=v12.verify(False);h=v12.verify(True) if live else None
    assert all(digest(ROOT/n)==sha for n,sha in history.items())
    restored=before==c29.state() if live else None
    if live:assert restored
    with (OUT/(label+'.log')).open('x',encoding='utf-8') as stream:stream.write(buffer.getvalue())
    c29.save(label,{'scope':'imagine-test-demo','status':'PASS','bootstrap_current':current,'bootstrap_without_only_C29':hashlib.sha256(old).hexdigest(),
        'exact_owned_block':c29.BLOCK,'all_other_component_bytes_exact':True,'unrelated_bootstrap_tamper_rejected':rejected,
        'historical_receipts_and_PRET_unchanged':history,'checks':{'C27':a['gates'],'B11_offline':len(b),'B11_live':len(d) if d else None,'C28_offline':len(e),'C28_live':len(f) if f else None,'B12_offline':g,'B12_live':h},
        'business_preserved':restored,'mode':'offline-and-live-readonly' if live else 'offline','log':label+'.log','UI_save_verified':False,
        'boundary':'Existing independent packet readers and their live exact-source checks; no replay of mutating neighbor recipes, no historical reseal.'})
    print(buffer.getvalue());print('All historical packets and B12 companion preserved')
if __name__=='__main__':run(sys.argv[1], '--offline' not in sys.argv[2:])
