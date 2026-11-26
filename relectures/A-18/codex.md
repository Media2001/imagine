# A-18 — Relecture indépendante Codex

26 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine et grille, brief A-18, cahier des charges §4.4, décisions du dépôt. Examen de `production/A-18`, des sources et tests A-18, ainsi que des dépendances A-11/A-12 pertinentes. Le rapport de Claude n’a pas été lu. Aucun autre fichier n’a été modifié.

## 1. Conformité

Le lot fournit le complément confiné, les comptes séparés de jetons, l’inventaire des médias, les deux lignes du mode d’emploi, les tests et `PRET`. Le paquet unique `preuves/final` comprend les deux consoles. La neutralisation produit bien un état inconnu plutôt qu’un zéro historique. Aucun nettoyage n’est implémenté.

**R1 — Important — `wp/outils/bascule/a18/Inventory.php:64` : le magasin inactif échappe à l’inventaire.** Le choix ternaire ne lit que les métadonnées du stockage faisant autorité. Si HPOS est actif et qu’un ancien IBAN reste dans `postmeta`, il est invisible ; réciproquement pour un reliquat dans `wc_orders_meta` lorsque le stockage classique est actif. C’est un inventaire de conservation au titre du §4.4 : une copie inactive reste une donnée stockée. L’interprétation restrictive est documentée dans le README, mais laisse cet objectif incomplet. **Correction proposée :** inventorier les deux magasins lorsqu’ils existent, distinguer leur provenance par un libellé technique fermé et expliciter que les comptes portent sur les valeurs physiquement conservées. Ajouter un cas où la seule forme sensible se trouve dans le magasin inactif, dans les deux sens.

### Décisions techniques, défaut proposé

**D1 — `wp/outils/bascule/a18/README.md:27` : la protection effective des dossiers demeure inconnue.** Le oui/non demandé n’est pas livré : le code observe un nom de fichier de règles et rend `reading_denied=null`. L’écart est signalé honnêtement. **Catégorie : technique. Défaut prudent proposé :** conserver cet état inconnu et l’interdiction d’ouvrir les fichiers ; ne jamais assimiler présence à protection, ni absence à exposition. Faire entériner par Claude cette limite et harmoniser le critère de réception avec elle. Aucune demande d’accès au réel ni d’arbitrage à Ced n’est nécessaire pour appliquer ce défaut.

## 2. Exactitude métier

Déroulement manuel de cas fictifs du lot, rattachés à l’interdiction de conservation du §4.4 :

| Cas | Attendu | Code et preuves livrées |
|---|---|---|
| Deux métadonnées de commande de même clé : `BE68539007547034` et `BE69539007547034` | Un seul IBAN compté | Structure belge de 12 chiffres ; reste modulo 97 égal à 1 pour le premier, différent pour le second. Groupe `_a18_bank` à 1 en classique et HPOS. |
| Carte de test `4242 4242 4242 4242` dans une métadonnée de compte | Une carte, aucune valeur restituée | 16 chiffres, somme de Luhn 80 ; groupe `_a18_card` à 1. |
| Trois fichiers fictifs dans `exports`, de 3, 4 et 5 octets | Deux CSV, un LOG, 12 octets | Résultat conforme dans les deux stockages ; les noms ne figurent pas dans les rapports. |

**R2 — Important — `wp/outils/bascule/a18/Forms.php:75` : des chiffres voisins masquent une forme valide.** L’expression commune extrait un candidat glouton de 11 à 19 chiffres, puis les validateurs ne reconsidèrent pas ses sous-candidats. Ainsi `4242 4242 4242 4242 123` est testé comme un unique numéro de 19 chiffres, rejeté par Luhn : la carte de test disparaît. De même, `85.07.30-033.28 2026` perd le registre belge valide, absorbé dans un candidat trop long. **Correction proposée :** rechercher séparément les candidats de carte et de registre, réexaminer les frontières de groupes après échec, sans accepter des fragments arbitraires d’une suite continue de chiffres. Tester ces deux valeurs et maintenir le comptage maximal d’une occurrence par forme et par ligne stockée.

