"""Portes B08 canoniques et références natives officielles."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import subprocess
import urllib.request
import re
import b08


def run(kind, label):
    assert kind in ['prepare', 'regression', 'standard']
    if kind == 'standard':
        urls = ['https://developer.wordpress.org/reference/functions/wp_insert_post/', 'https://developer.wordpress.org/reference/functions/wp_nav_menu/', 'https://developer.wordpress.org/plugins/privacy/adding-the-personal-data-exporter-to-your-plugin/', 'https://developer.wordpress.org/plugins/privacy/adding-the-personal-data-eraser-to-your-plugin/']
        rows = []
        for url in urls:
            with urllib.request.urlopen(url, timeout=30) as reply:
                raw = reply.read()
                text = raw.decode('utf-8')
                title = re.search(r'<title>(.*?)</title>', text, re.S).group(1)
                rows.append({'url': url, 'status': reply.status, 'title': title, 'sha256': hashlib.sha256(raw).hexdigest()})
                print(reply.status, title)
        b08.save(label, {'references': rows})
        return
    script = {'prepare': 'wp/tests/preparer-image.ps1', 'regression': 'wp/tests/rejouer.ps1'}[kind]
    cmd = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', script]
    p = subprocess.run(cmd, cwd=b08.ROOT, capture_output=True, encoding='utf-8', errors='replace')
    text = p.stdout + p.stderr
    path = b08.PROOF / (label + '.log')
    assert not path.exists()
    path.write_text(text, encoding='utf-8')
    b08.save(label, {'command': cmd, 'exit': p.returncode, 'log': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'results': [json.loads(line[11:]) for line in text.splitlines() if line.startswith('T01_RESULT ')]})
    print(text[-3500:])
    assert p.returncode == 0


if __name__ == '__main__':
    run(*sys.argv[1:])
