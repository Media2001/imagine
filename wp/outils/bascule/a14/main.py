"""A14 CSV reader: reuse the unchanged A13 decoder/strict CSV parser."""
import importlib.util
import importlib.machinery
import json
import os
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def load(name,path):
    loader=importlib.machinery.SourceFileLoader(name,str(path))
    spec=importlib.util.spec_from_loader(name,loader)
    m=importlib.util.module_from_spec(spec);loader.exec_module(m);return m


def read_contacts(source,mapping):
    a13=load('a13_csv',HERE.parent/'controler-export')
    try:
        if source.stat().st_size>16777216 or mapping.stat().st_size>65536:
            raise RuntimeError('A14_INPUT_LIMIT')
        c=json.loads(mapping.read_text(encoding='utf-8-sig'),object_pairs_hook=a13.objet_unique)
        if (set(c)!={'version','encodage','separateur','colonnes','statuts'} or type(c['version']) is not int or c['version']!=1
            or c['encodage'] not in ('auto','utf-8','utf-8-sig','utf-16','cp1252','iso-8859-1')
            or c['separateur'] not in ('auto',*a13.SEPARATORS)
            or set(c['colonnes'])!={'email','statut'} or len(set(c['colonnes'].values()))!=2
            or any(not isinstance(v,str) or not v.strip() for v in c['colonnes'].values())
            or set(c['statuts'])!={'inscrit','desinscrit','bloque'}):
            raise RuntimeError('A14_MAPPING_INVALID')
        statuses={}
        for status,values in c['statuts'].items():
            if not isinstance(values,list) or not values:raise RuntimeError('A14_MAPPING_INVALID')
            for value in values:
                if not isinstance(value,str) or not value.strip() or value.strip().casefold() in statuses:
                    raise RuntimeError('A14_MAPPING_INVALID')
                statuses[value.strip().casefold()]=status
        text,_=a13.decoder(source.read_bytes(),c['encodage'])
        records,_=a13.lire_csv(text,c['separateur'])
        header=records[0][1]
        if not all(x in header for x in c['colonnes'].values()):raise RuntimeError('A14_MAPPING_INVALID')
        email=header.index(c['colonnes']['email']);status=header.index(c['colonnes']['statut'])
        return [{'line':line,'email':row[email],'status':statuses.get(row[status].strip().casefold(),'inconnu')} for line,row in records[1:]]
    except (a13.Refus,ValueError,KeyError,TypeError,OSError):
        raise RuntimeError('A14_INPUT_INVALID') from None


def main(argv=None):
    options={}
    for arg in (sys.argv[1:] if argv is None else argv):
        key,sep,value=arg.partition('=')
        if not sep or not value or key not in {'--wp-path','--output','--audit','--contacts','--correspondance'} or key in options:
            raise RuntimeError('A14_USAGE')
        options[key]=value
    if len(options)!=5:raise RuntimeError('A14_USAGE')
    site=Path(options['--wp-path']).resolve(strict=True)
    parent=Path(options['--output']).parent.resolve(strict=True)
    candidate=HERE.parents[3] if len(HERE.parents)>3 else HERE.parent
    repo=candidate if (candidate/'wp/outils/bascule/audit').is_file() else HERE.parent
    a12=load('a12_fence',HERE.parent/'a12/confine.py')
    if not a12.disjoint_output(parent,site,repo):raise RuntimeError('A14_OUTPUT_UNSAFE')
    inputs=[Path(options[k]).resolve(strict=True) for k in ('--contacts','--correspondance')]
    if any(p==parent or parent in p.parents for p in inputs):raise RuntimeError('A14_INPUT_OUTPUT_OVERLAP')
    rows=read_contacts(*inputs)
    guard=load('stream_guard',HERE.parent/'stream_guard.py')
    return guard.inventory('A14',HERE/'command.php',
        {key:options[key] for key in ('--wp-path','--output','--audit')},
        fence=a12,input_data=json.dumps(rows).encode('utf-8'))


def cli():
    try:return main()
    except Exception as error:
        guard=load('stream_guard',HERE.parent/'stream_guard.py')
        code=guard.public_error(error,'A14')
        print(code,file=sys.stderr);return 1
