#!/usr/bin/env python3
"""Mandatory A21 Linux confinement; reuse the unchanged A12 Landlock engine."""
import importlib.util
import os
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def main():
    options={}
    for arg in sys.argv[1:]:
        key,sep,value=arg.partition('=')
        if not sep or not value or key not in {'--wp-path','--output','--audit','--as-of'} or key in options:
            raise RuntimeError('A21_USAGE')
        options[key]=value
    if not {'--wp-path','--output','--audit'}.issubset(options):
        raise RuntimeError('A21_USAGE')
    spec=importlib.util.spec_from_file_location('a12_fence',HERE.parent/'a12/confine.py')
    fence=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fence)
    site=Path(options['--wp-path']).resolve(strict=True)
    parent=Path(options['--output']).parent.resolve(strict=True)
    candidate=HERE.parents[3] if len(HERE.parents)>3 else HERE.parent
    repo=candidate if (candidate/'wp/outils/bascule/audit').is_file() else HERE.parent
    if not fence.disjoint_output(parent,site,repo):
        raise RuntimeError('A21_OUTPUT_UNSAFE')
    fence.confine(parent)
    os.environ['A21_CONFINED']='1'
    os.execvp('php',['php','-d','display_errors=0','-d','log_errors=0','-d','disable_functions=mail,exec,shell_exec,system,passthru,popen,proc_open,pcntl_exec',str(HERE/'inventorier-portes'),*sys.argv[1:]])
if __name__=='__main__':
    try:
        main()
    except Exception as error:
        code=str(error) if isinstance(error,RuntimeError) and str(error) in {'A21_USAGE','A21_OUTPUT_UNSAFE'} else 'A21_CONFINEMENT_FAILED'
        print(code,file=sys.stderr)
        sys.exit(1)
