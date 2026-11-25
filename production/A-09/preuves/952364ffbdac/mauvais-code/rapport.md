# Test des redirections — lecture seule

1 CONFORME ; 1 non conforme(s).

| Ligne | Ancienne | Code attendu | Code observé | Cible attendue | Cible observée | HTTP final | Sauts | Résultat |
|---|---|---|---|---|---|---|---|---|
| 2 | /depart | 301 | 302 | /attendu | /attendu | 200 | 1 | mauvais_code |
| 3 | /ok | 301 | 301 | /fin | /fin | 200 | 1 | CONFORME |
