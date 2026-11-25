# Répétition A-08

Statut : ARRÊT : précontrôle (A08_STATE_OR_PROOF_INVALID)

## Passage 1

Durées cumulées dans ce passage (essais refusés inclus), hors attentes opérateur.

| Étape | Durée (s) | Résultat | Preuves relatives à cet état |
|---|---:|---|---|
| audit | 1.061 | OK | audit-1-receipt.json |
| avant | 1.417 | OK | avant-1-receipt.json |
| mise-a-jour | 76.324 | OK | mise-a-jour-1-receipt.json, mise-a-jour-2-receipt.json |
| nettoyage | 2.133 | OK | nettoyage-1-receipt.json |
| apres | 1.453 | OK | apres-1-receipt.json |
| comparaison | 0.039 | OK | comparaison-1-receipt.json |

Comparaison native du passage 1 : attendus : 4, anormaux : 0.

## Passage 2

Durées cumulées dans ce passage (essais refusés inclus), hors attentes opérateur.

| Étape | Durée (s) | Résultat | Preuves relatives à cet état |
|---|---:|---|---|
| audit | 1.078 | OK | audit-2-receipt.json |
| avant | 0.761 | OK | avant-2-receipt.json |
| mise-a-jour | 3.626 | OK | mise-a-jour-3-receipt.json |
| nettoyage | 0.435 | OK | nettoyage-2-receipt.json |
| apres | 0.781 | OK | apres-2-receipt.json |
| comparaison | 0.040 | OK | comparaison-2-receipt.json |

Comparaison native du passage 2 : attendus : 0, anormaux : 0.

À regarder : etat.json, entrées et preuves ; ne supprimer ni checkpoints ni verrous.
Les durées excluent les attentes opérateur. Aucun résultat ne vaut GO de mise en ligne.
Aucune valeur de base n’est reproduite ici. Les noms de ressources restent dans les preuves natives.
