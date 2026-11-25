# Répétition A-08

Statut : attente opérateur avant apres

| Étape | Durée (s) | Résultat | Preuves relatives à cet état |
|---|---:|---|---|
| audit | 2.451 | OK | audit-1-receipt.json, audit-2-receipt.json |
| avant | 2.624 | OK | avant-1-receipt.json, avant-2-receipt.json |
| mise-a-jour | 82.212 | OK | mise-a-jour-1-receipt.json, mise-a-jour-2-receipt.json, mise-a-jour-3-receipt.json |
| nettoyage | 2.630 | OK | nettoyage-1-receipt.json, nettoyage-2-receipt.json |
| apres | 1.399 | arrêt code 0 | apres-1-receipt.json |
| comparaison | 0.038 | arrêt code 3 | comparaison-1-receipt.json |

À regarder : repetition.md : réception isolée, compte SELECT ; puis --reception-ready.
Les durées excluent les attentes opérateur. Aucun résultat ne vaut GO de mise en ligne.
Aucune valeur de base n’est reproduite ici. Les noms de ressources restent dans les preuves natives.