**R3 — Important — `wp/outils/bascule/a18/Forms.php:63` : l’extraction IBAN est moins permissive que sa validation.** `$space` n’accepte qu’un espace, une tabulation ou un tiret facultatif. `BE68  5390 0754 7034`, ou le même IBAN avec un retour à la ligne après `BE68`, passe la normalisation de `iban()` mais n’est jamais extrait par `scan()`. Une valeur valide ainsi mise en forme disparaît donc du compte. **Correction proposée :** rendre les séparateurs reconnus par l’extraction cohérents avec ceux du validateur, en conservant les contrôles de longueur, structure et clé. Ajouter des tests passant par `scan()` puis `groups()`, pour espaces multiples, retour à la ligne et espaces insécables.

R1 à R3 résultent de la lecture du code. Pour R2, le parcours de l’expression et les calculs ont aussi été vérifiés en Python, en mémoire, sur ces données fictives ; cela ne constitue pas un rejeu du PHP.

## 3. Tests

Exécutés pendant cette relecture, sans production de fichiers :

- `python -B wp/tests/a18/verify.py production/A-18/preuves/final` : code 0, les 34 contrôles passent, dont correspondance des sources, intégrité du paquet et égalité des empreintes livrées.
- `python -B wp/tests/a18/test_launcher.py` avec `PYTHONIOENCODING=cp1252`, `PYTHONUTF8=0` : 3 tests réussis, code 0.
- Même suite avec `PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1` : 3 tests réussis, code 0.

**Limite du rejeu indépendant :** le prérequis Docker du lanceur natif a été tenté via sa fonction `b.call(['image','inspect',b.IMAGE])`. WSL refuse l’accès : `Wsl/Service/E_ACCESSDENIED`, retour 4294967295. Le banc natif, les tests PHP et PHPCS n’ont donc pas été rejoués ici ; aucun PHP n’est disponible dans le PATH. Le lanceur complet, qui crée des fichiers de preuves, n’a pas été démarré après ce refus.

Les preuves vérifiées déclarent, par console, 10 assertions PHP, 84 assertions natives et 7 contrôles du lanceur réussis, ainsi qu’un PHPCS sans erreur ni avertissement. Ce sont les résultats livrés, distincts des exécutions ci-dessus. La couverture des canaris, empreintes, liens symboliques, refus, neutralisation et médias est substantielle. Elle ne couvre pas les contre-exemples R1 à R3 ; les corrections doivent ajouter ces régressions au paquet unique.

## 4. Sécurité et données

La lecture examinée ne relève pas de restitution de valeurs ou d’identifiants de personnes dans les rapports nominaux. Clés techniques filtrées, dossiers et extensions sur listes fermées, SQL paginé, références de jetons séparées sans lecture de leur colonne `token`. Le point d’entrée PHP réduit les exceptions à une liste littérale de codes ; les refus de drop-ins utilisent la liste fermée du runtime commun.

Le confinement A12 et la connexion en transaction READ ONLY d’A11 sont réutilisés. Les preuves livrées contrôlent les écritures, les empreintes et l’absence d’ouverture des médias. Leur validité en exécution n’a pas été réétablie ici faute de WSL. Nonces et paywall : sans objet pour ce complément CLI. R1 à R3 affectent surtout la fiabilité du diagnostic de conservation.

## 5. Doctrine

La logique de reconnaissance est isolée du branchement WordPress ; les sources PHP de production portent `strict_types` et l’espace de noms `Imagine`. Le README explique le rôle des jetons, le lancement et les limites. Le recours au sur-mesure est justifié dans la livraison par l’absence d’inventaire transversal dans l’API de jetons ; les références sont consignées, sans nouvelle consultation externe pendant cette relecture. Aucun nettoyage, déploiement ou accès au réel effectué.

## 6. Études (lots sans code)

Sans objet : lot de code. La provenance du registre IBAN et la limite de fraîcheur sont explicitement documentées ; cette relecture n’en certifie pas l’actualité.

## Verdict

**À corriger.**

- **Bloquant :** aucun constat classé à ce niveau.
- **Important :** R1, magasin inactif ignoré ; R2, formes masquées par des chiffres voisins ; R3, IBAN valides perdus sur les séparateurs.
- **Mineur :** aucun constat supplémentaire.

D1 conserve un défaut technique prudent à faire entériner. Le rejeu natif indépendant reste à effectuer dans un environnement autorisant WSL. Ce verdict n’est pas un GO.
