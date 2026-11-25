# Test des redirections — lecture seule

5 CONFORME ; 0 non conforme(s).

| Ligne | Ancienne | Code attendu | Code observé | Cible attendue | Cible observée | HTTP final | Sauts | Résultat |
|---|---|---|---|---|---|---|---|---|
| 2 | /old0 | 301 | 301 | /new0?n=1 | new0?n=1 | 200 | 1 | CONFORME |
| 3 | /old1 | 302 | 302 | /new1?n=1 | http://127.0.0.1:40739/new1?n=1 | 200 | 1 | CONFORME |
| 4 | /old2 | 303 | 303 | /new2?n=1 | new2?n=1 | 200 | 1 | CONFORME |
| 5 | /old3 | 307 | 307 | /new3?n=1 | http://127.0.0.1:40739/new3?n=1 | 200 | 1 | CONFORME |
| 6 | /old4 | 308 | 308 | /new4?n=1 | new4?n=1 | 200 | 1 | CONFORME |
