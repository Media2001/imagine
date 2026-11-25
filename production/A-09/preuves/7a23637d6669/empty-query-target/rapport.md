# Test des redirections — lecture seule

1 CONFORME ; 1 non conforme(s).

| Ligne | Ancienne | Code attendu | Code observé | Cible attendue | Cible observée | HTTP final | Sauts | Résultat |
|---|---|---|---|---|---|---|---|---|
| 2 | /ok | 301 | 301 | /fin | /fin | 200 | 1 | CONFORME |
| 3 | /a | 301 | 301 | /b? | /b | 200 | 1 | mauvaise_cible |
