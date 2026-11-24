"""Temporary conservative PHP line wrapper, followed by PHPCBF and real tests."""
import pathlib
import textwrap
ROOT = pathlib.Path(__file__).resolve().parents[2]
files = [ROOT / 'outils/bascule/non-regression', ROOT / 'outils/bascule/comparer'] + list((ROOT / 'outils/bascule/a03').glob('*.php')) + list(pathlib.Path(__file__).parent.glob('*.php'))
for file in files:
    output = []
    for original in file.read_text().splitlines():
        line = original
        indent = len(line) - len(line.lstrip())
        if line.lstrip().startswith('//') and len(line) > 120:
            output.extend(textwrap.wrap(line.strip()[3:], width=110-indent, initial_indent=' '*indent+'// ', subsequent_indent=' '*indent+'// '))
            continue
        for _ in range(20):
            if len(line) <= 120:
                break
            quote = None
            start = 0
            escape = False
            breaks = []
            strings = []
            for i, char in enumerate(line):
                if quote:
                    if escape:
                        escape = False
                    elif char == '\\':
                        escape = True
                    elif char == quote:
                        strings.append((start, i, quote))
                        quote = None
                    continue
                if char in ('\"', "'"):
                    quote = char
                    start = i
                elif char == ',':
                    breaks.append(i+1)
                elif any(line.startswith(op, i) for op in [' && ', ' || ', ' . ', ' => ']):
                    breaks.append(i)
            choices = [i for i in breaks if indent+10 < i <= 110]
            if choices:
                cut = max(choices)
                output.append(line[:cut].rstrip())
                line = ' '*(indent+4)+line[cut:].lstrip()
                continue
            long = next(((a,b,q) for a,b,q in strings if b-a > 90), None)
            if long:
                a,b,q = long
                cuts = [i for i in range(a+20, min(b,a+85)) if line[i]==' ']
                if cuts:
                    cut = max(cuts)
                    output.append(line[:cut]+q+' .')
                    line = ' '*(indent+4)+q+line[cut:]
                    continue
            break
        output.append(line)
    file.write_text('\n'.join(output)+'\n')
print('Wrapped only A03-owned PHP files.')
