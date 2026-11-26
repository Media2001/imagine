"""B06 : gates locaux canoniques, reçus distincts sans remplacer les historiques."""
import sys
sys.dont_write_bytecode = True
import json, subprocess, hashlib
import b06


def command(label, args):
    assert not (b06.PROOF/(label+'.json')).exists()
    process = subprocess.run(args, cwd=b06.ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=900)
    result = {'command':args,'exit':process.returncode,'stdout':process.stdout,'stderr':process.stderr}
    b06.save(label,result)
    print(label, 'exit',process.returncode, (process.stdout+process.stderr)[-1400:])
    assert process.returncode==0
    return result


def run():
    command('fusion-image-final-V2',['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File','wp/tests/preparer-image.ps1'])
    docker = ['wsl.exe','-d','Ubuntu','--','docker','run','--rm','--pull','never','--network','none','--read-only',
              '--tmpfs','/tmp:rw,nosuid,nodev,size=128m,mode=1777','--user','65534:65534','--cap-drop','ALL',
              '--security-opt','no-new-privileges','--mount','type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly',
              '--entrypoint','php','imagine-tests-t01:1']
    quality = subprocess.run(docker+['/opt/t01/imagine-site/vendor/bin/phpcs','--standard=PSR12','--exclude=Generic.Files.LineLength','--report=json',
                                    '/repo/wp/plugins/imagine-site/Cooperateurs.php','/repo/wp/plugins/imagine-site/CooperateursRegles.php'],
                             capture_output=True,text=True,encoding='utf-8',timeout=120)
    report = json.loads(quality.stdout)
    b06.save('fusion-quality-V2',{'exit':quality.returncode,'report':report,'stderr':quality.stderr})
    assert quality.returncode==0 and report['totals']['errors']==0 and not quality.stderr
    command('fusion-regression-final-V2',['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File','wp/tests/rejouer.ps1'])


if __name__=='__main__': run()
