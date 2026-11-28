import sys
sys.dont_write_bytecode=True
import c30 as o
import b13
r=b13.c29.docker('run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,nosuid,nodev,size=64m','--mount','type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly','--entrypoint','php','imagine-tests-t01:1','/opt/t01/imagine-site/vendor/bin/phpunit','-c','/repo/wp/plugins/imagine-site/phpunit.xml','--bootstrap','/repo/wp/tests/demo/c30-unit-bootstrap.php','--do-not-cache-result','--filter',sys.argv[2] if len(sys.argv)>2 else 'CodesSuivisC30')
b13.save(o,sys.argv[1],{'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'sources':o.sources(o)})
print(r.stdout,r.stderr);raise SystemExit(r.returncode)
