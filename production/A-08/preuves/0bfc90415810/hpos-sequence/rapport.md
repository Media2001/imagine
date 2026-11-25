# Répétition A-08

Statut : TERMINÉ — réception sans anomalie

## Passage 1

Durées cumulées dans ce passage (essais refusés inclus), hors attentes opérateur.

| Étape | Durée (s) | Résultat | Preuves relatives à cet état |
|---|---:|---|---|
| audit | 1.268 | OK | audit-1-receipt.json |
| avant | 1.727 | OK | avant-1-receipt.json |
| mise-a-jour | 81.157 | OK | mise-a-jour-1-receipt.json, mise-a-jour-2-receipt.json |
| nettoyage | 2.527 | OK | nettoyage-1-receipt.json |
| apres | 1.634 | OK | apres-1-receipt.json |
| comparaison | 0.043 | OK | comparaison-1-receipt.json |

Comparaison native du passage 1 : attendus : 4, anormaux : 0.

## Passage 2

Durées cumulées dans ce passage (essais refusés inclus), hors attentes opérateur.

| Étape | Durée (s) | Résultat | Preuves relatives à cet état |
|---|---:|---|---|
| audit | 1.456 | OK | audit-2-receipt.json |
| avant | 0.982 | OK | avant-2-receipt.json |
| mise-a-jour | 3.968 | OK | mise-a-jour-3-receipt.json |
| nettoyage | 0.480 | OK | nettoyage-2-receipt.json |
| apres | 1.016 | OK | apres-2-receipt.json |
| comparaison | 0.045 | OK | comparaison-2-receipt.json |

Comparaison native du passage 2 : attendus : 0, anormaux : 0.

À regarder : rapport.md ; maintenance non pilotée par A08 ; aucun GO implicite.
Les durées excluent les attentes opérateur. Aucun résultat ne vaut GO de mise en ligne.
Aucune valeur de base n’est reproduite ici. Les noms de ressources restent dans les preuves natives.
