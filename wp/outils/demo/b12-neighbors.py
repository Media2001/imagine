"""B12 complementary receipts: old packets immutable; only additive boot portion excluded."""
import sys
sys.dont_write_bytecode=True
import contextlib
import hashlib
import importlib.util
import io
import json
import b12
import b11
import c28
ROOT,OUT=b12.ROOT,b12.OUT
BOOT='wp/plugins/imagine-site/imagine-site.php'
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def run(label):
    b12.guard(); before=b11.state()
    raw=(ROOT/BOOT).read_text(encoding='utf-8')
    assert raw.count(b12.BLOCK)==1
    legacy=hashlib.sha256(raw.replace(b12.BLOCK,'').encode()).hexdigest()
    current=hashlib.sha256((ROOT/BOOT).read_bytes()).hexdigest()
    receipts={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['production/B-11/reception-politique1330-V2.json','production/C-28/reception-corrections.json','production/C-27/correction-final-V2.json']}
    for owner,path in [(b11,'production/B-11/reception-politique1330-V2.json'),(c28,'production/C-28/reception-corrections.json')]:
        expected=json.loads((ROOT/path).read_text(encoding='utf-8'))['sources']
        actual=owner.sources()
        assert set(actual)==set(expected)
        assert {n for n in actual if actual[n]!=expected[n]}=={BOOT}
        assert expected[BOOT]==legacy
        # Component contract: exactly one additive B12 block, all other bytes sealed.
        def component_sources(original=owner.sources):
            values=original(); assert values[BOOT]==current
            values[BOOT]=legacy
            return values
        owner.sources=component_sources
    buffer=io.StringIO()
    with contextlib.redirect_stdout(buffer):
        c27=load_module('c27_receipt',ROOT/'production/C-27/verifier.py')
        c27_result=c27.validate(ROOT,c27.load(ROOT/'production/C-27/correction-final-V2.json'))
        print('C27 PASS',json.dumps(c27_result))
        v11=load_module('b11_receipt',ROOT/'wp/tests/demo/b11-verifier1330.py')
        a=v11.verify(False); b=v11.verify(True)
        v28=load_module('c28_receipt',ROOT/'wp/tests/demo/c28-verifier.py')
        c=v28.verify(False); d=v28.verify(True)
        # Re-exercise native adapters without replacing the neighbors' receipts.
        b11.OUT=OUT
        b11.runtime(label+'-B11-native')
        c28.OUT=OUT
        c28.runtime(label+'-C28-native')
    assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h for n,h in receipts.items())
    assert before==b11.state()
    with (OUT/(label+'.log')).open('x',encoding='utf-8') as f:f.write(buffer.getvalue())
    b12.save(label,{'scope':'imagine-test-demo','status':'PASS','bootstrap_current':current,'bootstrap_without_only_B12':legacy,'excluded_exact_block':b12.BLOCK,'all_other_component_bytes_exact':True,'historical_receipts_unchanged':receipts,'checks':{'C27':c27_result['gates'],'B11_offline':len(a),'B11_live':len(b),'C28_offline':len(c),'C28_live':len(d)},'business_preserved':True,'UI_save_verified':False,'log':label+'.log'})
    print(buffer.getvalue())
if __name__=='__main__':run(sys.argv[1])
