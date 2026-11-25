# Test des redirections — lecture seule

0 CONFORME ; 4 non conforme(s).

| Ligne | Ancienne | Cible attendue | Résultat |
|---|---|---|---|
| 2 | /chaine | /final | mauvaise_cible, chaine |
| 3 | /boucle | /boucle-b | chaine, boucle |
| 4 | /auto | /final | mauvaise_cible, boucle |
| 5 | /long0 | /final | mauvaise_cible, chaine, limite_sauts |
