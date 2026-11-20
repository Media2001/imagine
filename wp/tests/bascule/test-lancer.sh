#!/bin/sh
set -eu
src=$(dirname "$0")/../../outils/bascule/lancer
t=$(mktemp -d); trap 'rm -rf "$t"' EXIT
cp "$src" "$t/lancer"
printf '#!/bin/sh\nexit 0\n' > "$t/010-ok"
printf '#!/bin/sh\nexit 17\n' > "$t/020-stop"
printf '#!/bin/sh\nexit 0\n' > "$t/030-never"
chmod +x "$t"/0*
if bash "$t/lancer" 2>"$t/result"; then exit 1; else test "$?" -eq 17; fi
grep -q '^OK 010-ok$' "$t/result"; grep -q '^ECHEC 020-stop 17$' "$t/result"; ! grep -q 030 "$t/result"
