1. Depuis PowerShell : `Set-Location C:\Users\Ced\imagine` ; prérequis : Python, WSL/Docker et outil de staging déjà présents ; aucune installation sur l’hôte.
2. Construire : `python wp/outils/demo/construire.py` ; seule cible `imagine-test-demo`, création normale autorisée avec Novamira puis garde MU sans email/HTTP/paiement, aucun compte ni licence commerciale.
3. Rejouer : `python wp/outils/demo/construire.py --preuve reconstruction` ; mêmes IDs, slugs, URL, contenus et médias vérifiés, aucun autre site ni outil modifié.
4. Tests : `python -m unittest discover -s wp/tests/demo -p "test_b00*.py" -v` puis `python wp/tests/demo/b00-verifier.py` ; identifiants générés dans `C:\Users\Ced\.imagine-demo\identifiants.json`, hors dépôt.
5. Ouvrir `production/B-00/A-VOIR.md` ; preuves JSON/HTTP ici ; interprétations, versions, sécurité et ancien blocage levé dans `production/B-00/verification.md`.
