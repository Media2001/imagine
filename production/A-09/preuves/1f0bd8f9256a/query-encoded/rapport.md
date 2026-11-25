# Test des redirections — lecture seule

3 CONFORME ; 0 non conforme(s).

| Ligne | Ancienne | Code attendu | Code observé | Cible attendue | Cible observée | HTTP final | Sauts | Résultat |
|---|---|---|---|---|---|---|---|---|
| 2 | /ancien?u=%2Fpage | 301 | 301 | /nouveau0?u=%2Fpage | /nouveau0?u=%2Fpage | 200 | 1 | CONFORME |
| 3 | /x?q=deux%20mots | 301 | 301 | /nouveau1?q=deux%20mots | /nouveau1?q=deux%20mots | 200 | 1 | CONFORME |
| 4 | /trois?u=%2fpage&amp;x=%61%5c%3f%23 | 301 | 301 | /nouveau2?u=%2fpage&amp;x=%61%5c%3f%23 | /nouveau2?u=%2fpage&amp;x=%61%5c%3f%23 | 200 | 1 | CONFORME |
