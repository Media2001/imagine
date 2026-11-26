# Relecture indépendante Codex — A-27

Date : 27 novembre 2026. Périmètre : brief A-27, production A-27, code et tests concernés dans `wp/`, dépendances utilisées. Référentiel : `relecteurs/AGENTS.md`, doctrine et grille, cahier des charges §3.6 et §4.3, décisions du dépôt. Aucune consultation de la relecture Claude. Aucune correction du code ni des preuves.

## 1. Conformité

Les livrables demandés sont présents : inventaire, lanceur confiné utilisant A-22/A-12, tests Python et PHP, dix lignes sur le standard, deux lignes intégrées au mode d'emploi commun, paquet unique et marqueur `PRET`. Le périmètre reste un comptage ; aucune conclusion de survie du renouvellement n'est produite. Les états vivants correspondent à A-20. Les conventions d'expiration, de rattachement et de regroupement sont explicitées.

La réponse « inconnu après neutralisation » pour tous les comptes est cohérente avec la purge des tables de jetons et des références sensibles dans l'import actuel. Ce résultat est explicitement permis par le brief. Il ne constitue pas une autorisation de compter sur la source réelle.

**R1 — Bloquant pour accepter les preuves courantes — `production/A-27/PRET:1`.** Le marqueur annonce des « gates et sceau verts », mais les deux vérificateurs livrés échouent aujourd'hui. `wp/tests/a27/verify.py` retourne 1, avec trois contrôles rouges : `exact_current_dependencies`, `utf8:executed_dependencies`, `cp1252:executed_dependencies`. La comparaison des empreintes identifie précisément `wp/outils/staging/command.php` et `wp/outils/staging/lib.php` comme différents du paquet final et du gel parent. `production/A-27/verify.py` retourne également 1 (`SEALED_VERIFICATION_FAILED`, `AssertionError`). Les sources propres à A-27 correspondent encore au paquet : il s'agit d'une dérive des dépendances, sans attribution de son origine au producteur du lot. **Correction proposée :** faire requalifier par le parent le lot avec les dépendances actuelles, notamment la neutralisation réellement exécutée, puis renouveler le paquet unique, son scellement et le statut `PRET`. Ne pas simplement actualiser les empreintes de preuves anciennes.

## 2. Exactitude métier

Cas déroulés manuellement à partir des exigences de conservation des moyens (§4.3) et des circuits carte/SEPA/PayPal (§3.6), avec comparaison au code et aux rapports fictifs archivés :

- **Cartes et seuil de cinq.** Au 26/11/2026 à 12 h UTC, cinq abonnements automatiques avec carte expirant en octobre 2026 donnent `stripe/carte = 5` et `expired = 5`. Cinq cartes expirant en mars 2027 et cinq en novembre 2026 donnent dix expirations dans les six mois. Le rapport `production/A-27/preuves/final/utf8/native/classic-five/paiements.json` porte bien quinze abonnements par carte, cinq cartes expirées et dix dans la fenêtre. La même comparaison HPOS est validée par le vérificateur des rapports archivés.
- **PayPal sans jeton de compte.** Cinq abonnements vivants automatiques avec `_paypal_subscription_id` non vide, sans identifiant de jeton, donnent `paypal/accord_paypal = 5` et `paypal/subscriptions_unlinked = 5`. C'est bien le résultat archivé. Ce classement constate une référence locale ; il ne prouve pas la validité d'un accord bancaire.
- **Après neutralisation.** La présence du marqueur conduit directement aux trois valeurs « inconnu après neutralisation », même avec des tables de jetons vides. Le rapport neutralisé correspond ; aucun zéro de remplacement n'est calculé.
- **Bornes.** L'expiration de novembre reste valide à `2026-11-30T23:59:59+00:00` et devient passée la seconde suivante. Une échéance fin mai 2027 dépasse la fenêtre terminant le 26 mai à midi. Le calcul tient compte du changement d'année et borne le jour cible pour les mois courts. Ces cas sont également présents dans les assertions PHP livrées, non rejouées ici.

