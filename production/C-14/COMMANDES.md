# C-14 — commandes et résultats actuels des corrections

Exécution finale le **25 novembre 2026**, sur Windows/bash, depuis `C:/Users/Ced/imagine`. Seul site : `imagine-test-demo`. PHP de la démo **8.3.32**, WordPress **7.0.9**, WooCommerce **11.2.2**, HPOS **yes** (versions lues, pas modifiées).

## Image publique obligatoire — exécutée, code retour 0

```bash
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:/Users/Ced/imagine/wp/tests/preparer-image.ps1
```

Résultat enregistré dans `validation-image.log` : `T01 IMAGE READY : PHP 8.2.33; 4 packages; no site or commercial extension`, image vérifiée `sha256:3f05efd8b5f8177f26d30b29895262ef867b3de5c2515cbd919bfb7c3927aed1`.

Les lignes PowerShell `System.Management.Automation.RemoteException` répercutent stderr de BuildKit ; préparation/vérification ont terminé **0**. T01 découvre désormais le paquet racine `imagine-site` C13 préservé et `tests/AchatNumeroTest.php`. Le thème reste signalé sans PHPUnit ; aucune couverture fictive. Aucun runner/manifeste/lock fermé modifié.

## Rejeu parent en une commande

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c14-validation.py
```

La commande exécutée pour livrer est `PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c14-validation.py --prepare --deploy-code` : préparation publique, T01 complet, C14 avec code seul, régressions, PSR12, lecture finale du nettoyage et comparaison de l’état partagé/PRET. `validation-corrections.json` enregistre les argv exacts, codes 0 et empreintes ; journaux `validation-*.log`. Le rejeu parent sans options ne prépare pas de dépendances et ne réinitialise aucun profil.

La commande `powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:/Users/Ced/imagine/wp/tests/rejouer.ps1` donne **1012 tests, 34006 assertions, 0 échec/erreur/ignoré — PASS**, dont paquet site 48/258 et règles C14 2/28. Les suites ci-dessous recouvrent T01, ce ne sont pas des nombres de tests tous distincts.

## Installation puis rejeu sans reset — exécutés, code retour 0 chacun

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c14.py --deploy-code
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c14.py
```

Installation ciblée et rejeux finaux : **686/686** contrôles, sans échec :

| Suite | Contrôles réussis |
|---|---:|
| Règle PHP pure C14, conteneur hors réseau | 24 |
| C14 natif WP/Woo HPOS, canaris nettoyés | 51 |
| Complément natif corrections C14 | 45 |
| C14 HTTP/cookies natifs/REST/PDF, corrections incluses | 132 |
| C08 natif | 30 |
| C09 natif, V-NUM compris | 379 |
| C11 natif | 25 |
| **Total du rejeu** | **686** |

`--deploy-code` installe les quatre sources C14 par comparaison et relecture d’octets, **sans reset de P-NUMERO ni réinstallation de seeds C09**. Bootstrap C13/B02 conservé. Le mode historique `--deploy`, qui réinitialise le seul P-NUMERO, n’a pas été utilisé pour ces corrections. Sans argument : vérification du code, téléversement des recettes, tests/restauration ; pas read-only (canaris jetables et états temporaires de la commande de fixture).

`resultats.json` contient le dernier rejeu. Comparaison avant/après : fixtures/réglages/historique C13, fichiers C13/MonCompte, thème et bibliothèques closes, conservés lors des rejeux finaux. Natifs : paiement/propriétaire, pagination 51 commandes, catalogue indépendant, numéro dépublié, instantané retiré, deux modes de remboursement à deux numéros. HTTP : vraies sessions/nonce REST, octets PDF exacts et refus, mêmes mutations et vrais POST `options.php` avec nonce/capacité/persistance.

