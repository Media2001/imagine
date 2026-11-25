"""A04 PSR-12 only in owned offline PHP container; optional owned-file fixes."""
import argparse,hashlib,importlib.util,json,pathlib,sys,uuid
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('a04_runner',ROOT/'run.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--fix',action='store_true');args=parser.parse_args()
    name='imagine-a04-style-'+uuid.uuid4().hex[:12];out=r.REPO/'production/A-04/style'/name;out.mkdir(parents=True)
    tool=pathlib.Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a02-phpcs.phar')
    assert hashlib.sha256(tool.read_bytes()).hexdigest()=='9ff3ddf1fcc6c9347a57bed63da10edfc6610e4339c6bee149e92537609c7939'
    targets=list((r.REPO/'wp/outils/bascule/a04').glob('*.php'))
    created=False;receipt={'exit_code':1,'cleanup':False}
    try:
        r.bench.call(['create','--name',name,'--label',r.LABEL+'='+name,'--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','--pull','never','--no-healthcheck','--entrypoint','/bin/sleep',r.bench.IMAGE,'infinity']);created=True
        r.bench.validate(json.loads(r.bench.call(['inspect',name]).stdout)[0],name)
        r.bench.call(['start',name]);r.bench.call(['exec',name,'mkdir','/subject'])
        r.bench.call(['cp',r.bench.local(tool),name+':/phpcs.phar'])
        for p in targets:r.bench.call(['cp',r.bench.local(p),name+':/subject/'+p.name])
        paths=['/subject/'+p.name for p in targets]
        if args.fix:
            code="<?php require 'phar:///phpcs.phar/autoload.php'; $runner = new PHP_CodeSniffer\\Runner(); exit($runner->runPHPCBF());"
            r.bench.call(['exec','-i',name,'tee','/fix.php'],input_text=code)
            fixed=r.bench.call(['exec',name,'php','/fix.php','--standard=PSR12']+paths,check=False)
            (out/'fix.log').write_text(fixed.stdout+fixed.stderr)
            for p in targets:r.bench.call(['cp',name+':/subject/'+p.name,r.bench.local(p)])
        checked=r.bench.call(['exec',name,'php','/phpcs.phar','--standard=PSR12','--report=json']+paths,check=False)
        detail=json.loads(checked.stdout);(out/'phpcs.json').write_text(checked.stdout)
        strict=r.bench.call(['exec',name,'php','/phpcs.phar','--standard=PSR12','-n','--report=json']+paths,check=False)
        receipt.update(exit_code=strict.returncode,all_messages_exit=checked.returncode,totals=detail['totals'],sources={str(p.relative_to(r.REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in targets})
        r.bench.validate(json.loads(r.bench.call(['inspect',name]).stdout)[0],name)
    finally:
        if created:
            v=json.loads(r.bench.call(['inspect',name]).stdout)[0];assert v['Name']=='/'+name and v['Config']['Labels'].get(r.LABEL)==name
            r.bench.call(['rm','-f',name]);v=r.bench.call(['inspect',name],check=False);receipt['cleanup']=v.returncode!=0 and 'no such' in v.stderr.lower()
        (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'output':str(out),**receipt},indent=2))
    return receipt['exit_code']
if __name__=='__main__':sys.exit(main())
