# Relecture indépendante Codex — A-24

Date : 26 novembre 2026. Périmètre : brief A-24, production du lot, outil et tests A-24, dépendances de confinement et anonymiseur. Doctrine, grille, décisions et CDC §3.13/§4.3 lus. Le rapport Claude n’a pas été consulté. Aucun code ni document de production modifié.

## 1. Conformité

Les livrables sont présents, dont `production/A-24/PRET`. Les deux lignes du mode d’emploi commun sont intégrées et leur contrat passe. Les quatre états vivants correspondent à A-20 ; les comptes portent sur les abonnements, sans prétendre déterminer les droits au prochain numéro du §3.13. Aucun repli facturation→livraison ni correction d’adresse n’est effectué.

Les obligations proviennent de `WC_Countries::get_address_fields()`, les getters natifs lisent le magasin faisant autorité, les petits groupes sont regroupés sous « autres pays ». Le choix « facturation remplie = au moins un champ non vide » et le traitement séparé des comptes indisponibles sont explicités.

Un écart au brief reste à corriger : la comparaison au compte est littérale. Il est décrit dans les notes et le README, mais cette documentation ne remplace pas la règle demandée. Voir P1 ci-dessous.

## 2. Exactitude métier

**P1 — important — `wp/outils/bascule/a24/Analysis.php:29` : la comparaison compte à tort la casse et les espaces comme des divergences.** Le brief demande une comparaison « champ à champ, à la casse et aux espaces près ». L’opérateur `!==` compare les chaînes brutes. Deux rues fictives `Rue Exemple` et `rue exemple`, ou `Rue Exemple` et `Rue Exemple `, augmentent donc `different_from_account` alors que ce compteur devrait rester nul. Cela fausse le total et les groupes par pays. Le banc livré contient précisément ces deux variations et publie `different_from_account = 2`, globalement et pour BE.

**Correction proposée :** normaliser uniquement les valeurs utilisées pour cette comparaison, afin d’ignorer la casse et les variations d’espacement, sans modifier les données stockées ni les critères de complétude. Tester séparément casse, espaces et changement réel de rue ou de code postal. Mettre en cohérence le README et les attentes du banc, puis régénérer le paquet unique de preuves. Ce point applique une règle déjà écrite dans le brief et ne nécessite pas d’arbitrage de Ced.

Cas déroulés à la main, pour le diagnostic préparatoire aux CDC §3.13/§4.3, puis confrontés au code et aux preuves livrées :

| Cas fictif | Résultat attendu et constat |
| --- | --- |
| Livraison belge complète, identique au compte | Aucun vide, aucun champ obligatoire manquant, aucune divergence : conforme. |
| Livraison entièrement vide, facturation complète | Un vide, un vide avec facturation présente, un incomplet et un pays absent ; les six champs requis du pays de base BE sont manquants : conforme, sans recopie. |
| Livraison FR sans code postal, autres champs complets | Un incomplet et un manque `shipping_postcode` : conforme. Le même manque en AE ne crée pas d’incomplétude sur la pile qualifiée. |
| Compte et abonnement ne différant que par casse ou espace | Aucune divergence attendue ; le code en compte une par abonnement : P1. |

Le seuil de regroupement est bien strictement inférieur à cinq. Les états `cancelled` et `expired` sont exclus. Les dates de clôture et les droits au numéro relèvent de la liste d’envoi, pas de cet inventaire.

Après lecture de l’anonymiseur, le remplacement par « inconnu après neutralisation » est cohérent pour les compteurs dépendant des champs effacés. Restent exploitables les effectifs, les pays absents/inconnus, les groupes par pays, le manque du champ pays et les comptes indisponibles. Les preuves classique/HPOS présentent ces inconnus au total comme dans les groupes.

## 3. Tests

Exécutions indépendantes effectuées avec `C:/Python314/python.exe`, option `-B`, sans écriture de bytecode dans le dépôt :

