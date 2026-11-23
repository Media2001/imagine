# Relecture T-01 — Commande de rejeu des tests (Claude, relecteur indépendant)

Lot : outillage. Brief : `briefs/T-01-commande-de-rejeu.md`.
Production relue : `wp/tests/rejouer.ps1`, `wp/tests/preparer-image.ps1`, `wp/tests/t01/*`, `production/T-01/`.
Je n'ai pas ouvert `relectures/T-01/codex.md`. Pas de fusion à ce stade.

## Préambule — ce que j'ai pu exécuter

L'environnement de relecture bloque toute exécution de script PowerShell : le test de contrat engendre des processus PowerShell enfants, et l'approbation n'est pas disponible en session non interactive. Je n'ai donc **pas** pu rejouer moi-même `test-rejeu.ps1`, `test-isolation.ps1` ni `rejouer.ps1`. Conformément à la grille (« les lancer ; à défaut, le dire »), je le dis.

À défaut, j'ai :
- lu tout le code de l'outillage ;
- déroulé à la main la logique des cas de contrat contre le double `mock-wsl.ps1` ;
- contrôlé la cohérence interne des preuves réelles d'Hermès (`production/T-01/preuves/`).

Les preuves sont cohérentes : `final-rejeu.log` finit sur `REJEU : 802 tests, 33367 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS` ; les sous-totaux concordent (connecteur 37 + pilotage 765 = 802 ; assertions 224 + 33143 = 33367) ; `final-verification.json` porte `ready: true` avec empreintes des bibliothèques et des scripts inchangées.

## 1. Conformité

Le brief est satisfaisant, point par point.

- **Suite complète, toutes les extensions sur mesure.** `wp/tests/t01/executer.php:68` découvre `/repo/wp/plugins/*/composer.json`. J'ai vérifié : exactement deux bibliothèques (`imagine-pilotage`, `imagine-connecteur`), aucune autre `composer.json`/`phpunit.xml` ailleurs sous `wp/`. `executer.php:40-62` (verifyCoverage) exige que les `<testsuite>` du `phpunit.xml` racine couvrent **tous** les `*Test.php` de `tests/`, chacun une fois — un fichier de test oublié fait échouer le rejeu. Bon garde-fou contre une suite partielle.
- **Conteneur jetable, sans réseau, dépôt en lecture seule, dépendances pré-préparées.** `rejouer.ps1:25` : `--network none`, `--read-only`, montage `type=bind,...,readonly`, `--pull never`, `--cap-drop ALL`, `--security-opt no-new-privileges`, `--user 65534:65534`, `--tmpfs /tmp`, limites pids/mémoire/cpu, entrypoint `timeout 600`. Les dépendances viennent du cache de l'image `/opt/t01` (`executer.php:76-92`), avec refus d'un `vendor` hôte (`executer.php:90`) et refus des liens symboliques (`executer.php:11`).
- **N'écrit rien, ne laisse aucun conteneur.** Dépôt monté en lecture seule, écritures en tmpfs seulement ; `probe-isolation.php` prouve concrètement que l'écriture dans `/repo` et hors tmpfs échoue. Nettoyage en `finally` (`rejouer.ps1:47-50`) via `Remove-T01Container`, qui **vérifie la propriété par label avant `rm -f`** (`commun.ps1:37`) puis **prouve l'absence** du conteneur (`commun.ps1:39-43`). Un nettoyage raté force le code 1.
- **Dernière ligne stable + code 0/1.** `rejouer.ps1:52-56`. Format exact, é et tiret cadratin par points de code. La preuve réelle (`final-rejeu.log:994`) et le vérificateur (`verifier-t01.py:38-40`) confirment le format attendu. Cas d'échec réel vérifié : `preuves/rejeu-reel-image-absente.log` → `0 tests, …, 1 erreurs … — FAIL`, code 1.
- **Échec clair si Docker ou l'image manquent, sans rien installer.** `rejouer.ps1:13` (Docker) et `:15` (image absente, avec remédiation nommant `preparer-image.ps1`). Aucun `pull`, aucun `install`.
- **Pas de bancs commerciaux ni de création de site.** Seules les bibliothèques `wp/plugins/*` à `composer.json` sont jouées ; aucune opération de staging.
- **Script de préparation séparé.** `wp/tests/preparer-image.ps1` existe, n'est jamais appelé par le rejeu (`rejouer.ps1` ne le référence pas).
- **Livrables.** Deux scripts, preuve d'exécution complète (`preuves/final-rejeu.log`, `preparation-20261123-1350.log`), `production/T-01/notes.md` en cinq lignes, `production/T-01/PRET`. ✔

