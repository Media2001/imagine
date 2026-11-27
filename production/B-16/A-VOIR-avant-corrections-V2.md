# B-16 — à ouvrir sur la démo fictive uniquement

Base : `http://192.168.129.32:8085`.

- `/demo-2026-t1-reserve-1/` : anonyme = titre, résumé éditorial, thématique, numéro et extrait/paywall ; A-PAPIER = texte complet, sans appel final ; P-NUMERO = texte complet puis appel final vers la même destination que « S'abonner » du menu.
- `/demo-2026-t1-ouvert/` : libre pour tous ; appel final pour anonyme et acheteur, pas pour A-PAPIER.
- `/c08-article-reserve-automatique/` : résumé vide = aucun résumé ajouté, pas de signature par défaut.
- Éditeur d'article : extrait natif = résumé public, étiquettes = mots-clés ; boîte « Signature publique » = nom signé sans lien ni adresse. Vide, aucun paragraphe. Les essais temporaires signature/mots-clés et numéro manquant sont restaurés ; aucune signature inventée ne reste sur la démo.
- Mode lecture : l'en-tête entier et l'appel final disparaissent via le marqueur B03 existant. Corps C08 et médias B11 conservés.

Capture de la vraie réponse anonyme, pendant les champs fictifs temporaires : `browser-final5-V2.png`. Vérifier le visuel avec les maquettes quand elles arriveront ; aucun design livré ici.

Commandes :
```
python -B production/B-16/verifier.py
python -B production/B-16/verifier.py --live
python -B production/B-13/qualifier.py B-16
```

Preuves : 10 contrôles natifs, 79 contrôles sur 9 réponses (anonyme/A-PAPIER/P-NUMERO × réservé/libre/vide), mutation C26 refusée, mode lecture CSS existant, 23 contrôles complémentaires B11. Données et sessions restaurées et relues. Pas de nouvelle matrice C26. Limite héritée : les lecteurs historiques B01/B11 ne sont pas rescellés ; le complément B11 de ce lot est distinct. Le premier rejeu T01 a trouvé un test lisant le thème absent de sa copie isolée ; test ramené au contrat pur, vérifications du vrai thème faites par navigateur.
