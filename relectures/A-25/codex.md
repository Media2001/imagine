# Relecture indépendante Codex — A-25

**Alerte import : les messages de formulaires peuvent rester en clair après neutralisation/anonymisation.** Dans `wp/outils/staging/lib.php:352`, les tables inconnues sont exclues des transformations personnelles automatiques ; leur anonymisation explicite dépend de la décision traitée à la ligne 420. Avec `garder`, les messages du banc restent présents. Les reçus livrés `classic-neutralisation.json` et `hpos-neutralisation.json` le confirment pour les deux tables fictives. Information à transmettre au chantier d’import ; aucune modification de l’import demandée dans ce lot.

Relecture du 26 novembre 2026. Doctrine, grille, brief et §4.4 du cahier des charges lus. Aucun accès à un site, compte ou jeu de données réel ; rapport Claude non consulté. Seul fichier du dépôt écrit : le présent rapport.

## 1. Conformité

Le lot fournit le script, le lanceur confiné, les tests, le paquet de preuves et `PRET`. Les deux lignes A-25 sont présentes dans `wp/tests/a02-audit/README.md:95`. Les livrables restent dans le périmètre du registre des traitements du §4.4 : aucun nettoyage, aucune durée de conservation imposée. Le choix fermé de Fluent Forms et l’interprétation « commande sans compte = client natif 0 » sont explicités.

**I-1 — Important — `wp/outils/bascule/a25/Inventory.php:87` : exclusion injustifiée de certaines tables de messages inconnues.** La seule présence d’une colonne `submission_id` fait considérer la table comme une sous-table à ignorer. Contre-exemple fictif : une table inconnue comportant `submission_id PRIMARY KEY`, `form_id`, `message`, `submitted_at`, avec cinq soumissions de 2024. Elle contient bien une ligne par message et satisfait les autres critères du détecteur, mais le `continue` empêche tout comptage. Sans autre table de formulaires, la sortie indique `other_tables = 0` et un total de zéro, alors que le brief exige le classement sous « autre ». La limite générale annoncée dans le README ne résout pas ce faux négatif au sein des structures déjà reconnues.

**Correction proposée :** distinguer une clé primaire de soumission d’une référence vers une soumission par les contraintes du schéma, au lieu d’exclure toute colonne portant ce nom. Compter cette table sous `autre`, sans publier son nom. Ajouter un cas natif avec cinq messages et une vraie table enfant pour vérifier simultanément la conservation du compte et l’absence de double comptage. Si la structure reste ambiguë, signaler une couverture indéterminée par une valeur fermée plutôt que présenter une absence certaine.

## 2. Exactitude métier

Cas déroulés à la main à partir du brief et comparés au moteur et aux rapports livrés :

- **Banc nominal :** trois commentaires répartis sur deux années, deux avec email/IP et un lié à un compte donnent respectivement `autres = 3, 2, 2, 1`. Deux entrées Fluent Forms et deux inconnues donnent `autres = 4` ; deux commandes sans compte donnent `autres = 2`. Aucun groupe année/état inférieur à cinq n’est exposé. Les rapports classique et HPOS concordent.
- **Seuil et changement d’année :** cinq commentaires datés du 31 décembre 1999 en GMT, mais du 1er janvier 2000 localement, restent dans le groupe 1999/état `1`. Cinq commandes et cinq entrées Fluent Forms de 1999 deviennent visibles ; les petits groupes précédents restent fondus. Le rapport `classic-five/visiteurs.json` correspond à ce calcul.
- **Après import :** l’email est remplacé même lorsqu’il était vide (`lib.php:465`) et l’IP est effacée (`lib.php:460`). Les métriques email/IP deviennent correctement « inconnu après neutralisation ». Le même traitement prudent s’applique aux nombres de formulaires ; les comptes de commentaires et de commandes du banc restent conservés.

Le contre-exemple I-1 a été déroulé dans les branches du code ; il n’a pas été exécuté sur une base pendant cette relecture.

## 3. Tests

Exécutions effectuées sans modifier les sources :

- `C:/Python314/python.exe -B wp/tests/a25/verify.py --require-shared-doc` : **code 0**. Sources et dépendances actuelles, empreintes, rapports, paquet scellé et documentation partagée sont acceptés. Ce contrôle valide des preuves livrées ; il ne rejoue pas l’intégration.
- Suite `unittest discover -s wp/tests/a25 -p 'test_*.py' -v`, en cp1252 : **21 tests exécutés, 18 réussis, 3 erreurs**. Les erreurs concernent l’accès aux répertoires temporaires (`PermissionError`/`WinError 5`) dans les tests de superviseur manquant, de fichiers de rapport et de sceau. Aucun échec d’assertion observé.
- `C:/Python314/python.exe -B wp/tests/a25/matrix.py --output=$env:TEMP/a25-codex-review-20261126` : **code 1**. Les deux passages Python retrouvent ces trois erreurs. Les runners natifs échouent avant création du banc avec `DOCKER_IMAGE_FAILED:4294967295` ; le contrôle de style échoue également sur son infrastructure. PHP, classique/HPOS et PHPCS n’ont donc pas pu être rejoués ici.

Ces limitations d’exécution ne sont pas attribuées au code A-25. Le paquet livré, vérifié avec succès, contient par encodage 21 tests Python, 15 contrôles PHP purs, 9 qualifications natives, 194 contrôles d’intégration et 9 contrôles du runner. Il couvre notamment canaris, canaux d’erreur, import, rejeu, seuil de cinq et date absente.

**Lacune associée à I-1 :** `wp/tests/a25/seed.php:38` fournit uniquement une table inconnue avec clé `id` et colonne `message`, qui satisfait exactement l’heuristique. Elle ne permet pas de détecter l’exclusion erronée d’une clé primaire `submission_id`.

## 4. Sécurité et données

Le lanceur réutilise la supervision A-22, attend la fin des deux flux et valide strictement les deux rapports avant publication. Les noms libres de tables, contenus, emails, IP et identifiants de visiteurs ne sont pas projetés. Les requêtes sur les formulaires sélectionnent uniquement années et comptes ; les identifiants SQL interpolés sont bornés. Les protections SQL en lecture seule et Landlock sont réutilisées.

Aucune fuite supplémentaire identifiée à la lecture et dans les preuves contrôlées. Cette conclusion reste limitée par l’impossibilité de rejouer le banc natif. Droits web, nonces et paywall : sans objet pour cette commande locale d’inventaire.

## 5. Doctrine

Les objets WordPress/WooCommerce et les protections communes sont réutilisés. Le regroupement est isolé dans une classe PHP pure ; espace de noms et typage strict sont présents. Le paquet annonce un contrôle PSR-12 sans erreur ni avertissement, vérifié comme artefact mais non rejoué ici. Aucune correction directe du code ni de l’import effectuée.

## 6. Études (lots sans code)

Sans objet : lot avec code. `production/A-25/SOURCES.md` fournit les références officielles et explique le choix de Fluent Forms. Leur contenu distant n’a pas été consulté, conformément à l’interdiction d’accéder à un site. Le banc reproduit le schéma Fluent Forms ; il ne qualifie pas une installation de cette extension, limitation correctement déclarée.

## Verdict

**À corriger.**

- **Bloquant :** aucun point identifié.
- **Important :** I-1 — ne pas perdre les tables de messages dont `submission_id` est la clé primaire ; compléter la preuve native correspondante.
- **Mineur :** aucun point retenu.

Le rejeu complet reste non confirmé dans l’environnement de cette relecture. Ce verdict ne constitue pas un GO.
