#!/usr/bin/env python3
"""Mandatory confined A18 launcher; no WordPress bootstrap in Python."""
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
        if not sep or not value or key not in {'--wp-path','--output','--audit'} or key in o:raise RuntimeError('A18_USAGE')
        o[key]=value
    if not {'--wp-path','--output','--audit'}.issubset(o):raise RuntimeError('A18_USAGE')
    spec=importlib.util.spec_from_file_location('a12_fence',HERE.parent/'a12/confine.py');a12=importlib.util.module_from_spec(spec);spec.loader.exec_module(a12)
    site=Path(o['--wp-path']).resolve(strict=True);parent=Path(o['--output']).parent.resolve(strict=True)
    candidate=HERE.parents[3] if len(HERE.parents)>3 else HERE.parent
    repo=candidate if (candidate/'wp/outils/bascule/audit').is_file() else HERE.parent
    if not a12.disjoint_output(parent,site,repo):raise RuntimeError('A18_OUTPUT_UNSAFE')
    spec=importlib.util.spec_from_file_location('stream_guard',HERE.parent/'stream_guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    guard.inventory('A18',HERE/'inventorier-conservation',o,fence=a12)
if __name__=='__main__':
    try:main()
    except Exception as error:
        import re
        spec=importlib.util.spec_from_file_location('stream_guard',HERE.parent/'stream_guard.py')
        guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
        code=guard.public_error(error,'A18')
        print(code,file=sys.stderr);sys.exit(1)
