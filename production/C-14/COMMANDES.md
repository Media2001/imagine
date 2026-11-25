# C-14 — commandes et résultats réels

Exécution finale le **25 novembre 2026**, sur Windows/bash, depuis `C:/Users/Ced/imagine`. Seul site : `imagine-test-demo`. PHP de la démo **8.3.32**, WordPress **7.0.9**, WooCommerce **11.2.2**, HPOS **yes** (versions lues, pas modifiées).

## Image publique obligatoire — exécutée, code retour 0

```bash
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:/Users/Ced/imagine/wp/tests/preparer-image.ps1
```

Dernier résultat : `T01 IMAGE READY : PHP 8.2.33; 3 packages; no site or commercial extension`, image vérifiée `sha256:30ef247ddf39ffdd701976472d7fa99fe88998e7de1344edc92c3ae2c6d199e5`.

Les lignes PowerShell `System.Management.Automation.RemoteException` répercutent stderr de BuildKit ; la construction, la vérification hors réseau et le script ont réellement terminé **0**. Avertissements explicites : T01 ne découvre pas les tests de `plugins/imagine-site` ni du thème. **Le total C14 ci-dessous vient de ses runners dédiés, pas du runner T01.** Aucun script T01 ni manifeste de bibliothèque n'est modifié.

## Installation puis rejeu sans reset — exécutés, code retour 0 chacun

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c14.py --deploy
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c14.py
```

Les deux exécutions finales ont donné **536/536** contrôles, sans échec :

| Suite | Contrôles réussis |
|---|---:|
| Règle PHP pure C14, conteneur hors réseau | 21 |
| C14 natif WP/Woo HPOS, canaris nettoyés | 50 |
| C14 HTTP/cookies natifs/REST/PDF | 31 |
| C08 natif | 30 |
| C09 natif, V-NUM compris | 379 |
| C11 natif | 25 |
| **Total du rejeu** | **536** |

Le mode `--deploy` ne réinstalle que les quatre fichiers C14 du plugin, les scripts C09/C14 ciblés et le profil P-NUMERO. Le mode sans argument ne réinitialise aucun profil ; il relit les octets du code distant, téléverse les recettes, teste et restaure. Il n'est pas strictement read-only : des canaris synthétiques sont créés/supprimés et les tests HTTP exercent les états de la commande de fixture avant restauration.

`resultats.json` contient le dernier rejeu. États partagés C08/C09/C10/C11/C12/C13 et bibliothèques closes comparés avant/après, conservés. Les 50 contrôles natifs comprennent la pagination sur 51 commandes synthétiques, les suppressions, remboursements, erreurs de lecture, champ produit et refus client. Les 31 HTTP comprennent de vraies sessions, un nonce REST natif, les octets exacts du PDF autorisé, le refus de l'autre numéro et les anciens accès média directs.

## Non-régression complémentaire — exécutée, code retour 0

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c14-regressions.py
```

| Suite | Résultat |
|---|---:|
| PHPUnit C11 | 36 tests, 200 assertions |
| PHPUnit C12 | 7 tests, 63 assertions |
| C12 natif | 32/32 contrôles |
| C12 HTTP | 85/85 contrôles |
| Unitaires locaux `test_*.py` | 33/33 tests |
| **Total complémentaire** | **193/193 tests/contrôles** |

`regressions.json` contient ces résultats. Les deux suites PHPUnit utilisent des conteneurs hors réseau, retirés par nom/propriété puis absence relue. Les six wheels B01 sont réutilisées hors installation pour les 33 unitaires. Aucun rapport C11/C12/C13 existant n'est réécrit. Les 536 et 193 donnent **729 contrôles/tests dans deux reçus distincts** ; les assertions PHPUnit ne sont pas ajoutées une seconde fois.

## PSR-12 — exécuté après la dernière écriture de code, retour 0 sans sortie

```bash
wsl.exe -d Ubuntu -- docker run --rm --pull never --network none --read-only --tmpfs /tmp:rw,nosuid,nodev,size=16m,mode=1777 --cap-drop ALL --security-opt no-new-privileges --user 65534:65534 --mount type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly --entrypoint php imagine-tests-t01:1 /opt/t01/imagine-pilotage/vendor/bin/phpcs --standard=PSR12 /repo/wp/plugins/imagine-site/AchatNumero.php /repo/wp/plugins/imagine-site/AchatsNumeros.php
```

## Incidents corrigés, pas de blocage restant

- Le premier test pur était rouge (classe C14 encore absente), puis vert.
- Woo garde un total de remboursement en cache après un `delete()` brut ; la lecture des droits interroge donc directement les remboursements natifs par parent. Les témoins partiel et total utilisent deux commandes, sans purge artificielle du cache du sujet.
- Passer manuellement une commande à `refunded` peut créer un remboursement natif : le scénario de doublon utilise une annulation, et les véritables remboursements ont leurs propres tests.
- Les oracles C09 « 30/45 jours à partir de maintenant » devenaient faux deux jours après le seed : ils mesurent désormais à partir de `imagine_c09_seeded_at`, sans modifier les dates ni reconstruire les profils.
- Les témoins HTTP ciblent les slugs B00 exacts et leur sentinelle de fin ; un texte complet concaténé sans HTML et une recherche générique qui sélectionnait un article C12 n'étaient pas des oracles fiables.
- Extraction web directe indisponible : documentation officielle lue avec le navigateur. Premier PHPCS refusé faute de répertoire temporaire inscriptible dans le conteneur read-only ; rejoué avec tmpfs, puis conventions corrigées et contrôle final vert.

Lecture finale séparée : **0 utilisateur temporaire C14, 0 contenu/produit temporaire C14, 0 remboursement restant** ; seul le produit de profil conservé subsiste. `production/C-14/PRET` est absent, conformément à la délégation.
