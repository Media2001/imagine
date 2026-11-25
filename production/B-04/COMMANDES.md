# B-04 — Rejeu ciblé

Depuis `C:/Users/Ced/imagine`, en bash :

```bash
QA='C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe'
"$QA" wp/tests/demo/b04-work.py php relecture-parent
"$QA" wp/tests/demo/b04-http.py relecture-parent
"$QA" wp/tests/demo/b04-catalogue-test.py relecture-parent
"$QA" wp/tests/demo/b04-fixture-test.py relecture-parent
"$QA" wp/tests/demo/b04-safety.py
"$QA" wp/tests/demo/b04-preservation.py relecture-parent
```

Ces lectures ne changent aucun droit. Les sessions et les deux dates d’activité natives des visiteurs sont des effets normaux documentés, pas des fixtures restaurées. `b04-preservation.py` compare les 146 objets préexistants au gel avant B04 et ne normalise en mémoire que les deux valeurs exactes d’activité prouvées dans `native-activity-reconciliation.json`.

## Prérequis fictifs propres B04

```bash
"$QA" wp/outils/demo/b04.py inspect relecture-parent
"$QA" wp/outils/demo/b04.py product produit-rejoue
"$QA" wp/tests/demo/b04-queries.py
```

- `product` crée uniquement le produit propre marqué B04 s’il manque ; sinon réutilise son ID, sans modifier 271. Contrôles de statut/prix/association dans `b04-fixture-test.py`.
- `b04-queries.py` crée/rejoue vingt vrais articles et leur numéro propre, mesure le SQL par vrais GET sous les trois visiteurs, puis supprime dans `finally` les 21 IDs exacts et son seul contrôleur HTTP. Pas de requêtes SQL exportées. Aucun compte, commande ou droit créé. Le total inclut le bootstrap ; le sous-total commence à la fin de `template_redirect`.
- Reprise manuelle d’un témoin interrompu : `"$QA" wp/outils/demo/b04.py cleanup-witness nettoyage-propre`. Refus si une propriété exacte ne correspond plus. Pas de suppression par préfixe de titre.

## Suite complète

```bash
"$QA" wp/tests/demo/b04-final.py
```

Lancer ce pilote comme **processus suivi en arrière-plan** avec le tool terminal : les huit étapes PHP/HTTP peuvent dépasser la limite foreground de 420 secondes. Attendre son vrai statut de sortie. Après une interruption survenue **après les huit logs verts** et sans changement des sources ni du thème, `b04-final.py --resume` vérifie les dates et les empreintes puis termine navigateur, préservation et agrégation, sans rejouer les créations/nettoyages déjà réussis.

Le Python QA 3.14 demandé sert aux tests principaux. Pour le navigateur seulement, le pilote réutilise le Python Hermes 3.11 et Playwright déjà installés : le QA venv n’a pas ce paquet ; aucune installation ni modification d’environnement partagée. L’ajout au `sys.path` ne fournit que les dépendances HTML pures du venv QA.

`wp/tests/preparer-image.ps1` a été exécuté, sortie 0 : `preparer-image-resume.log`. Le thème n’est pas un paquet Composer ; ses tests B04 sont donc exécutés explicitement ici, pas prétendus découverts par T01.

## Rouge → vert et limites des archives

- `php-resume-red.json` → `php-resume-status-green.json` : helper absent puis 11 contrôles.
- `http-resume-issue-red.json` → `http-final.json` : sommaire, CTA et PDF, puis suivi des articles.
- `fixture-product-red.json` → `fixture-product-green.json` : prérequis produit absent puis produit natif 2475.
- `catalogue-red.json` → `catalogue-final.json` : statuts, thématiques, vraie destination produit, pagination.
- `witness-red.json` → `witness-green.json`, `queries-20.json` : absence puis vingt objets distincts réellement servis et mesurés.
- `undated-red.json` et l’essai intermédiaire n’étaient pas un défaut B04 : le modèle B01 interdit déjà de publier sans date. Le code expérimental a été retiré ; `undated-native-guard-final.json` vérifie le brouillon et son absence du public.
- `preservation-resume-after.json` conserve l’écart brut ; la réconciliation exacte des deux `wc_last_active` ne réécrit aucune donnée.

Les scripts de l’ancien arrêt (`b04-arreter.py`, `b04-inventaire.py`), les reçus rouges et `catalogue-candidat.php` sont **historiques**, pas des commandes de livraison à rejouer. Aucun reset C09/C14/C15, aucune restauration globale de B03 et aucun déploiement de plugin ne sont nécessaires.
