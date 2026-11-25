"""Exercise the same kernel fence for privileged fixture-only SQL probes."""
import os
import pathlib
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, '/subject/a12')
from confine import confine

abi = confine('/report')
# This file is created only by the test harness; not by third-party PHP.
pathlib.Path('/report/landlock-abi.txt').write_text(str(abi)+'\n')
os.environ['A12_CONFINED'] = '1'
os.execvp('php', ['php', '-d', 'display_errors=0', '-d', 'log_errors=0', '-d',
    'disable_functions=mail,exec,shell_exec,system,passthru,popen,proc_open,pcntl_exec',
    '/opt/a12/readonly-probe.php'])
