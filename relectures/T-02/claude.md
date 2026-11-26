# Relecture T-02 — Rejeu des tests purs des outils (Claude)

Relecteur indépendant. Je n'ai pas lu `codex.md`. Pas de fusion à ce stade.

## Rejeu exécuté (commande autorisée, sans argument)

Commande lancée depuis la racine :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Code de sortie : **0**. Dernière ligne :

```
REJEU : 1123 tests, 34569 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Ligne ajoutée juste avant (nouvelle, conforme au brief) :

```
OUTILS : 13 outils, 242 contrôles, 0 échecs ; hors rejeu : aucun
```

Détail des 13 banques jouées : a02-audit 17, a03-non-regression 10, a10 10, a11 19, a12 15, a14 8, a15 14, a16 23, a17 42, a18 37, a19 9, a20 23, a21 15. Somme = **242 contrôles, 0 échec**.

Isolation constatée dans ma propre sortie, inchangée : `network=none ; rootfs=ro ; mount=/mnt/c/Users/Ced/imagine/wp:/repo/wp:ro ; ports=none ; cap-drop=ALL ; no-new-privileges`, vérifiée avant et après le démarrage. Balayage des orphelins au départ, puis `T01 CLEANUP : absence verifiee de imagine-t01-611dfc4e…` : **aucun conteneur ne reste**. Je n'ai pas pu relancer `docker ps` à la main (le bac à sable a bloqué l'appel WSL/docker) ; je m'appuie sur la vérification d'absence que le script fait lui-même après `rm -f` (`commun.ps1:60-65`) et sur le code 0.

Intégrité : les empreintes SHA-256 des 8 sources (`rejouer.ps1`, `t01/executer.php`, `t01/tools.php`, `t01/tools-contract.php`, `t01/corrections-php.php`, `t01/mock-wsl.ps1`, `t01/test-tools.ps1`, `t01/test-tools-summary.ps1`) sont **identiques** à `production/T-02/verification.json`. Ce que je relis est ce qui a été rejoué et scellé.

## 1. Conformité

- **Même commande, sans argument, joue en plus les banques pures.** Vérifié en vrai. `rejouer.ps1:14` refuse tout argument. Conforme.
- **Découverte automatique des `wp/tests/<lot>/unit.php` immédiats, triés.** `tools.php:6-52` (`discoverT01Tools`) : sous-dossiers immédiats de `wp/tests`, nom validé `^[a-z0-9][a-z0-9-]*$`, tri par lot. 13 banques présentes, 0 exclusion. Conforme au périmètre « unit.php » du brief.
- **« hors rejeu » avec raison.** `tools.php:35-46` lit `unit.hors-rejeu` (raison ≤120 car., une ligne), liste le lot sans le lancer. Aucune banque actuelle n'en a besoin (les 13 tournent bien en PHP pur), d'où `hors rejeu : aucun` — correct.
- **Une ligne ajoutée avant la dernière.** `rejouer.ps1:71` écrit la ligne `OUTILS` ; la ligne `REJEU` (72) garde sa forme `REJEU : … — PASS|FAIL`. Conforme.
- **Dernière ligne à `FAIL` si une banque échoue.** Tracé à la main (voir §2), et prouvé en vrai par `production/T-02/preuves/final/utf8/outil-rouge.log`. Conforme.
- **Ajouter un outil ne touche pas la commande.** Le `Dockerfile` ne cuit que `/opt/t01` (caches vendor) et `verifier-image.php` ; `executer.php`, `tools.php` et les `unit.php` sont lus depuis le **montage lecture seule** `/repo/wp`, jamais dans l'image. Donc une banque de plus = aucun changement de commande ni d'image. Confirmé : mon rejeu vert a tourné sur l'image pré-existante (`sha256:46b2fb81…`) sans aucune reconstruction. Conforme.
- **Convention écrite en trois lignes dans le mode d'emploi de T-01.** `production/T-01/notes.md:21-23` : trois puces (découverte auto de `unit.php` + `unit.hors-rejeu` ; sous-processus séparés et relocalisation des chemins ; matrices natives/Python hors commande). Conforme.
- **Isolation non assouplie, aucun script nouveau à autoriser.** Les options Docker de T-01 sont reprises telles quelles (`rejouer.ps1:29`). Conforme.
- **Matrices natives (classique/HPOS, commerciales) et suites Python hors de cette commande.** Dit en une phrase dans `notes.md:23` de T-01 et dans la note T-02. Conforme.
- **Lots clos non régénérés.** Aucune preuve close touchée ; seules les banques `unit.php` existantes sont rejouées, pas réécrites. Conforme.
- Périmètre : la découverte ne capte que les `unit.php`. Les suites `*-runner` plus anciennes de `wp/tests/` restent hors rejeu de cette commande — c'est le périmètre explicite du brief, pas un oubli.

## 2. Exactitude — cas déroulés à la main

**Cas A — une banque passe au rouge (le cœur du brief).** Trace : `tools.php:98-162` relance chaque `unit.php` dans un sous-processus PHP ; un `check` `FAIL`, un `exit_code` non nul, un reçu absent/invalide/vide, un lien symbolique ou la moindre sortie sur `stderr` force `failures ≥ 1` (lignes 119-155, `max(1, …)`). `executer.php:200` : `pass = pass && … && $toolTotals['failures'] === 0` → `pass=false`. `rejouer.ps1:57` lève dès `toolResult.failures > 0` → `exitCode=1` → dernière ligne `… — FAIL`. Les totaux PHPUnit (`tests`, `assertions`) ne bougent pas : les outils tournent dans un **sous-processus distinct, après** PHPUnit, et sont comptés dans une clé `tools` séparée (`executer.php:192-201`). 
Confirmé par la preuve réelle `preuves/final/utf8/outil-rouge.log` : rejeu réel sur un **miroir jetable** du dépôt (montage `scratch/imagine-t02/…:/repo/wp:ro`), `T01 TOOL : a10 ; 10 controls ; 1 failures ; exit=1`, puis `REJEU : 1123 tests, 34569 assertions, 0 échecs, 1 erreurs, 0 ignorés — FAIL`. Les 1123/34569 PHPUnit sont préservés. Le dépôt réel n'a pas été modifié (miroir hors dépôt), puis remis en état : mon propre rejeu vert de ce jour montre a10 de nouveau à 0 échec. Exact.

**Cas B — une banque exige WordPress/base/commerciale.** Trace : `discoverT01Tools` lit `unit.hors-rejeu`, ajoute le lot à `excluded` avec sa raison, et **ne l'exécute pas** (`tools.php:39-46`, `continue`). La ligne `OUTILS` l'affiche en « hors rejeu : <lot> (<raison>) ». Couvert par les contrats `tools-contract.php:53-60` et `:166-173` (le code natif marqué n'est jamais lancé). Exact.

**Cas C — garde-fou « échoue fermé ».** Reçu manquant, JSON invalide, reçu vide, statut inconnu, booléen `false`, avertissement PHP : tous forcent l'échec (`tools.php:119-155`, batterie `tools-contract.php:135-151`). Exact.

**Cas D — relocalisation des seuls littéraux de chemin.** `relocateT01Unit` (`tools.php:54-77`) ne réécrit que les `T_CONSTANT_ENCAPSED_STRING` dont le préfixe est `/subject`, `/checkout`, `/report`, `/unit-origin-fixture` suivis de `/` ou du guillemet fermant ; les commentaires et les quasi-homonymes (`/subjective`) sont intacts (contrat `:160-164`). Les sources métier et les banques du dépôt ne sont pas réécrites ; tout écrit reste sous `/tmp`. Exact.

## 3. Tests

- Suite PHP : **1123 tests, 34569 assertions, 0 échec/erreur/ignoré**, identique en UTF-8 et cp1252 (`verification.json`) et à mon rejeu. Le nombre de tests PHPUnit est conservé par l'ajout T-02 (compteurs séparés). Conforme.
- Les banques d'outils vérifient de vraies règles, pas une répétition du code : ex. a10 contrôle la projection des coupons (types récurrents, parsing numérique, métadonnées sérialisées, rejet `A10_META_INVALID`) sur `/subject/a10/Projection.php` — `wp/tests/a10/unit.php`. Satisfaisant.
- Cas limites couverts par les contrats (`tools-contract.php`) : symlink pendant refusé, exit non nul non masqué par un exit 0 de process, totaux PHPUnit préservés sous veto outil, exclusion native non lancée.
- **Réserve de vérifiabilité (note).** Ces contrats et les « doubles de frontière » (`mock-wsl.ps1`) ne sont **pas** joués par la commande autorisée (`rejouer.ps1`, chemin vert uniquement). Un relecteur limité à cette commande + droits lecture seule confirme le VERT directement, mais ne peut rejouer le ROUGE qu'en passant par le paquet de preuves ou, comme ici, en déroulant le code à la main. Le brief est satisfait par le rejeu réel sur miroir (`outil-rouge.log`). Je le signale pour transparence, ce n'est pas un défaut de code.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle. Fixtures `@example.org`.
- Montage `wp/` en **lecture seule**, écritures confinées au tmpfs `/tmp` ; les alias symboliques (`tools.php:92-96`) pointent vers le montage déjà en lecture seule. Pas de réseau, `cap-drop=ALL`, `no-new-privileges`, `user 65534`. Conforme au §3/§4 de la doctrine.
- Liens symboliques refusés à chaque frontière (`discovery.php`, `tools.php:9-38`, `executer.php:11`). Bon.
- Validation stricte du reçu machine côté PowerShell (`rejouer.ps1:41-56`) : compteurs numériques bornés, raison d'exclusion sans retour-ligne, lot au bon format. Bon.

## 5. Doctrine

- Logique métier en PHP pur, testable hors WordPress (§4) : c'est exactement ce que le lot industrialise côté rejeu. Conforme.
- « Tu ajoutes, tu ne réécris pas » : image, isolation et dernière ligne inchangées. Conforme.
- Conventions §5 : `declare(strict_types=1)`, PHP 8.2, échoue-fermé. Conforme.

## Points

**Mineurs**

1. `production/T-02/notes.md:8` — sous « Résultat vérifié », « **11 banques, 204 contrôles** » (A-02…A-19). C'est en réalité le décompte du **miroir rouge** (avant l'ajout de a20/a21), pas celui du dépôt final, qui est **13 banques / 242 contrôles** (`FINALISATION.md`, `verification.json`, mon rejeu). `FINALISATION.md` porte le bon chiffre et dit remplacer `notes.md`. *Correction proposée* : dans `notes.md`, préciser que 11/204 est la photo du miroir, ou aligner sur 13/242, pour qu'un lecteur ne prenne pas 11/204 pour l'état courant. Sans incidence sur le code.

2. Vérifiabilité du ROUGE par la seule commande autorisée (voir §3, dernière puce). *Proposition* : accepter la preuve miroir `outil-rouge.log` telle quelle — n'ajouter aucun levier de mutation dans `rejouer.ps1` (le brief interdit d'élargir la surface). Défaut prudent : statu quo.

**À noter (pas d'action T-02)**

3. L'image **n'avait pas besoin de changer** pour cette fonction (scripts et banques montés, jamais cuits — `Dockerfile`). Mon rejeu vert l'a confirmé sur l'image pré-existante. Le relancement de `preparer-image.ps1` par le parent était une précaution, cohérente avec la règle « si l'image doit changer ».

4. A-19 : 9 contrôles de banque pure + 9 cas PHPUnit sont **deux compteurs de rejeu**, pas 18 règles (`notes.md:19`). Transparent. La question « schéma de passerelle inconnu vs moyen absent », défaut prudent distinct, relève du lot A-19 et de Ced, pas de T-02.

## Décisions techniques, défaut proposé

- *Portée de la découverte aux seuls `unit.php`* (les suites `*-runner`/Python restent dehors). Défaut : conserver — c'est le périmètre explicite du brief. Hermès applique, j'arbitre après coup si besoin.

## Pour Imagine

- Rien. Aucune règle métier nouvelle n'est introduite par ce lot d'outillage.

## Verdict

**Conforme** — avec deux points **mineurs** (alignement du décompte dans `notes.md` ; note de vérifiabilité du cas rouge) et deux notes sans action. Aucun point **bloquant** ni **important**. 

Ce verdict n'est pas un GO : il ne vaut que pour la clôture d'un lot de code, et la fusion avec Codex reste à faire.

## Suite

`relectures/T-02/codex.md` existe mais n'a pas été ouvert, conformément à la consigne. Je m'arrête après la relecture : **pas de fusion** tant qu'elle n'est pas demandée.
