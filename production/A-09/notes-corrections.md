# A-09 — corrections fusion du 25 novembre 2026

## Résultat et décisions prises à défaut

- **R1** : chemin/requête validés séparément. Encodages licites de la requête conservés exactement, casse comprise, dans comparaison et GET ; contrôles encodés refusés, séparateurs/espaces encodés toujours refusés dans le chemin.
- **R2** : défaut prudent permis par la fusion : requête vide (`/a?`, cible `/b?`) refusant tout le plan avant GET, code 2 `A09_PLAN_EMPTY_QUERY`. Aucun conflit interrogé ni faux `mauvaise_cible`. Location à requête vide invalide, non suivie ; garde également dans le client.
- **R3** : ASCII intégral avant analyse du plan, origine et Location. > U+FFFF dans ancienne ou cible en fin de plan : refus global, zéro GET.
- Origine, marqueurs natifs A04/A05, octets exacts du MU et déclaration supplémentaire `.imagine-a09-http.json` inchangés. GET seulement, aucun WordPress ni SQL.
- Facultatif : mode d'emploi précisant que `mauvaise_cible` porte sur la première cible, même si la chaîne arrive finalement au bon endroit.

## Preuves

`preuves/a1671ceb23d2/` : **28 tests réussis, 0 échec** (21 existants + 7 nouveaux), 15 rapports HTTP. Piège autre origine vide, plans invalides zéro requête. HTTP loopback réel dans des runners Docker jetables owned A09 : network none, aucun montage/port exposé, capacités supprimées, no-new-privileges. Tous supprimés par nom exact après vérification du label ; absence relue, RED compris.

| Correction | RED réellement exécuté | GREEN |
|---|---|---|
| R1 | `5d086f34747b` | `1f0bd8f9256a` |
| R2 | `7a23637d6669` | `5aeae2f21554` |
| R3 | `0c8c40532852` | `e1ae232504e9` |

```text
python -B wp/tests/a09/run.py
python -B production/A-09/verifier.py
python -B production/A-09/verifier.py --replay
```

La commande dédiée est autorisée comme preuve A09 par l'instruction 4 de la fusion ; aucun succès global `rejouer.ps1` revendiqué. Aucun nouveau paquet ajouté : extension des tests A09 existants, donc pas de nouvelle préparation requise par la règle effective. Préparation historique conservée byte-identique.

## Baseline et historique

`avant-corrections/` préserve les anciens pointeurs/métadonnées byte-identiques. `historique-corrections.json` suit **722 fichiers historiques**, toutes les preuves présentes au début incluses. Les cinq dérives antérieures seules sont qualifiées dans `transition-corrections.json` :

- README A02 : retrait en mémoire des **deux lignes A10 exactes** rétablit le SHA-256 original `7314ab53dd50331d8f3e310215cda613954214c96b0df353981f4ebdac89db72`. Aucun changement du README, aucun masque large.
- Quatre fichiers A08 (`sequence.py`, `repetition.md`, `inside.py`, `test_sequence.py`) : SHA actuels confirmés par manifeste et sources de la preuve verte `0bfc90415810`, sans opération Git.

Baseline actuelle : **95 fichiers protégés**. Tous les autres SHA originaux sont maintenus ; outils acceptés hors scope inchangés. Le vérificateur contrôle encore historique, transition exacte, HTTP, cadence, origine, compteurs, cleanup, PRET/manifeste. File et correction A09 consultées liées par SHA au nouveau manifeste, pour détecter un retour de correction.

## Limites

Preuve technique fictive, pas un staging WordPress, pas de plan SEO réel, pas de GO production. Aucun compte, archive, donnée réelle, staging/démo ou Git. Verrous et lots voisins intouchés. Délai par opération socket, pas une échéance DNS globale ; TLS standard conservé, preuve demandée HTTP.
