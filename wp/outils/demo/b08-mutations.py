"""Mutants du vrai code B08 dans les seules copies jetables hors réseau."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import re
import subprocess
from pathlib import Path
import b08
mutations = ['slash', 'https', 'don', 'parts', 'consentement', 'mail', 'http', 'prive', 'rest', 'public', 'export', 'effacement', 'lecture', 'nonce']
prefix = sys.argv[1] if len(sys.argv) > 1 else 'mutations'
results = []
for mutation in mutations:
    label = prefix + '-' + mutation
    p = subprocess.run([sys.executable, str(b08.ROOT / 'wp/outils/demo/b08-local.py'), label, mutation], capture_output=True, encoding='utf-8')
    text = p.stdout + p.stderr
    path = b08.PROOF / (label + '.log')
    assert path.is_file()
    match = re.search(r'tests="(\d+)" assertions="(\d+)" errors="(\d+)" failures="(\d+)"', text)
    assert match and int(match[3]) == 0 and int(match[4]) > 0 and p.returncode == 1, (mutation, text)
    results.append({'mutation': mutation, 'exit': p.returncode, 'tests': int(match[1]), 'assertions': int(match[2]), 'errors': int(match[3]), 'failures': int(match[4]), 'log': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    print(mutation, 'DETECTEE', match[4])
b08.save(prefix, {'results': results})
