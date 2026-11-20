#!/usr/bin/python3
import os
import sys
from runtime import main

stage = os.path.basename(sys.argv[0])
if stage == 'worker-bridge' and len(sys.argv) == 4 and sys.argv[1] == '--stage':
    stage = sys.argv[2]
    del sys.argv[1:3]
if stage not in ('importer','neutraliser','anonymiser','verifier','bascule','novamira'):
    raise SystemExit(78)
raise SystemExit(main(stage))
