"""C28 : commandes parentes inchangées, journaux et codes réels."""
import sys
sys.dont_write_bytecode = True
import subprocess
import c28


def run(action, label):
    scripts = {'image':'preparer-image.ps1', 'replay':'rejouer.ps1'}
    assert action in scripts
    log = c28.OUT/(label+'.log')
    assert not log.exists()
    cmd = ['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(c28.ROOT/'wp/tests'/scripts[action])]
    with log.open('xb') as stream:
        p = subprocess.run(cmd, cwd=c28.ROOT, stdout=stream, stderr=subprocess.STDOUT)
    c28.save(label, {'action':action, 'command':cmd, 'exit':p.returncode, 'log':log.name, 'sources':c28.sources()})
    print('\n'.join(log.read_bytes().decode('utf-8','replace').splitlines()[-14:]))
    return p.returncode


if __name__ == '__main__':
    raise SystemExit(run(*sys.argv[1:]))
