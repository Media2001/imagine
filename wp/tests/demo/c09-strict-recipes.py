"""Rejoue les recettes strictes sans déployer ni écrire les rendus des autres lots."""
from pathlib import Path
from datetime import datetime, timezone
import json
import sys
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c13
import b02

ROOT = c13.ROOT
PROOF = ROOT / 'production/C-09'
original_write = Path.write_text


def redirected_write(self, data, *args, **kwargs):
    if self == ROOT / 'production/C-13/resultats.json':
        self = PROOF / 'complement-c13-strict.json'
    if ROOT / 'production/B-02' in self.parents:
        self = PROOF / ('complement-b02-' + self.name)
    return original_write(self, data, *args, **kwargs)


def run(lot):
    outcome = {'lot': lot, 'at': datetime.now(timezone.utc).isoformat(), 'deploy': False}
    try:
        with patch.object(Path, 'write_text', redirected_write):
            if lot == 'C13':
                c13.run(deploy=False, php_only=False, require_complete=True)
            elif lot == 'B02':
                result = b02.run(deploy=False, http=True)
                if result['acceptance_blockers']:
                    raise SystemExit(2)
            else:
                raise ValueError(lot)
        outcome['exit'] = 0
    except SystemExit as error:
        outcome['exit'] = error.code
    except Exception as error:
        outcome.update(exit=1, error=str(error))
    original_write(PROOF / ('complement-' + lot.lower() + '-exit.json'), json.dumps(outcome, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(outcome, ensure_ascii=False), flush=True)
    return outcome


if __name__ == '__main__':
    raise SystemExit(run(sys.argv[1])['exit'])
