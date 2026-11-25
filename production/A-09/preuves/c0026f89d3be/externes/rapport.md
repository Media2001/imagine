# Test des redirections — lecture seule

0 CONFORME ; 4 non conforme(s).

| Ligne | Ancienne | Cible attendue | Résultat |
|---|---|---|---|
| 2 | /externe | /final | cible_externe |
| 3 | /plus-tard | /hop | cible_non_200 |
| 4 | /protocole | /final | cible_externe |
| 5 | /schema | /final | redirection_invalide |
