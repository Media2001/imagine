#!/usr/bin/env python3
"""Mandatory confined A16 launcher; no WordPress bootstrap in Python."""
import importlib.util
import os
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def main():
    o={}
    for arg in sys.argv[1:]:
        key,sep,value=arg.partition('=')
        if not sep or not value or key not in {'--wp-path','--output','--audit','--correspondance','--limit'} or key in o:raise RuntimeError('A16_USAGE')
        o[key]=value
    if '--correspondance' not in o:raise RuntimeError('A16_MAPPING_REQUIRED')
    if not {'--wp-path','--output','--audit'}.issubset(o):raise RuntimeError('A16_USAGE')
    spec=importlib.util.spec_from_file_location('a12_fence',HERE.parent/'a12/confine.py');a12=importlib.util.module_from_spec(spec);spec.loader.exec_module(a12)
    site=Path(o['--wp-path']).resolve(strict=True);parent=Path(o['--output']).parent.resolve(strict=True)
    candidate=HERE.parents[3] if len(HERE.parents)>3 else HERE.parent
    repo=candidate if (candidate/'wp/outils/bascule/audit').is_file() else HERE.parent
    if not a12.disjoint_output(parent,site,repo):raise RuntimeError('A16_OUTPUT_UNSAFE')
    spec=importlib.util.spec_from_file_location('stream_guard',HERE.parent/'stream_guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    guard.inventory('A16',HERE/'inventorier-numeros',o,fence=a12)
if __name__=='__main__':
    try:main()
    except Exception as error:
        import re
        code=str(error) if isinstance(error,RuntimeError) and re.fullmatch(r'A(?:16|12)_[A-Z_]+',str(error)) else 'A16_CONFINEMENT_FAILED'
        print(code,file=sys.stderr);sys.exit(1)