- `-m unittest discover -s wp/tests/a24 -p 'test_*.py' -v`, avec `PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1` : **14 tests, 8 réussites, 6 erreurs**.
- Même commande avec `PYTHONIOENCODING=cp1252`, `PYTHONUTF8=0` : **14 tests, 8 réussites, 6 erreurs**.
- `wp/tests/a24/verify.py --require-shared` : **code 0, tous les contrôles PASS**, empreintes des sources et dépendances, paquet, rapports et intégration du README compris.
- `wp/tests/a24/run.py --output=<dossier temporaire neuf hors dépôt>` : **code 1**, arrêt sur `DOCKER_IMAGE_FAILED:4294967295`, avant création du conteneur. Les contrôles de stabilité des sources et dépendances passent.

Les six erreurs de chaque suite Python sont des refus de permissions dans les dossiers temporaires (`PermissionError`, notamment `WinError 5`), pendant la préparation ou le nettoyage des fixtures. Elles ne démontrent pas un défaut métier du lot. Le banc PHP pur et natif n’a pas pu être rejoué dans cet environnement ; je ne revendique donc pas un rejeu indépendant complet classique/HPOS ni du parcours opérateur.

Le paquet livré, vérifié sur les sources présentes, consigne par encodage 14 tests Python, 17 contrôles PHP purs, 9 fichiers PHP lintés et 206 contrôles natifs réussis. Il couvre notamment les canaux de sortie, les mutations sans gardien, la neutralisation effective, les filtres de champs requis et les empreintes avant/après.

Pour P1, `wp/tests/a24/unit.php:50` attend explicitement deux divergences sous le nom `literal_case_and_space_comparison`. Le test reproduit ainsi l’interprétation erronée au lieu de vérifier le brief ; le succès du paquet ne détecte pas cet écart. La correction de P1 doit inclure cet oracle et son équivalent natif.

## 4. Sécurité et données

Aucune fuite d’adresse ou d’identifiant repérée dans les rapports examinés. Les fixtures sont fictives. Le lanceur utilise le gardien commun A-22, attend la terminaison et les deux fins de flux, puis vérifie le schéma fermé et la correspondance JSON/Markdown avant publication. Les valeurs libres de pays ou de champs ne sont pas restituées.

Les preuves livrées vérifiées établissent l’absence de canaris dans les artefacts, les refus de sorties altérées et l’égalité des empreintes des tables et fichiers avant/après, y compris après neutralisation. Cette conclusion reste fondée sur le paquet livré pour les contrôles natifs, compte tenu de la limite de rejeu ci-dessus. Aucun accès à un site, une base réelle ou un compte n’a été effectué pendant cette relecture. Nonces et paywall : hors périmètre de cet outil CLI.

## 5. Doctrine

Le standard est utilisé pour les données et obligations WooCommerce ; le calcul d’agrégats reste dans une classe PHP pure, séparée de l’adaptateur natif. Les classes de production déclarent les types stricts et un espace de noms `Imagine`. Le confinement existant est réutilisé et l’anonymiseur n’est pas modifié. La correction de P1 doit rester une normalisation en mémoire, sans devenir une opération de nettoyage des adresses.

## 6. Études (lots sans code)

Sans objet : lot de code. Le README fournit les dix lignes de standard, trois références officielles et les preuves de qualification native. Ces pages externes n’ont pas été ouvertes, conformément au périmètre de relecture local ; leur contenu n’est pas certifié par cette relecture.

## Verdict

**À corriger.**

- **Bloquant :** aucun défaut de cette gravité établi.
- **Important : P1**, `wp/outils/bascule/a24/Analysis.php:29` — comparaison sensible à la casse et aux espaces, contraire au brief ; corriger le calcul, les oracles et les preuves associées.
- **Mineur :** aucun point distinct retenu.

La validation indépendante des tests reste partielle pour les raisons d’environnement décrites en section 3. Aucune question ouverte pour Ced ou Imagine. Ce verdict n’est pas un GO.
