# Test des redirections — lecture seule

0 CONFORME ; 4 non conforme(s).

| Ligne | Ancienne | Code attendu | Code observé | Cible attendue | Cible observée | HTTP final | Sauts | Résultat |
|---|---|---|---|---|---|---|---|---|
| 2 | /externe | 301 | 301 | /final | http://127.0.0.1:37913/never-visit | — | 1 | cible_externe |
| 3 | /plus-tard | 301 | 301 | /hop | /hop | — | 2 | chaine, cible_externe |
| 4 | /protocole | 301 | 301 | /final | //127.0.0.1:37913/never-visit | — | 1 | cible_externe |
| 5 | /schema | 301 | 301 | /final | mailto:nobody@example.org | — | 1 | cible_externe |