**Mineur C1.** Interprétation « extensions sur mesure = `wp/plugins/*/` ayant un `composer.json` ». Elle est juste aujourd'hui, mais n'est pas posée explicitement comme choix (doctrine §1 : « j'ai compris X »). `notes.md:3` la sous-entend seulement. Une extension sur mesure future placée hors `wp/plugins` (mu-plugins, thème) serait silencieusement ignorée.

## 2. Exactitude (logique de l'outil déroulée à la main)

Pas de règle métier ici ; j'ai déroulé les cas de comportement de l'outil.

- **Agrégation multi-bibliothèques.** `executer.php:111` lit `$document->testsuite[0]`. Vérifié sur `final-rejeu.log` : PHPUnit 11 enveloppe chaque configuration dans un **unique** `<testsuite>` racine portant les totaux complets (pilotage `tests="765"` à la ligne 106 ; connecteur `tests="37"` à la ligne 21). `testsuite[0]` capte donc bien l'agrégat — pas de sous-comptage malgré les 6 testsuites configurées de pilotage.
- **Autoload PSR-4 inter-paquets.** `imagine-connecteur/composer.json:12` mappe `Imagine\Pilotage\Entreprise\` vers `../imagine-pilotage/src/Entreprise/`. `executer.php:73-95` copie **tous** les paquets en frères sous `/tmp/t01/plugins/` avant de lancer le moindre test, donc le chemin relatif résout. Le `vendor` du cache est relogeable (chemins calculés depuis `__DIR__`). Les 802 PASS le confirment.
- **PASS/FAIL cohérent.** Un exit conteneur non nul avec 0 échec/0 erreur fait lever `rejouer.ps1:42`, et le `catch:46` force `errors=1` : le résumé affiche alors « 1 erreurs — FAIL », sans contradiction « 0 erreurs mais FAIL ». Déroulé contre `mock-wsl.ps1` (cas `malformed`, `start-error`, `create-error`, `cleanup-error`) : comportement conforme.

## 3. Tests

- **Je n'ai pas pu les relancer** (voir préambule). Les preuves fournies passent au vert et sont cohérentes.
- **Deux niveaux de tests, bien séparés.** `test-rejeu.ps1` : 10 cas de rejeu + 3 cas de préparation, double WSL/Docker injecté, aucun PHP réel — vérifie codes de sortie, ligne de résumé, preuve de nettoyage, message de remédiation. `test-isolation.ps1` : vrais appels Docker hors ligne sur une image publique synthétique, prouve read-only/réseau coupé et le refus de dépendances absentes par `executer.php` — **sans** jouer la vraie suite. Le périmètre de chaque test est honnêtement annoncé (« NOT a PHP-suite receipt »).
- **Les tests vérifient la règle, pas seulement le code.** Le contrat teste des chemins d'erreur réels (Docker absent, image absente, démarrage/création/nettoyage en échec, montage non conforme, image non conforme) et pas uniquement le cas nominal.

**Mineur T1.** Trous de couverture du contrat : le refus d'argument (`rejouer.ps1:12`) n'est jamais testé ; l'assainissement du chemin WSL (refus virgule/saut de ligne, `rejouer.ps1:22`) non plus ; le refus par `ExposedPorts` ou par label d'image incohérent n'est pas couvert séparément (`unsafe-image` ne teste que `Volumes`).

**Mineur T2.** `pass` ignore les tests `skipped` (`executer.php:135`) ; aucune option `--fail-on-skipped` / `--fail-on-incomplete`. Le compte « ignorés » reste affiché (donc visible, non masqué), mais un `markTestSkipped` futur passerait en PASS. À considérer : faire ressortir `ignorés > 0` ou ajouter ces drapeaux.

## 4. Sécurité et données

Point fort du lot.

- **Aucun secret, aucune donnée réelle.** `preparer-image.ps1:20-24` ne copie que `composer.json`/`composer.lock` dans le contexte de build (commentaire ligne 24 : ni dépôt, ni site, ni config, ni identifiants). Contexte temporaire hors dépôt, supprimé en `finally` (`preparer-image.ps1:41`).
- **Chaîne d'approvisionnement.** Build avec `--no-scripts --no-plugins` (`Dockerfile:14`), `allow-plugins: false` dans les deux `composer.json`, versions figées par `composer.lock`, image vérifiée hors ligne (`verifier-image.php`). Au rejeu, le cache de l'image est lié aux manifestes source par empreinte SHA-256 (`executer.php:80`) : un `composer.lock` modifié depuis la préparation fait échouer clairement.
- **Isolation durcie** (voir §1) + droits : nettoyage refusé si le label de propriété ne correspond pas (`commun.ps1:25-28`).
- **Paywall** : hors périmètre de ce lot (outillage).

**Mineur S1.** Moindre privilège : `rejouer.ps1:25` monte **tout** le dépôt en lecture seule alors que `executer.php` ne lit que `/repo/wp/plugins`. Monter seulement `wp/plugins` réduirait la surface (docs, `.git`). Non bloquant (lecture seule + réseau coupé neutralisent le risque).

## 5. Doctrine

- **Conventions §5.** `declare(strict_types=1)` partout en PHP ; PHP 8.2 (`Dockerfile:3`) ; messages opérateur et résumé en français ; aucun code tiers modifié. ✔
- **Tests d'abord / rejouable / non-régression.** L'outil sert précisément l'idempotence de la vérification : image préparée une fois, rejeu déterministe (`--do-not-cache-result`, conteneur neuf à chaque fois).

**Mineur D1.** Deux reçus coexistent dans `preuves/` : `final-verification.json` (`preparation_executed: false`) et `livraison-verifiee.json` (`preparation_executed: true`). `notes.md:5` explique l'écart (le premier décrit le vérificateur, qui ne prépare jamais l'image). Reste deux points à clarifier : (a) la coexistence prête à confusion ; (b) `livraison-verifiee.json` n'est produit par aucun script versionné que j'aie relu — sa provenance n'est pas traçable dans le dépôt.

## Verdict

**Conforme**, sous une réserve de méthode : je n'ai pas pu rejouer la suite moi-même dans mon environnement ; mon avis repose sur la lecture du code et sur les preuves réelles d'Hermès, cohérentes entre elles. Mon verdict n'est pas un GO.

Points classés :
- **Bloquant** : aucun.
- **Important** : aucun.
- **Mineur** : C1 (interprétation du périmètre à expliciter), T1 (trois chemins non testés), T2 (`skipped` n'échoue pas), S1 (monter `wp/plugins` plutôt que tout le dépôt), D1 (deux reçus / provenance de `livraison-verifiee.json`).

Rappel procédure : `codex.md` existe déjà, mais la consigne est de ne pas l'ouvrir et de ne pas fusionner à ce stade. Je m'arrête après ce rapport.
