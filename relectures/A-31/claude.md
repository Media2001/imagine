# Relecture indépendante — Lot A-31 (historique des commandes, comptées)

Relecteur : Claude, indépendant. Date : 2026-11-27. Je n'ai pas ouvert `codex.md`. Pas de fusion à ce stade.

## Rejeu de la suite PHP (commande autorisée, sans argument)

Commande exacte :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Conteneur jetable, réseau coupé, dépôt monté en lecture seule (`mount=/mnt/c/Users/Ced/imagine/wp:/repo/wp:ro`).

- **1re passe** — dernière ligne :
  `REJEU : 0 tests, 0 assertions, 0 échecs, 1 erreurs, 0 ignorés — FAIL`
- **2e passe** — dernière ligne :
  `REJEU : 1167 tests, 36333 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

Lecture : l'outil A-31 passe dans **les deux** rejeux (`T01 TOOL : a31 ; 31 controls ; 0 failures ; exit=0`). L'erreur de la 1re passe n'est pas une assertion A-31 : c'est `Get-T01Inspect` du harnais partagé `wp/tests/t01/commun.ps1:44` qui échoue (« Inspection du conteneur impossible. » → `error: no such object: imagine-t01-…`) car le conteneur orchestrateur avait déjà disparu au moment de l'inspection (`PAQUETS : 0 vérifiés, 1 échecs ; … T-03 RUNNER_OUTPUT`). La 2e passe, identique, est verte (`PAQUETS : 12 vérifiés`). C'est un aléa d'infrastructure du runner T01, hors périmètre A-31.

Nota 2e passe : `PAQUETS … 1 échecs ; … A-32 A32_PARTIAL_EVIDENCE` concerne le lot **A-32** (travail en cours, non scellé), pas A-31, et ne fait pas échouer le rejeu.

## 1. Conformité

Le lot compte, ne répare, ne rattache, ne supprime rien. Vérifié : aucune écriture métier, SELECT seuls, `disable_functions` (`confine.py:63-64`), sortie à schéma fermé.

Métriques du brief, toutes présentes (`Analysis.php:34-91`) :
- commandes par année et par année×état, liste fermée Woo + `autre` sans nom de l'état d'extension (`Analysis.php:10-11,54`) ;
- nature en liste fermée, « illisible » jamais rangé d'office, plusieurs natures → illisible (`Inventory.php:79`, `Analysis.php:12,56`) ;
- liens cassés : renouvellements orphelins (`Inventory.php:59-66`), abonnements vivants sans commande d'origine (`Analysis.php:68-73`), commandes à compte disparu (`Inventory.php:153-155`), commande native illisible distincte (`Inventory.php:148-151`, `orders_link_unknown`) ;
- remboursements par année, objet séparé (`Inventory.php:141-146`) ;
- année de la plus ancienne **commande** seulement (refunds exclus) (`Analysis.php:82-89`).

Règles reprises et **signalées** comme reprises, non réécrites :
- « vivant = exactement `active` » repris d'A-19. Vérifié contre la source : `wp/outils/bascule/a19/Analysis.php:63` = `if ($status !== 'active') { continue; }`. Reprise exacte. Conforme à la consigne du brief (« reprends celle d'A-19 telle quelle »).
- Fusion des groupes < 5 (K=5) comme A-20 (`Analysis.php:19-32`).

Import A-28 gelé : lu, non modifié. Défaut prudent après neutralisation : `natures = « inconnu après neutralisation »` (jamais zéro) (`Inventory.php:159`, `Analysis.php:79-80`). Le reste reste lisible. Interprétation explicitée dans le README et la réception.

Mode d'emploi : 8 lignes « standard d'abord » avec sources officielles citées (`README.md:7-20`) ; 2 lignes d'ajout au mode d'emploi d'audit (`readme-ajout.txt`). Livrables présents : outil, tests, `PRET`, `manifest.json`, `rejeu.json`.

**Interprétations faites et signalées** (aucune non déclarée détectée) :
- périmètre = magasin faisant autorité seul, backups classiques/HPOS non additionnés (`README.md:36`, `Inventory.php:99-106`) ;
- année = date de création UTC, jamais paiement/renouvellement (`README.md:37`, `Inventory.php:19-23`) ;
- une référence opaque ne devient jamais un lien numérique absent → pas comptée orpheline (`Inventory.php:38-45,56-67`).

## 2. Exactitude métier — deux cas déroulés à la main

Banc fictif (`seed.php`), par répétition : 10 commandes (1 en 2018, 1 en 2019, 8 en 2020), 3 abonnements, 1 remboursement 2021. Natures attendues : parent, renewal (×2 : la commande renewal + l'orphelin numérique 987654321), switch, resubscribe, none (×3), illisible (×2 : valeur opaque + clé d'extension Stripe).

**Cas A — 5 répétitions (sans fusion).** Déroulé manuel :
- années : 2018→5, 2019→5, 2020→40 ;
- états : 2018 completed 5, 2019 completed 5, 2020 completed 35, 2020 autre 5 (l'état canari `a31canary`) ;
- natures : parent 5, renewal 10, switch 5, resubscribe 5, none 15, illisible 10 ;
- orphan_renewals 5 ; living_without_parent 5 (l'actif à parent 0 ; le `cancelled` exclu) ; orders_missing_account 5 ; refunds 2021→5 ; oldest 2018.

Concorde trait pour trait avec l'oracle `expected.py:11-23` et les assertions natives `unit.php` / `adapter-unit.php`.

**Cas B — 1 répétition (fusion K=5).** Déroulé manuel : seules 2020 (8) et 2020/completed (7) dépassent 5 ; tout le reste se fond en `autres` (natures autres 10, orphan autres 1, structural autres 2, refunds autres 1). oldest : la plus petite année (2018, count 1 < 5) → `fusionne`, **jamais** 2020. Concorde avec `expected.py:5-10` et le test `oldest_not_next_visible_year` (`unit.php:56-57`).

Cas limites vérifiés au code et testés : état inconnu → `autre` sans nom (`unit.php:30-34`) ; nature inconnue → `illisible`, jamais `none` (`unit.php:35-37`) ; date invalide → oldest `illisible` (`unit.php:61-64`) ; neutralisation → natures inconnu mais orphelins/années lisibles (`unit.php:65-70`) ; référence malformée/opaque/débordante → illisible et non orpheline (`adapter-unit.php:82-95`) ; référence absente jamais résolue par le getter qui journalise (`adapter-unit.php:78-81`, lecture seule préservée).

## 3. Tests

- Passent au 2e rejeu (voir ci-dessus) ; 31 contrôles A-31 verts dans les deux passes.
- Couvrent les cas limites, pas seulement le nominal : fusion aux bornes 1/4/5, oldest rare, exclusions A-19 état par état (`unit.php:52-54`), natures mixtes, contradiction du lecteur natif, UTF-8 **et** cp1252 (`matrix.py:54`).
- Les tests vérifient la règle, pas le code : le témoin RED (`run.py:93-100`) mute `< 5` en `< 6` et exige que `renewal_five` tombe — preuve que le test K=5 est discriminant. Le test de gel exécute le **vrai** `Engine::neutraliser()` puis `anonymiser()` (`neutralise.php:33-47`), il ne simule pas.

## 4. Sécurité et données

- Aucun secret. Fixtures en `@example.org` et noms manifestement inventés (`A31_…_PRIVATE_CANARY`).
- Canaris (état, compte, lien, remboursement) absents des sorties : testé (`unit.php:34`, et réception « 11 témoins observés puis détruits »).
- Lecture seule tenue : confinement exigé (`Command.php:21-23`), SELECT only, écritures interdites, sortie parent-only et symlinks refusés (`confine.py:47-54`, `report.py`).
- Schéma public fermé sans montant, ID commande/compte/abonnement, email, jour ni heure (`report.py:35-64`). Seul lien technique = SHA-256 de l'audit.
- Pas de sortie de texte réservé (lot sans paywall).

## 5. Doctrine

- Standard d'abord : getters natifs WCS/Woo cités et empreinte du code **installé** avant le sujet (`standard.php`, `README.md:22`). Le sur-mesure se limite au comptage.
- Logique métier en PHP pur, testable sans WordPress (`Analysis.php`, sonde `pure-probe.php`).
- Conventions §5 : `declare(strict_types=1)`, namespace `Imagine\`, PSR-12 strict annoncé sans erreur ni avertissement.

## Verdict

**Conforme** (la relecture n'est pas un GO ; A-22 non clos).

Points classés :

- **Bloquant** : aucun.
- **Important** : aucun imputable à A-31. À signaler néanmoins : le rejeu canonique partagé (T01, `wp/tests/t01/commun.ps1:44`) peut échouer de façon non déterministe sur l'inspection du conteneur orchestrateur (« no such object »), comme à ma 1re passe. Cela peut bloquer une clôture par intermittence sans défaut du lot.
- **Mineur** :
  1. Sous K=5, les trois métriques `structural_links` (living_without_parent, orders_missing_account, orders_link_unknown) partagent un même `autres`, qui additionne des unités différentes quand chacune est rare (`Analysis.php:40-48`, pool unique). C'est déclaré et prudent (anonymisation), mais rend ces métriques indistinctes dans le cas fusionné.
  2. Cas limite non couvert par une fixture : un abonnement **à la corbeille**. Le code l'inclut dans le recensement d'existence (donc un renouvellement vers lui n'est pas orphelin) et le refus est fermé si l'objet ne se charge pas (`Inventory.php:117-121`). Comportement raisonnable mais non prouvé par un test.

## Décisions techniques, défaut proposé

- *Aléa du rejeu T01.* Défaut : traiter l'échec « Inspection du conteneur impossible / no such object » comme un aléa d'infrastructure à rejouer, non imputable à A-31 (confirmé : 2e passe verte, résultats A-31 identiques). Durcissement éventuel (retenter/tolérer l'absence dans `Get-T01Inspect`) relève du harnais partagé, hors A-31 ; Hermès applique le défaut sans attendre.
- *Abonnement à la corbeille.* Défaut : ajouter au banc une fixture « abonnement à la corbeille » pour prouver qu'il compte à l'existence (renouvellement non orphelin) sans compter comme vivant. Défaut prudent conservé en l'absence du test.
- *`autres` mixte des liens structurels.* Défaut : conserver le pool unique (anonymisation K=5 prime), la note « unités différentes » du README étant explicite.

## Pour Imagine

Aucune question métier ouverte ; aucune question visuelle ou touchant au réel. Les règles de comptage sont fermées et reprises des lots amont (A-19, A-20).
