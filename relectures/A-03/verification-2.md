# Vérification A-03 — tour complémentaire (après les trois compléments arbitrés)

Date : 2026-11-25. Vérificateur : Claude. Objet : contrôler les **compléments** appliqués par Hermès après `verification.md`, à la suite de `docs/arbitrages-2026-11-25.md` (§ A-03) et de `A-FAIRE.md` (consignes 1 et 2). Ce n'est pas une relecture complète.

État relu : `git diff 1d00798..HEAD` (dernier état « corrections » du 25/11 0 h 38 → HEAD `c7b66a6`) sur `wp/outils/bascule/a03/`, `wp/plugins/imagine-non-regression/`, `wp/tests/a03-non-regression/`, `wp/outils/bascule/non-regression.md`, `production/A-03/`. Diff ciblé, lecture du code et des tests ajoutés.

## 1. Application des consignes / arbitrages

**Arbitrage §A-03.1 — Hooks « attendus après mise à jour ». → Appliqué.**
- Liste **courte et justifiée** : un seul hook, `woocommerce_run_on_woocommerce_admin_updated`, en constante, commentaire « no migration, renewal, maintenance … exception ». `imagine-non-regression/src/Report.php:11`.
- Qualification conditionnée au changement de version Woo et au hook exact, sinon tout le reste reste **anormal** : `Report.php:13-30` (`expectedActionChange`), appelé `:224-226`, classe `attendu` `:227`. Conforme à « tout le reste demeure anormal ».
- « attendu seul = code 3, jamais 0 » : vérifié par le test `testOnlyObservedAdminHookAndItsCounterAreExpectedAfterWooUpdate` (présent au JUnit, cf. §2).

**Arbitrage §A-03.2 — Journal d'erreurs PHP (contrôle complémentaire). → Appliqué.**
- Nouveau lecteur `imagine-non-regression/src/PhpLog.php` : lecture d'un **vrai** fichier journal natif UTC, bornée par deux horodatages inclusifs encadrant les GET (`during()`), refus si rotation/troncature/lien/format inconnu/> 16 Mio/fenêtre > 24 h (`A03_PHP_LOG_READ`, `A03_PHP_LOG_FORMAT`, `A03_PHP_LOG_WINDOW`). Aucun message ni chemin exporté : le bilan n'émet que `{checked, from_utc, until_utc, errors}`.
- Branchement : `php_error_log` devient **obligatoire** (`Site.php:299`, `A03_PHP_LOG_CONFIG`), collecte enveloppée par `PhpLog::during` `:301`, champ `php_log` au rapport `:313`.
- Validation à la relecture : `Report.php:105-115` (forme, `checked===true`, `errors>=0`, horodatages, fenêtre ≤ 86 400 s). Horodatages ignorés dans le diff `:207`.
- Diagnostic PHP silencieux à affichage coupé / HTTP 200 **et compteur inchangé** = anormal : `Report.php:238-242`. Correspond à « avertissement natif silencieux avec HTTP 200 détecté ».

**Arbitrage §A-03.5 — Échec de collecte bloquant, pas de rapport partiel. → Appliqué.**
- HTTP : handle/corps en échec, corps > 4 Mio, délai dépassé, `Content-Length` invalide ou incohérent, statut 0, longueur ≠ `Content-Length` → `A03_HTTP_READ`. `Site.php:400,411,414,423`.
- Redirection hors site : auparavant `break` silencieux, désormais `A03_HTTP_REDIRECT`. `Site.php:432`.
- Échecs SQL déjà bloquants (acquis du tour C4, inchangé).
- Preuve bout en bout : `inside.py` (cas `http-unavailable`, `short`, `large`, `redirect`, journal `missing`/`not-configured`/`format`/`unreadable`) vérifie code 1, `stderr` du bon code, **aucun fichier de sortie** produit.

**Arbitrage §A-03.3 — Étanchéité du paywall hors A-03. → Appliqué (déjà au tour précédent).**
- Reversé à C-08/C-11, documenté `non-regression.md:8`. Aucun changement de code requis ce tour.

**Arbitrage §A-03.4 — Retrait des archives de preuves. → Appliqué (déjà au tour précédent), reconfirmé.**
- `production/A-03/` ne contient que `PRET`, `notes.md`, `sources.md` et le JSON de vérification des compléments. Aucune archive de preuves. Sorties dans le scratch hors dépôt.

**A-FAIRE consigne 1 — relancer `preparer-image.ps1` puis `rejouer.ps1`. → Fait.**
- Image reconstruite (artefact Hermès `prepare_image: 0`) et surtout : **j'ai rejoué moi-même** `rejouer.ps1` ce tour (cf. §2), au vert. L'autorisation permanente de `arbitrages-2026-11-25.md` §A-01 (Hermès relance `preparer-image.ps1` quand un lot ajoute un paquet) est respectée.

