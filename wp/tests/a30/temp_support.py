"""Single temporary-directory policy for A30's Python-only fixtures.

TMPDIR is an optional explicit override. Without it, Python selects its standard
Windows TEMP/TMP directory. The matrix supplies an authorized Hermes scratch
TEMP/TMP in each fresh process; no repository fixture is ever allocated.
"""
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[3]


def assert_outside_repo(directory, *, repo=ROOT):
    path = Path(directory).resolve()
    if path.is_relative_to(Path(repo).resolve()):
        raise RuntimeError('A30_TEST_TEMP_IN_REPOSITORY')
    return path


def temporary_directory(prefix, *, repo=ROOT):
    base = assert_outside_repo(os.environ.get('TMPDIR') or tempfile.gettempdir(), repo=repo)
    temporary = tempfile.TemporaryDirectory(prefix=prefix, dir=base)
    try:
        assert_outside_repo(temporary.name, repo=repo)
    except Exception:
        temporary.cleanup()
        raise
    return temporary
