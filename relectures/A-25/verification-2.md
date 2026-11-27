# Vérification A-25 — 3e tour (après modifications d'Hermès du 27/11)

Date : 2026-11-27. Vérificateur. Base comparée : dernière vérification (`relectures/A-25/verification.md`, commit `5085e0e7` du 26/11 23:43) → HEAD. `git diff` sur `wp/outils/bascule/a25`, `wp/tests/a25` et `production/A-25`. Ce n'est pas une relecture complète : je contrôle l'application des consignes de requalification, les tests et l'absence de régression.

Consignes et arbitrages justifiant les modifications : `A-FAIRE.md` consigne 1 (« A-23, A-24, A-25 : code inchangé, clôture sur le paquet refait ; A-25 : en-tête du mode d'emploi à jour »), T-03 (déclaration `rejeu.json` ajoutée lot par lot pendant la requalification), et `docs/arbitrages-2026-11-27.md` (passage de 1 h « A-23, A-24, A-25 — clôture sur le paquet refait » ; passage de 4 h « A-25 : son banc attend maintenant le refus du `garder` et la purge »).

## 1. Consignes / arbitrages concernés

### C1 — Banc adapté à A-28 : il attend la purge et refuse le `garder` (arbitrage 27/11, 4 h) : **Appliquée**
- Le `garder` sur la table connue est retiré de la fixture nominale : `wp/tests/a25/neutralise.php:13` (plus de `'wp_fluentform_submissions' => ['action' => 'garder']`). La sortie mesure désormais la purge : `neutralise.php:49` (`known_messages_before`/`known_messages_after` au lieu de l'ancien `known_message_preserved`).
- Nouveau témoin ROUGE natif : `wp/tests/a25/neutralise-keep-red.php` (nouveau) rejoue l'ancien `garder` connu contre l'import A-28 courant et attend le refus fermé `FormDecisionRefused`/`A25_OLD_KEEP_REFUSED`, `exit=1` (`neutralise-keep-red.php:22-26`).
- Câblage de bout en bout : `wp/tests/a25/inside.py:259-263` (`actual_old_keep_refused_red` + base inchangée après refus `old_keep_refusal_database_unchanged`) ; `inside.py:271-278` sépare `actual_import_comments_anonymised`, `actual_import_known_forms_purged` (2 → 0) et `actual_import_unknown_forms_kept_separately` (inconnues conservées à part).
- Imposé par le vérificateur : `wp/tests/a25/verify.py:75-82` (`import_purge_valid`, valeurs fermées), contrôles obligatoires ajoutés `verify.py:101-103` et contrôles de paquet `verify.py:151-154` (`actual_purge_provenance`, `genuine_old_keep_red`).
- Contrat de mutation : `wp/tests/a25/test_import_purge.py` (nouveau) rend rouge la survie du message connu, le témoin positif absent (`known_messages_before=0`), l'effacement d'une table inconnue, et exige le témoin keep-red natif ainsi que l'absence de `garder` connu dans la fixture.

### C2 — En-tête du mode d'emploi à jour (A-FAIRE consigne 1 ; arbitrage 27/11, 1 h) : **Appliquée**
- `wp/outils/bascule/a25/README.md:3` remplace l'ancienne note « Corrections du 26 novembre… Python seul rejoué ici… pas de `PRET` » par « Requalification du 27 novembre 2026 après A-28… » (paquet unique `preuves/final/`, purge obligatoire, refus du `garder`, conservation séparée des inconnues, code inchangé). Ceci lève le « Nit de traçabilité » signalé en §3 de la 1re vérification.

### C3 — Code de l'outil inchangé (arbitrage 27/11 : « le code de l'outil ne change pas ») : **Appliquée (confirmée)**
- `git diff --stat 5085e0e7..HEAD` sur `wp/outils/bascule/a25` : seul `README.md` change (2 lignes). Aucune modification de `Inventory.php`, `Analysis.php`, `report.py`, `confine.py`, `Command.php`. La correction de fond I-1 vérifiée au 2e tour est donc intacte.

### C4 — Paquet refait avec déclaration `rejeu.json` (T-03 / requalification) : **Appliquée**
- `production/A-25/rejeu.json` (nouveau) : `entrypoint verify.py`, `requires []`, 14 logs liés, 150 contrôles fermés dont les nouveaux `*:actual_purge_provenance` et `*:genuine_old_keep_red` (classique/HPOS × UTF-8/cp1252).
- Paquet unique `production/A-25/preuves/final/` ; l'ancien reçu `candidate-verification.json` est supprimé (modèle « un seul paquet par lot »), pas rescellé. `PRET` et `FINALISATION.md` posés à 05:03, matrice neuve sur l'import A-28 gelé.

## 2. Résultat des tests

Commande exacte lancée (acceptée) :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Conteneur jetable, réseau coupé, dépôt monté en lecture seule (`mount=…/wp:/repo/wp:ro ; network=none ; cap-drop=ALL ; no-new-privileges`). Dernière ligne :

```
REJEU : 1153 tests, 36075 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

- Outil A-25 dans la matrice : `T01 TOOL : a25 ; 25 controls ; 0 failures ; exit=0` (15 → 25 contrôles : le banc enrichi est pris en compte, dont les tests purs de purge/keep-red).
- **Paquet A-25 vérifié par le rejeu indépendant** : `PAQUETS : 9 vérifiés, 0 échecs` ; la liste inclut A-25. Le vérificateur de paquet (`rejeu.json` → `verify.py`) rejoue donc la matrice native scellée d'A-25 et la trouve verte, nouveaux contrôles de purge compris. C'est la réserve de forme du 2e tour (« pas pu relancer la suite ») levée côté paquet.
- `OUTILS : 22 outils, 582 contrôles, 0 échecs ; hors rejeu : aucun`.

Réserve : `rejouer.ps1` rejoue le côté PHP et les vérificateurs de paquet. La matrice native Python (`matrix.py`, Windows UTF-8/cp1252) reste la preuve d'Hermès, non re-générée ici ; mais son paquet scellé est re-vérifié par le rejeu ci-dessus.

## 3. Régressions ou modifications non demandées

- **Aucune.** Le code de l'outil est inchangé (C3). Les seuls fichiers touchés sont le banc de tests (`wp/tests/a25`), le README (en-tête), et le paquet de production — tous attendus par la requalification.
- La bascule de l'assertion nominale de `neutralise.php` (`known_message_preserved` → `known_messages_before/after` 2→0) est **légitime et non régressive** : elle traduit exactement la purge imposée par A-28, et la conservation des tables inconnues/PK/filles est toujours prouvée séparément.
- Suppression de `production/A-25/candidate-verification.json` : intentionnelle (modèle « un seul paquet par lot »), remplacée par `preuves/final/` + `rejeu.json`. Pas une régression.
- Aucune restructuration d'un fichier commun ; aucune fonction nouvelle glissée en correction. L'import (`wp/outils/staging/`) et le gardien ne sont pas touchés.

## 4. Verdict

**Prêt pour la clôture.**

Les quatre consignes de requalification sont appliquées, vérifiées au fichier et à la ligne : banc adapté à A-28 (purge connue 2→0, refus natif du `garder`, inconnues conservées à part), en-tête du mode d'emploi à jour, code de l'outil inchangé, paquet refait avec `rejeu.json`. La suite PHP est entièrement verte (1153 tests, 0 échec) et le paquet A-25 est re-vérifié vert par le rejeu indépendant (9 paquets, 0 échec), nouveaux contrôles de purge inclus. Aucune régression, aucune modification non demandée ; aucun problème de fond restant ; aucune question visuelle, métier ou touchant au réel.

Rappels, non bloquants : A-22 reste non clos (hors périmètre de ce lot) ; la matrice native Python n'est pas re-générée dans cette session (preuve retenue : le rejeu indépendant du paquet scellé). La pose du `PRET` et le GO de clôture relèvent de Ced / du parent — un verdict de vérification n'est pas un GO (doctrine §6).
