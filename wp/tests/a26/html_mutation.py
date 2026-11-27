"""Legacy HTML witness on the parent's disposable /subject copy only."""
from contextlib import contextmanager
import hashlib
from pathlib import Path

START = b'    public static function htmlUrls('
END = b'    public static function emptyCounts('
SUBJECT = Path('/subject/a26/Analysis.php')
LEGACY = Path('/opt/a26/html-regex-before.txt')


def replace_html_method(source, method):
    if source.count(START) != 1 or source.count(END) != 1:
        raise RuntimeError('A26_HTML_MUTATION_TARGET_INVALID')
    start, end = source.index(START), source.index(END)
    if end <= start or not method.startswith(START) or END in method:
        raise RuntimeError('A26_HTML_MUTATION_TARGET_INVALID')
    return source[:start] + method + source[end:]


@contextmanager
def legacy_html():
    # Never accept a caller-supplied host path. This is not a production fallback.
    if str(SUBJECT) != '/subject/a26/Analysis.php' or not Path('/opt/a26/inside.py').is_file():
        raise RuntimeError('A26_DISPOSABLE_SUBJECT_REQUIRED')
    original = SUBJECT.read_bytes()
    try:
        SUBJECT.write_bytes(replace_html_method(original, LEGACY.read_bytes()))
        yield hashlib.sha256(original).hexdigest()
    finally:
        SUBJECT.write_bytes(original)
        if SUBJECT.read_bytes() != original:
            raise RuntimeError('A26_HTML_SOURCE_NOT_RESTORED')
