"""Explicit syntax-only MySQL8 -> offline MariaDB adaptation; no row edits."""
import re
from archive import Refusal

COLLATIONS = {
    'utf8mb4_0900_ai_ci':'utf8mb4_unicode_520_ci',
    'utf8mb4_0900_as_ci':'utf8mb4_unicode_520_ci',
    'utf8mb4_0900_as_cs':'utf8mb4_bin',
    'utf8mb4_0900_bin':'utf8mb4_bin',
}
# Language-specific variants are deliberately not silently flattened.
MODES = frozenset(('ALLOW_INVALID_DATES ANSI_QUOTES ERROR_FOR_DIVISION_BY_ZERO HIGH_NOT_PRECEDENCE IGNORE_SPACE NO_AUTO_VALUE_ON_ZERO NO_BACKSLASH_ESCAPES NO_DIR_IN_CREATE NO_ENGINE_SUBSTITUTION NO_UNSIGNED_SUBTRACTION NO_ZERO_DATE NO_ZERO_IN_DATE ONLY_FULL_GROUP_BY PAD_CHAR_TO_FULL_LENGTH PIPES_AS_CONCAT REAL_AS_FLOAT STRICT_ALL_TABLES STRICT_TRANS_TABLES').split())


def compatible_tokens(tokens):
    converted, changes = [], []
    for kind, value in tokens:
        lower = value.lower()
        if kind == 'word' and lower in COLLATIONS:
            replacement = COLLATIONS[lower]
            changes.append({'from':lower,'to':replacement})
            value = replacement
        elif kind == 'word' and '_0900_' in lower:
            raise Refusal('SQL_COLLATION_UNSUPPORTED')
        converted.append((kind,value))
    return converted, changes


def unwrap_setting(payload):
    # Executable comments are allowed ONLY when the entire statement is a
    # closed safe SET. A version number never grants arbitrary execution.
    match = re.fullmatch(rb'\s*/\*![0-9]{5,6}\s+(SET\s+[^;]+?)\s*\*/\s*;\s*', payload, re.I|re.S)
    return match[1]+b';' if match else payload


def mode_statement(tokens):
    values = [v.upper() if k=='word' else v for k,v in tokens]
    if len(tokens)==4 and values[:3] == ['SET','SQL_MODE','='] and tokens[3][0]=='string':
        mode = tokens[3][1][1:-1]
        if not re.fullmatch(r'[A-Za-z_,]*', mode): raise Refusal('SQL_MODE_UNSUPPORTED')
        parts = mode.upper().split(',') if mode else []
        if any(p not in MODES for p in parts): raise Refusal('SQL_MODE_UNSUPPORTED')
        # Lexer only supports normal MySQL quoted literals; don't pretend to
        # import a different escaping grammar after changing these switches.
        if {'ANSI_QUOTES','NO_BACKSLASH_ESCAPES'} & set(parts): raise Refusal('SQL_MODE_UNSUPPORTED')
        return mode.upper()
    return None
