#!/usr/bin/env python3
"""Mandatory confined A20 launcher; no WordPress bootstrap in Python."""
import importlib.util
import os
from pathlib import Path
import sys
import json
import shutil
import subprocess
import tempfile
import re
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
REFUSALS=frozenset('''A02_AUDIT_FAILED A02_CONFIG_NON_LITERAL A02_DB_HOST_UNSUPPORTED A02_DB_NAME_UNSUPPORTED
A02_EXPECTED_TABLE_MISSING A02_FILE_TREE_LIMIT A02_FILE_UNREADABLE_OR_TOO_LARGE A02_LOG_UNREADABLE
A02_MULTISITE_UNSUPPORTED A02_NON_SELECT_FORBIDDEN A02_OUTPUT_CREATE_FAILED A02_OUTPUT_UNSAFE_OR_EXISTS
A02_OUTPUT_WRITE_FAILED A02_PATH_INVALID A02_RUNTIME_WARNING A02_SERIALIZED_TOO_LARGE
A02_SYMLINK_UNSUPPORTED A02_TABLE_IDENTIFIER_UNSUPPORTED A02_USAGE A11_ATTACHMENT_PARENT_CYCLE
A11_AUDIT_GUARD A11_CONFIG_OVERRIDE_UNSUPPORTED A11_CONFIG_UNSAFE A11_DROPIN_UNSUPPORTED A11_HOME_INVALID
A11_MULTISITE_UNSUPPORTED A11_NATIVE_URL_MISSING A11_OUTPUT_CREATE A11_OUTPUT_EXISTS A11_OUTPUT_UNSAFE
A11_OUTPUT_WRITE A11_PATH_INVALID A11_POSTS_FAILED A11_POST_READ_FAILED A11_READONLY_TRANSACTION_FAILED
A11_READ_FAILED A11_SYMLINK_UNSUPPORTED A11_TERMS_FAILED A11_USAGE A11_WRITE_FORBIDDEN
A12_ATTACHMENT_PATH_UNSAFE A12_AUDIT_GUARD A12_AUDIT_LIBRARY_GUARD A12_AUDIT_STORAGE_MISMATCH
A12_CONFIG_UNSAFE A12_CONFINED A12_CONFINEMENT_REQUIRED A12_DUPLICATE_ATTACHED_FILE
A12_MULTISITE_UNSUPPORTED A12_OUTPUT_CREATE A12_OUTPUT_EXISTS A12_OUTPUT_UNSAFE A12_OUTPUT_WRITE
A12_PATH_INVALID A12_READ_FAILED A12_SELECT_ONLY A12_TABLE_MISSING A12_TRANSACTIONAL_TABLES_REQUIRED
A12_UPLOAD_PATH_UNSUPPORTED A12_USAGE A20_AUDIT_GUARD A20_AUDIT_STORAGE_MISMATCH A20_DATA_UNSUPPORTED
A20_CONFINED A20_CONFINEMENT_REQUIRED A20_INVENTORY_FAILED A20_NATIVE_API_UNAVAILABLE
A20_OUTPUT_CREATE A20_OUTPUT_EXISTS A20_OUTPUT_UNSAFE A20_OUTPUT_WRITE A20_QUERY_FAILED
A20_RUNTIME_WARNING A20_USAGE'''.split())
DROPINS=('wp-content/db.php','wp-content/object-cache.php','wp-content/advanced-cache.php',
    'wp-content/sunrise.php','wordfence-waf.php','.user.ini')

def closed_refusal(result):
    allowed={(code+'\n').encode():(code) for code in REFUSALS}
    allowed.update({('A11_DROPIN_UNSUPPORTED '+json.dumps({'file':name},separators=(',',':'))+'\n').encode():
        'A11_DROPIN_UNSUPPORTED '+json.dumps({'file':name},separators=(',',':')) for name in DROPINS})
    if result.returncode==1 and result.stdout==b'' and result.stderr in allowed:
        return allowed[result.stderr]
    return 'A20_PROCESS_OUTPUT_INVALID'

def main():
    o={}
    for arg in sys.argv[1:]:
        key,sep,value=arg.partition('=')
        if not sep or not value or key not in {'--wp-path','--output','--audit'} or key in o:raise RuntimeError('A20_USAGE')
        o[key]=value
    if not {'--wp-path','--output','--audit'}.issubset(o):raise RuntimeError('A20_USAGE')
    spec=importlib.util.spec_from_file_location('a12_fence',HERE.parent/'a12/confine.py');a12=importlib.util.module_from_spec(spec);spec.loader.exec_module(a12)
    site=Path(o['--wp-path']).resolve(strict=True);parent=Path(o['--output']).parent.resolve(strict=True)
    candidate=HERE.parents[3] if len(HERE.parents)>3 else HERE.parent
    repo=candidate if (candidate/'wp/outils/bascule/audit').is_file() else HERE.parent
    if not a12.disjoint_output(parent,site,repo):raise RuntimeError('A20_OUTPUT_UNSAFE')
    out=parent/Path(o['--output']).name
    if out.exists() or out.is_symlink():raise RuntimeError('A20_OUTPUT_EXISTS')
    audit=Path(o['--audit'])
    if audit.is_symlink() or not audit.is_file() or audit.stat().st_size>16777216 or audit.resolve().parent.parent!=parent:raise RuntimeError('A20_AUDIT_GUARD')
    a12.confine(parent);os.environ['A20_CONFINED']='1'
    # The outer process owns publication. Never preserve raw PHP streams or a partial report.
    with tempfile.TemporaryDirectory(prefix='.a20-',dir=parent) as temporary:
        stage=Path(temporary);os.chmod(stage,0o700)
        (stage/'audit').mkdir(mode=0o700)
        staged_audit=stage/'audit/audit.json';shutil.copyfile(audit,staged_audit)
        staged_out=stage/'result'
        args=['--wp-path='+str(site),'--audit='+str(staged_audit),'--output='+str(staged_out)]
        result=subprocess.run(['php','-d','display_errors=0','-d','log_errors=0','-d','disable_functions=mail,exec,shell_exec,system,passthru,popen,proc_open,pcntl_exec',str(HERE/'inventorier-tarifs'),*args],capture_output=True)
        # run() waits for termination and both pipe EOFs, including shutdown callbacks.
        if result.returncode!=0 or result.stdout!=b'A20_OK tarifs.json tarifs.md\n' or result.stderr:
            message=closed_refusal(result)
            raise RuntimeError(message)
        spec=importlib.util.spec_from_file_location('a20_report',HERE/'report.py')
        validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
        validator.validate(staged_out,audit)
        staged_out.rename(out)
    print('A20_OK tarifs.json tarifs.md')
if __name__=='__main__':
    try:main()
    except Exception as error:
        import re
        code=str(error) if isinstance(error,RuntimeError) and (str(error) in REFUSALS | {'A20_CONFINEMENT_FAILED','A20_PROCESS_OUTPUT_INVALID','A20_REPORT_INVALID','A12_OUTPUT_UNSAFE','A12_DISCONNECTED_LINUX_REQUIRED','A12_LANDLOCK_ARCH_UNSUPPORTED','A12_LANDLOCK_ABI_REQUIRED','A12_LANDLOCK_CREATE_FAILED','A12_LANDLOCK_RULE_FAILED','A12_LANDLOCK_RESTRICT_FAILED'} or str(error) in {'A11_DROPIN_UNSUPPORTED '+json.dumps({'file':name},separators=(',',':')) for name in DROPINS}) else 'A20_CONFINEMENT_FAILED'
        print(code,file=sys.stderr);sys.exit(1)
