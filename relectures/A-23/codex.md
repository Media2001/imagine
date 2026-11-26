# Relecture indépendante — A-23

Date : 26 novembre 2026. Référentiel : `relecteurs/AGENTS.md`, doctrine, grille, brief A-23 et cahier des charges §4.3 (`docs/cahier-des-charges-v3.1.txt:1082`). Lecture du code A-23, de ses dépendances pertinentes, de l'anonymiseur et du paquet `production/A-23/preuves/final`. Le rapport de Claude n'a pas été lu.

## 1. Conformité

Les livrables demandés sont présents : inventaire, lanceur utilisant le gardien A-22, tests, dix lignes sur le standard WordPress, deux lignes intégrées au mode d'emploi partagé et PRET. Le code compte sans décider d'une reconnexion, d'une fusion ou d'une réactivation. Un seul paquet final est livré.

**P1 — Important — L'exclusion de l'administration n'applique pas entièrement la règle inclusive annoncée.** Fichier : `wp/outils/bascule/a23/Inventory.php:68`.

Le test porte sur trois noms de rôles fixes, puis sur les capacités finales de l'utilisateur (`allcaps`). Il ne recherche pas les rôles personnalisés de gestion dans les définitions des rôles, contrairement à A-17. Exemple fictif : le rôle `a23_operator` possède `read=true` et `edit_users=true`, mais son titulaire a une surcharge individuelle `edit_users=false`. A-17 classe toujours ce titulaire dans l'administration par son rôle (`wp/outils/bascule/a17/Inventory.php:69`, puis `:84`). A-23 le classe comme lecteur, car son rôle n'est pas dans les trois noms fixes et ses capacités finales ne comportent plus de capacité de gestion activée. Cela contredit aussi la définition du README A-23 : « Un compte ayant plusieurs rôles est exclu dès qu'un est de gestion. »

Conséquence : des comptes déjà compris dans l'administration d'A-17 entrent dans les totaux et anomalies des lecteurs, éventuellement dans les abonnés vivants et les comptes sans historique. Avec cinq comptes de ce type, une famille d'empreinte peut même franchir indûment le seuil de publication.

Correction proposée : construire l'ensemble des rôles de gestion à partir de leurs définitions selon A-17, exclure tout titulaire de l'un de ces rôles, puis conserver en complément la détection des capacités directes. Ajouter le cas d'une surcharge négative et celui de plusieurs rôles au banc classique/HPOS. Constat établi par lecture croisée ; ce scénario PHP n'a pas pu être exécuté ici.

Les autres interprétations sont explicites dans les notes : quatre statuts vivants, déduplication par compte, collisions comparées à tous les comptes, égalité login/email exacte, casse ASCII, regroupement des petites catégories par tableau.

## 2. Exactitude métier

Deux déroulements manuels du besoin de reprise du §4.3, précisé par le brief :

- **Comptes avant neutralisation.** Dans `wp/tests/a23/seed.php:12`, les 32 lecteurs se répartissent en 10 empreintes phpass, 20 WordPress bcrypt, une inconnue et une vide. Résultat attendu : 10, 20 et `autres=2`. Les indices 0 à 19 portent un abonnement vivant, malgré le second abonnement du premier lecteur : 20 personnes, réparties en 10 et 10. Les indices 29 à 31 n'ont aucun historique : `without_commerce.autres=3`. Ces résultats concordent avec le code et les rapports classique/HPOS livrés. Les cinq paires d'emails donnent 10 lecteurs concernés ; le partage entre le lecteur 31 et un administrateur porte le total lecteurs à 11, tout en laissant le total des vivants à 10.
- **Même population après neutralisation.** `wp/outils/staging/lib.php:447` remplace login, email et empreinte ; le marqueur est posé en `:489`. Les six blocs correspondants doivent donc devenir « inconnu après neutralisation ». Les rapports neutralisés livrés portent bien ces six mentions et conservent 32 lecteurs, 20 vivants et `autres=3` sans historique. Aucune déduction de compatibilité de mot de passe n'est faite.

Les bornes 4/5, la population vide, les collisions avec l'administration et le rejeu identique sont couverts. Les dates de clôture et changements d'année ne sont pas applicables à cet inventaire : il observe les statuts stockés. La classification des lecteurs reste à corriger selon P1.