## Non-régression complémentaire — exécutée, code retour 0

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c14-regressions.py
```

| Suite | Résultat |
|---|---:|
| PHPUnit via runner C11, sélection `tests/` C11+C13+C14 | 48 tests, 258 assertions |
| PHPUnit C12 | 7 tests, 63 assertions |
| C12 natif | 32/32 contrôles |
| C12 HTTP | 85/85 contrôles |
| Unitaires locaux `test_*.py` | 33/33 tests |
| **Total complémentaire** | **205/205 tests/contrôles** |

`regressions.json` contient ces résultats (avec sélection et horodatage). Conteneurs hors réseau nettoyés par nom/propriété et absence relue. Wheels B01 réutilisées sans installation pour Python. Aucun rapport C11/C12/C13 réécrit. Les assertions PHPUnit ne sont pas comptées comme des tests supplémentaires ; pas de total unique entre suites recouvrantes.

## PSR-12 — exécuté après la dernière écriture de code, retour 0 sans sortie

```bash
wsl.exe -d Ubuntu -- docker run --rm --pull never --network none --read-only --tmpfs /tmp:rw,nosuid,nodev,size=16m,mode=1777 --cap-drop ALL --security-opt no-new-privileges --user 65534:65534 --mount type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly --entrypoint php imagine-tests-t01:1 /opt/t01/imagine-site/vendor/bin/phpcs --standard=PSR12 /repo/wp/plugins/imagine-site/AchatNumero.php /repo/wp/plugins/imagine-site/AchatsNumeros.php /repo/wp/plugins/imagine-site/tests/AchatNumeroTest.php
```

## Incidents et limites explicites

- RED correction C14-01 : oracles catalogue/dépublication rouges avant changement ; GREEN après instantané seul. RED C14-02 : méthode de portée pure absente, puis GREEN (2 tests/28 assertions intégrés T01).
- Woo garde un total de remboursement en cache après un `delete()` brut ; la lecture des droits interroge donc directement les remboursements natifs par parent. Les témoins partiel et total utilisent deux commandes, sans purge artificielle du cache du sujet.
- Passer manuellement une commande à `refunded` peut créer un remboursement natif : le scénario de doublon utilise une annulation, et les véritables remboursements ont leurs propres tests.
- Les oracles C09 « 30/45 jours à partir de maintenant » devenaient faux deux jours après le seed : ils mesurent désormais à partir de `imagine_c09_seeded_at`, sans modifier les dates ni reconstruire les profils.
- Les témoins HTTP ciblent les slugs B00 exacts et leur sentinelle de fin ; un texte complet concaténé sans HTML et une recherche générique qui sélectionnait un article C12 n'étaient pas des oracles fiables.
- Extraction web directe indisponible : documentation officielle lue avec le navigateur. Premier PHPCS refusé faute de répertoire temporaire inscriptible dans le conteneur read-only ; rejoué avec tmpfs, puis conventions corrigées et contrôle final vert.

- Nouvel oracle HTML corrigé après lecture du vrai `selected='selected'` et de ses espaces natifs ; aucun comportement métier assoupli.
- Deux premiers diagnostics C11 hors transaction ont ajouté **12 observations synthétiques C13** (77/79, 14:25:02 et 14:28:30 UTC), via les plans temporaires. Aucun événement historique effacé/modifié ; inventaire exact `incident-observations-c13.json`. Pour empêcher la répétition sans supprimer ces observations append-only, seul ce banc C11 passe désormais dans une transaction InnoDB rollbackée, callbacks compris, sans cache objet externe. Égalité finale des états/historiques vérifiée par lectures distinctes. L’incident initial reste signalé au parent.
- Tous les remboursements de cette correction sont **zéro euro**, objets Woo natifs, sans passerelle/restock/transfert. Pour un partiel non ventilé zéro, filtre officiel borné à l’ID possédé (sinon Woo confond 0=0 avec un complet). Le complet natif utilise les deux quantités entières et le statut `refunded`, dans les deux modes.

Lecture finale séparée : **0 utilisateur temporaire C14, 0 contenu/produit temporaire C14, 0 remboursement restant**, défaut `commande`. Seul le produit de profil conservé subsiste. Le `PRET` initial **existe et reste inchangé**, SHA-256 `e3aa30e17c31e87514b080cc766f5cd29c4fc3ad5c5dadb4e886c971f9ca447b`, relecture des corrections attendue. Aucun Git ni fichier hors périmètre modifié.
