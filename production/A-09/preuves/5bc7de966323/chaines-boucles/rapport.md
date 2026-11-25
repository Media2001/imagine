# Test des redirections — lecture seule

0 CONFORME ; 4 non conforme(s).

| Ligne | Ancienne | Code attendu | Code observé | Cible attendue | Cible observée | HTTP final | Sauts | Résultat |
|---|---|---|---|---|---|---|---|---|
| 2 | /chaine | 301 | 301 | /final | /intermediaire | 200 | 2 | mauvaise_cible, chaine |
| 3 | /boucle | 301 | 301 | /boucle-b | /boucle-b | — | 2 | chaine, boucle |
| 4 | /auto | 301 | 301 | /final | /auto | — | 1 | mauvaise_cible, boucle |
| 5 | /long0 | 301 | 301 | /final | /long1 | — | 9 | mauvaise_cible, chaine, limite_sauts |
