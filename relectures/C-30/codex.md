# C-30 — Relecture indépendante Codex

Date : 28 novembre 2026. Périmètre : brief C-30, production C-30, code et tests dans `wp/`, raccords C-21/C-27, doctrine, décisions et cahier des charges §3.7, §3.14 et §4.2. Le rapport Claude n’a pas été consulté. Aucun site, compte ou base n’a été accédé ; aucun fichier de production n’a été modifié.

## 1. Conformité

L’essentiel du périmètre est présent : page native « Bienvenue », texte laissé vide, lien vers l’entrée abonnement, trois codes fictifs, liste fermée journalisée, session WooCommerce, attribution au paiement, compteurs distincts de C-27 et callbacks de confidentialité. Le code examiné ne modifie ni prix, ni coupon, ni source d’acquisition du compte ; il n’ajoute aucun transport vers Odoo ou la newsletter.

Les choix « dernier code connu avant la commande », candidat provisoire pour le paiement différé, bornes UTC incluses et checkout classique uniquement sont explicités. La restriction au checkout classique est une limite de livraison déclarée, pas une preuve de fonctionnement avec Blocks.

- **M1 — Mineur — `wp/plugins/imagine-site/CodesSuivisAdmin.php:79`.** L’aide annonce des codes composés de minuscules, chiffres ou tirets, mais le validateur impose une lettre en première position. Par exemple, `2026-affiche` respecte l’aide et est pourtant refusé avec le seul message générique « Liste invalide ». **Correction proposée :** préciser « commençant par une lettre minuscule » dans l’aide et le README ; conserver ce défaut technique prudent et couvrir cet exemple dans le test de validation.

## 2. Exactitude métier

Cas déroulés à la lecture du code et confrontés aux preuves livrées :

1. Visite avec `fictif-affiche`, puis `fictif-magazine`, puis un inconnu : la session conserve `fictif-magazine`. Le checkout enregistre le candidat ; une commande payée avec date native reçoit le code et le sceau, puis perd son candidat. Un nouveau paiement après changement de session ne remplace pas le code. Ce déroulé concorde avec les contrôles natifs archivés.
2. Session neuve, code inconnu ou absent : aucun candidat n’est créé, et `payer()` n’attribue rien. Une commande `created_via=imagine-c16` est également exclue. Une liste vidée avant un nouveau checkout empêche la reprise du code encore présent en session grâce à sa revalidation.
3. Paiement différé : le transfert utilise le candidat de la commande, sans relire la session. Après effacement, le sceau empêche la recréation sur cette commande. Les bornes du compteur sont inclusives ; une date impossible est refusée. Le changement d’année n’a pas de branche spéciale dans la comparaison de dates normalisées.

Le défaut de sélection des commandes pour la confidentialité est détaillé en section 4.

## 3. Tests

Exécutions effectuées sans écrire de nouveaux reçus :

| Commande | Résultat constaté |
|---|---|
| `python -B production/C-30/verifier.py` | PASS : intégrité des sources, enregistrement, README et preuves archivées |
| `python -B production/B-13/qualifier.py C-30` | PASS : 9 contre-épreuves du vérificateur |
| PHPUnit ciblé sur `CodesSuivisC30Test`, avec `--do-not-cache-result` | Non exécuté : `php` absent du PATH |
| `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1` | Échec d’environnement avant les tests : `Wsl/Service/E_ACCESSDENIED`, Docker inaccessible ; 0 test exécuté |

Le premier PASS vérifie des preuves existantes : il ne rejoue pas les 23 contrôles natifs, les 99 contrôles navigateur ni les 1 213 tests / 36 709 assertions annoncés par le reçu T01. Ces nombres restent historiques. `--live` et les recettes de démonstration n’ont pas été lancés : `relecteurs/AGENTS.md` interdit l’accès à un site ou une base. Aucune installation n’a été tentée.

La mutation PHPUnit modifie effectivement en mémoire le contrôle d’appartenance à la liste et constate le refus attendu du résultat mutant. Les preuves couvrent aussi le dernier code connu, C-16, le journal indisponible et l’absence de recréation après effacement.

- **I2 — Important — `wp/tests/demo/c30-runtime.php:49`.** La preuve `prix_identique` compare deux totaux fixés à `12.34` par la même fabrique, sans produit, panier ni calcul natif du prix. Elle ne détecterait pas une remise ou des frais introduits dans les hooks de calcul du panier. **Correction proposée :** comparer deux achats fictifs du même produit, mêmes quantités et mêmes conditions, avec et sans code, après calcul WooCommerce ; vérifier total, remises et coupons, puis restaurer les objets. Le test doit pouvoir échouer si une modification de prix liée au code est introduite.

Le cas I1 ci-dessous n’est pas couvert : la fixture de confidentialité utilise exclusivement des commandes rattachées au compte `P-NUMERO`.

## 4. Sécurité et données

- **I1 — Important — `wp/plugins/imagine-site/CodesSuivisConfidentialite.php:28`.** Dès qu’un compte existe pour l’adresse demandée, `commandes()` recherche uniquement son `customer_id` et abandonne la recherche par adresse de facturation. Une commande invitée (`customer_id=0`) portant cette adresse et un code suivi est donc absente de l’export et de l’effacement. Cas concret : un client possédant déjà un compte achète déconnecté, ou une ancienne commande invitée reste non rattachée après création du compte. L’effaceur peut retourner `done=true`, sans signaler de données conservées, alors que le code et son libellé subsistent sur cette commande. **Correction proposée :** sélectionner l’union des commandes du compte et des commandes invitées portant l’adresse vérifiée, avec dédoublonnage et pagination stable. Tester ensemble une commande liée, une commande invitée de même adresse et une commande d’un tiers ; exporter et effacer les deux premières, préserver la troisième.

Les contrôles d’accès des deux écrans, le nonce Settings API, l’échappement des sorties et les paramètres des verrous SQL sont présents. Les inconnus ne sont pas recopiés dans les métadonnées C-30. Aucun secret ni identité réelle repéré dans les éléments examinés. La page n’ajoute pas de lecture de texte réservé ; les contrôles d’étanchéité du navigateur restent des preuves archivées, non rejouées ici.

## 5. Doctrine

Le recours à la page WordPress, aux sessions et au CRUD WooCommerce, aux réglages natifs et aux outils de confidentialité évite de reconstruire ces mécanismes. Le README distingue l’attribution native Sourcebuster du catalogue fermé de codes imprimés ; les extraits de sources officielles installées sont conservés dans `standard2-V2.json`.

Les règles de validation sont isolées en PHP pur ; espace de noms `Imagine`, typage strict, préfixes et traduction des interfaces sont présents. Le seed est versionné et rejouable, mais réservé à la démonstration. Aucun déploiement n’a été effectué dans cette relecture.

## 6. Études (lots sans code)

Sans objet : lot de code. Les références au standard ont été examinées dans les fichiers livrés, sans consultation externe.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant :** aucun défaut classé à ce niveau.
- **Important : I1**, commandes invitées omises de l’export et de l’effacement ; **I2**, preuve de non-modification des prix insuffisante.
- **Mineur : M1**, aide de saisie incomplète sur le format des codes.

Le rejeu PHP reste à effectuer dans un environnement local disposant du runtime autorisé. Les corrections proposées sont techniques et ne nécessitent pas d’arbitrage de Ced.