## 3. Tests

Commandes exécutées depuis la racine, avec `C:/Python314/python.exe`, sans génération de bytecode :

```text
C:/Python314/python.exe -B -m unittest discover -s wp/tests/a23 -p test_*.py -v
C:/Python314/python.exe -B wp/tests/a23/verify.py --require-shared-doc
```

Chacune a été exécutée en UTF-8 (`PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1`), puis en cp1252 (`PYTHONIOENCODING=cp1252`, `PYTHONUTF8=0`).

- **Vérificateur du paquet : code 0 dans les deux contextes, 67 contrôles PASS.** Sources, dépendances, manifeste, rapports, journaux et intégration documentaire concordent. Les empreintes des tables avant/après sont identiques, y compris après neutralisation.
- **Suite Python : code 1 dans les deux contextes.** Sur 23 tests, 11 réussissent ; 12 rencontrent des refus d'accès aux dossiers temporaires (`PermissionError`, WinError 5). Les erreurs de nettoyage portent le bilan à 23 erreurs par passage. Ce résultat ne constitue pas un échec fonctionnel démontré du lot, mais interdit d'annoncer un rejeu intégral vert par ce relecteur.
- **Sonde PHP pure tentée par WSL :** `wsl.exe -d Ubuntu -- php -n /mnt/c/Users/Ced/imagine/wp/tests/a23/pure-probe.php` échoue avant PHP avec `Wsl/Service/E_ACCESSDENIED`. La matrice native Docker, qui utilise WSL, et PSR-12 n'ont donc pas été rejoués ici.

Les preuves livrées, distinctes de ces tentatives, rapportent par console 23 tests Python, 34 contrôles purs, 14 contrôles du standard, 160 contrôles natifs et 9 contrôles du runner, tous verts. Leur intégrité a été vérifiée ; leur exécution complète n'est pas une observation nouvelle de cette relecture.

Les assertions natives comparent des nombres attendus explicites, vérifient les canaris, les refus et l'absence de mutations. Le cas P1 manque : le rôle personnalisé du banc ne reçoit aucune surcharge négative.

## 4. Sécurité et données

Pas de fuite d'identité ou d'empreinte de mot de passe relevée dans les sorties examinées. `wp/outils/bascule/a23/report.py:39` ferme les clés et libellés du rapport ; `confine.py:71` attend le gardien commun avant validation et publication. Les erreurs exposées appartiennent à une liste fermée. Les canaris couvrent notamment les deux flux, les sorties de fin de processus et les fichiers altérés.

La lecture utilise le Runtime A-11 et sa transaction READ ONLY, avec confinement Landlock. L'import n'est pas modifié. Aucun site, compte ou base n'a été consulté pendant cette relecture. Nonces et paywall : sans objet pour ce complément CLI, qui ne crée aucune route web.

## 5. Doctrine

Analyse pure séparée de l'adaptateur WordPress ; PHP strict et espaces de noms `Imagine`. Réutilisation du gardien et des barrières existantes. Les choix de reconnaissance des préfixes ne remplacent pas la vérification native des mots de passe. Le standard et ses limites sont documentés ; aucun essai de connexion n'est nécessaire au comptage.

P1 est une incohérence technique avec une définition déjà annoncée. Défaut proposé : conserver l'exclusion inclusive des rôles d'A-17, en ajoutant les capacités directes. Aucun arbitrage sur le réel n'est requis.

## 6. Études (lots sans code)

Sans objet : lot avec code. Les dix lignes du README citent trois adresses officielles et le reçu d'inspection du code installé. Les pages externes n'ont pas été reconsultées dans ce rôle ; leur contenu n'est donc pas présenté comme vérifié indépendamment ici.

## Verdict

**À corriger.**

- **Bloquant :** aucun relevé.
- **Important :** P1 — exclure aussi les titulaires de rôles personnalisés de gestion lorsque leurs capacités individuelles sont désactivées ; ajouter les tests correspondants.
- **Mineur :** aucun point supplémentaire retenu.

Les restrictions locales de rejeu sont consignées séparément des défauts du code. Ce verdict n'est pas un GO.
