"""Small fail-closed PHP lexer: strings are atomic data, never source code."""
import re


def staging_declaration(source):
    """Recognize only a unique, standalone top-level literal define call.

    This does not execute PHP or attempt to understand computed declarations.
    Heredocs, backticks, inline HTML and namespaces are deliberately opaque.
    """
    if not source.startswith('<?php') or (len(source) > 5 and not source[5].isspace()):
        return False
    tokens = []
    i = 5
    while i < len(source):
        ch = source[i]
        if ch.isspace():
            i += 1
        elif source.startswith('/*', i):
            end = source.find('*/', i + 2)
            if end < 0:
                return False
            i = end + 2
        elif source.startswith('//', i) or ch == '#':
            if source.startswith('#[', i):
                return False
            end = re.search(r'[\r\n]', source[i:])
            end_at = len(source) if end is None else i + end.start()
            if '?>' in source[i:end_at]:
                return False
            i = end_at
        elif ch in "'\"":
            quote, start = ch, i + 1
            i += 1
            escaped = False
            while i < len(source) and source[i] != quote:
                if source[i] == '\\':
                    escaped = True
                    i += 2
                else:
                    i += 1
            if i >= len(source):
                return False
            value = source[start:i]
            # Only plain strings can supply literal define arguments.
            plain = not escaped and not (quote == '"' and ('$' in value or '{' in value))
            tokens.append(('string', value if plain else None))
            i += 1
        elif ch == '`' or source.startswith(('<<<', '<?', '?>'), i):
            return False
        else:
            match = re.match(r'[A-Za-z_][A-Za-z_0-9]*', source[i:])
            if match:
                value = match[0]
                if value.lower() == 'namespace':
                    return False
                tokens.append(('name', value))
                i += len(value)
            else:
                tokens.append(('symbol', ch))
                i += 1
    wanted = [('name', 'define'), ('symbol', '('), ('string', 'WP_ENVIRONMENT_TYPE'),
              ('symbol', ','), ('string', 'staging'), ('symbol', ')'), ('symbol', ';')]
    candidates = []
    depth = 0
    for index, token in enumerate(tokens):
        if token == ('name', 'define') or token == ('name', 'DEFINE'):
            fragment = tokens[index:index + len(wanted)]
            if fragment:
                fragment = [('name', fragment[0][1].lower())] + fragment[1:]
            if (fragment == wanted and depth == 0
                    and (index == 0 or tokens[index - 1] == ('symbol', ';'))):
                candidates.append(index + 2)
        if token[0] == 'symbol':
            if token[1] in '({[':
                depth += 1
            elif token[1] in ')}]':
                depth -= 1
            if depth < 0:
                return False
    references = [i for i, token in enumerate(tokens) if token[1] == 'WP_ENVIRONMENT_TYPE']
    return depth == 0 and len(candidates) == 1 and references == candidates