Deux cas limites restent incorrects, par déroulé du code actuel :

**R2 — Important — `wp/outils/bascule/a27/Inventory.php:84`.** L'adaptateur reprend sans distinction le verdict de présence A-19. Pour une passerelle sans lecteur local A-27, par exemple `ppcp-gateway`, sans lien de jeton, un champ déclaré par `woocommerce_subscription_payment_meta` avec une `value` non scalaire est transformé en `absent` par A-19 (`Inventory.php:33`, puis ligne 40). A-27 conserve des métadonnées locales vides ; `Analysis::reference()` conclut alors `present = false` et `analyse()` exclut l'abonnement. Cinq références opaques peuvent ainsi produire zéro abonnement automatique compté au lieu de cinq `illisible`. Cela contredit directement « ce qu'on ne sait pas lire est illisible, jamais absent ». **Correction proposée :** préserver dans l'adaptateur la distinction entre champ réellement vide et champ non interprétable ; réserver l'exclusion à une absence prouvée. Ajouter un cas d'intégration classique et HPOS avec un schéma déclaré non scalaire, cinq occurrences et aucun jeton. Le test PHP existant sur une métadonnée non scalaire injectée directement dans `Analysis` ne traverse pas ce chemin A-19.

**R3 — Important — `wp/outils/bascule/a27/Analysis.php:114`.** Une contradiction entre référence locale et lien explicite ne devient pas toujours `illisible`, contrairement au défaut documenté dans le README, ligne 46. Exemple fictif : abonnement `stripe_sepa`, lien explicite vers le jeton B de type `CC`, référence `_stripe_source_id` correspondant au jeton A de type `eCheck`, les deux appartenant au même compte et à cette passerelle. Le rapprochement trouve A, constate que son identifiant n'est pas dans les liens, puis le repli classe malgré tout l'abonnement `mandat_sepa`, avec liaison inconnue. Cinq exemplaires publient donc cinq mandats SEPA malgré deux instruments contradictoires. Le même repli impose `accord_paypal` pour PayPal. **Correction proposée :** traiter la contradiction avant le repli de type par passerelle et retourner `illisible` avec liaison indéterminée ; conserver le classement SEPA/PayPal pour les références non contradictoires. Ajouter des assertions distinctes pour contradiction, référence seule et correspondance unique.

## 3. Tests

Exécutions effectuées pendant cette relecture, avec Python `C:/Python314/python.exe`, option `-B` et `PYTHONDONTWRITEBYTECODE=1` :

| Commande / environnement | Résultat observé |
| --- | --- |
| `-m unittest discover -s wp/tests/a27 -p "test_*.py" -v`, `PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1` | 38 tests exécutés ; code 1 ; `FAILED (errors=15)` |
| Même suite, `PYTHONIOENCODING=cp1252`, `PYTHONUTF8=0` | 38 tests exécutés ; code 1 ; `FAILED (errors=15)` |
| `-B wp/tests/a27/verify.py` | Code 1 ; trois contrôles de dépendances rouges, détaillés en R1 |
| `-B production/A-27/verify.py` | Code 1 ; `SEALED_VERIFICATION_FAILED` |

Les erreurs des suites Python proviennent des refus d'accès Windows (`PermissionError`, `WinError 5`) dans les répertoires temporaires `C:/Users/Ced/AppData/Local/Temp/a27-*`, y compris lors de leur nettoyage. Ce résultat limite le rejeu indépendant ; il ne démontre pas un défaut fonctionnel des tests. Aucun déplacement des tests dans le dépôt ni changement de permissions n'a été effectué pour contourner ces refus. Les tests sans cette dépendance aux fichiers temporaires, notamment les pipes du gardien et les refus cp1252, passent.