## 2. Résultat des tests

**Rejeu indépendant réalisé ce tour — limite du premier tour levée.**

Commande, exactement : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`.

- Refusée par l'outil PowerShell direct (« nested PowerShell process »), **exécutée via l'outil Bash**, même commande mot pour mot.
- Dernière ligne : `REJEU : 1012 tests, 34006 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`.
- Conteneur jetable, `network=none`, dépôt monté en lecture seule, nettoyage vérifié.

Point important : **le cœur pur d'A-03 est désormais dans le banc autorisé.** La réserve de portée de `relectures/A-03/CLAUDE.md` (point « important » n°1) est levée : le paquet `imagine-non-regression` est découvert par T01 et compte `OK (152 tests, 314 assertions)` dans ce rejeu, dont les compléments (`UpdateHooksTest`, `PhpLogTest`, `LogReportTest`, cas `Silent…`, `MissingLog…`, `Rotation…`). Ces nombres concordent avec les artefacts d'Hermès (`verification-complements-20261125.json` : 152/314).

Ce qui reste hors du banc autorisé : le bout en bout Docker/WSL d'`inside.py` (serveur HTTP fictif, journaux, rollback natif), que je n'ai pas relancé moi-même — je m'appuie pour ces cas sur les artefacts d'Hermès (87/87 contrôles). Mais les comportements corrigés sont tous exercés en logique pure sous `rejouer.ps1`, désormais vérifiés par moi.

## 3. Régressions et modifications non demandées

- **Aucune régression métier.** Aucun droit d'accès, état, décision de renouvellement n'a changé (diff limité aux ajouts `php_log`, hooks attendus, gardes HTTP). Les classements existants restent (versions = attendu ; droits/états/actions = anormal ; HTTP sain = à regarder).
- **Nouveau fichier de banc `wp/tests/a03-non-regression/http-rollback.php`** (drop-in de fixture, `cli-server` seulement, écritures natives en rollback, jamais déployé). Justifié : le bootstrap web natif écrit des transients et le compte SELECT du sujet provoquerait une erreur SQL. Non dans le chemin de production. À signaler : **c'est une dépendance pour A-04** — `verification-complements-20261125.json` (`parent_a04_handoff`) demande à A-04 de copier `http-rollback.php` et d'activer `log_errors/date.timezone/error_log` dans son serveur HTTP de banc avant son rejeu. Dépendance inter-lots, pas un défaut d'A-03.
- **`seed.php:76`** : `update_option('current_theme_supports_woocommerce','no')` pour stabiliser l'`AUTO_INCREMENT` sous le HTTP rollback-only. Fixture uniquement.
- **Redirection hors site = refus** (`Site.php:432`) : changement de comportement **voulu** par l'arbitrage §A-03.5, pas une régression.
- **Prérequis opérateur** (à garder en tête, non bloquant pour le code) : le contrôle du journal suppose un serveur configuré `log_errors=On`, `date.timezone=UTC` ; A-03 ne configure pas le serveur et ne prouve pas qu'un fichier vide est le bon journal. Documenté `non-regression.md:3` et dans le JSON (`limits_and_decisions`).
- **Détail** : la liste d'un seul hook attendu est un **défaut technique prudent** (arbitrage : « technique » → Hermès applique, Claude arbitre après coup). Je le confirme : il colle au seul hook observé au banc A-04 classique/HPOS et n'ouvre aucune exception pour migrations ou paiements. Renversable plus tard sans risque si A-04 en observe d'autres.

## 4. Verdict

**Prêt pour la clôture.**

Les trois compléments arbitrés (hooks attendus, journal PHP, collecte bloquante) sont appliqués, cités et testés ; les deux autres points de l'arbitrage (étanchéité hors A-03, retrait des preuves) sont tenus. La suite autorisée est au vert **rejouée par moi** (`1012 tests, 34006 assertions, 0 échec`), et le cœur pur d'A-03 — y compris les compléments — est maintenant couvert par ce banc, ce qui lève la seule réserve « importante » du premier tour. Aucune régression A-03, aucune modification non demandée touchant au métier ; la seule modification de support (`http-rollback.php`) est un drop-in de fixture justifié et porte une dépendance à reporter dans A-04.

Ce verdict n'est pas un GO réel. Il n'ouvre ni staging, ni compte, ni déploiement (doctrine §3). La clôture du lot de code relève de Claude (doctrine §6) ; aucune question ouverte ne reste pour Ced dans A-03 — les questions de `corrections/A-03.md` §5 ont été tranchées comme défauts techniques/métier par `docs/arbitrages-2026-11-25.md`.
