"""Format only the C-06 PHP paths, inside the already owned runner."""
import io
import json
import sys
import tarfile

sys.dont_write_bytecode = True
from run import bench

name = json.loads(bench.STATE.read_text(encoding='utf-8'))['container']
assert not bench.info(name)['NetworkSettings']['Networks']
data, _ = bench.payload()
bench.call(['exec', name, 'rm', '-rf', '/work/src/Acces', '/work/tests/Acces'])
bench.call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/work'], data)
result = bench.call(['exec', '-w', '/work', name, 'php', 'vendor/bin/phpcbf',
                     '--standard=PSR12', 'src/Acces', 'tests/Acces'], check=False)
print((result.stdout + result.stderr).decode(errors='replace'))
assert result.returncode in (0, 1)
archive = bench.call(['exec', '-w', '/work', name, 'tar', '-cf', '-', 'src/Acces', 'tests/Acces']).stdout
with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
    for member in bundle:
        if member.isfile():
            assert member.name.startswith(('src/Acces/', 'tests/Acces/')) and '..' not in member.name
            (bench.PLUGIN / member.name).write_bytes(bundle.extractfile(member).read())