Les preuves archivées annoncent, par encodage, 38 tests Python, 53 assertions PHP pur, 166 assertions natives, 13 contrôles du runner et 10 contrôles du standard par magasin. Le vérificateur relit positivement ces résultats, les projections, les canaris et les empreintes avant/après des fixtures ; R1 empêche de les attribuer à l'ensemble des dépendances actuelles.

La matrice native, le style et le parcours Linux du mode d'emploi n'ont pas été réexécutés dans cette relecture : pas de PHP hôte disponible, et la réception livrée réserve les runners Docker/WSL à une exécution sérialisée par le parent (`production/A-27/RECEPTION-PARENT.md`, « Ne jamais lancer ces commandes en concurrence avec A-26 ou une autre porte Docker/WSL »). Leurs résultats ci-dessus sont des preuves archivées inspectées, pas de nouvelles exécutions. Aucune préparation d'image ni modification de fichier commun n'a été lancée.

La couverture est substantielle : seuil quatre/cinq, dates, magasins natifs, répétition, purge, arrêt anticipé, shutdown, canaux directs et altération cohérente des deux rapports. Les chemins R2 et R3 restent absents de cette couverture ; leurs résultats exposés ici proviennent d'une analyse statique, sans prétendre à un test PHP exécuté.

## 4. Sécurité et données

Aucune fuite de référence individuelle constatée dans les rapports examinés. Le vérificateur confirme l'absence des canaris retenus dans le paquet. Passerelles, types, expirations et métriques appartiennent à des listes fermées ; les petites cellules perdent leur libellé. Le JSON canonique, le Markdown dérivé, le jeu exact de fichiers et la liaison SHA-256 avant shutdown sont contrôlés avant publication.

Le lanceur réutilise le gardien A-22 et le confinement A-12. Le chargement natif utilise la couche SQL en lecture seule et les blocages HTTP, mail et planification. Les requêtes A-27 n'incorporent pas de valeurs métier fournies en entrée. Les contrôles de chemins et les modes privés sont prévus. Le lot est un outil CLI : nonces, droits d'administration web et paywall ne sont pas des surfaces modifiées ici.

Aucun accès à un site, compte, sauvegarde réelle ou service de paiement n'a été effectué pendant la relecture. La démonstration native actuelle de l'absence d'écriture et d'appel sortant reste à renouveler avec R1.

## 5. Doctrine

Le code réutilise les API WooCommerce/WCS et les protections existantes. L'analyse métier est séparée du chargement WordPress, avec typage strict et espace de noms `Imagine`. Le README explicite les limites de connaissance et n'annonce pas de migration bancaire réussie. Aucun changement d'extension tierce constaté dans le périmètre examiné.

### Décisions techniques, défaut proposé

R1 à R3 sont techniques : requalifier les preuves après dérive et classer les références opaques ou contradictoires comme `illisible`, sans exclusion silencieuse ni choix d'instrument. Ces corrections ne nécessitent pas d'arbitrage métier ni d'accès au réel. La décision future sur le procédé de comptage de la source, déjà signalée dans le livrable, reste distincte de la clôture technique.

## 6. Études (lots sans code)

Sans objet pour le classement du lot, qui contient du code. L'encart « standard d'abord » fournit des références officielles et des contrôles sur le code installé dans le banc. Les pages externes n'ont pas été consultées pendant cette relecture, conformément à l'interdiction d'accès à un site ; aucune confirmation documentaire externe supplémentaire n'est revendiquée.

## Verdict

**À corriger.** Ce verdict n'est pas un GO.

- **Bloquant : R1** — le paquet final ne qualifie plus les dépendances actuelles et ses deux vérificateurs échouent.
- **Important : R2** — certaines références opaques sont exclues comme absentes.
- **Important : R3** — une contradiction entre référence et lien peut encore être publiée sous un type SEPA ou PayPal déterminé.
- **Mineur :** aucun point supplémentaire retenu.

Les refus d'accès aux temporaires sont une limite d'exécution de cette relecture, distincte des trois corrections ci-dessus.
